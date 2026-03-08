import json
from pathlib import Path
import subprocess

import pytest

from routeforge.cli import main
from routeforge.labs.assessment import load_assessment_rubric
from routeforge.labs.contracts import FeatureOutcome, LabStepResult, build_result
from routeforge.labs.manifest import LABS
from routeforge.labs.progress import ProgressState, save_progress
from routeforge.labs.student_checks import StudentCheckFailure, StudentCheckRun


def _passing_lab_result(lab_id: str, *, step_name: str = "stubbed_step"):
    return build_result(
        lab_id,
        [
            LabStepResult(
                name=step_name,
                passed=True,
                detail="stubbed lab result for CLI contract testing",
                outcome=FeatureOutcome(
                    action="PASS",
                    reason="stubbed lab result for CLI contract testing",
                    checkpoints=("CLI_TEST_PASS",),
                    details={},
                ),
            )
        ],
    )


def test_labs_command_runs() -> None:
    assert main(["labs"]) == 0


def test_show_command_includes_conformance(capsys) -> None:
    assert main(["show", "lab01_frame_and_headers"]) == 0
    output = capsys.readouterr().out
    assert "id: lab01_frame_and_headers" in output
    assert "conformance.must: L2_FRAME_VALIDATION" in output
    assert "student.stage: 1" in output
    assert "student.target: src/routeforge/model/packet.py" in output
    assert "student.signatures:" in output


def test_show_command_includes_prereq_reason_when_present(capsys) -> None:
    assert main(["show", "lab02_mac_learning_switch"]) == 0
    output = capsys.readouterr().out
    assert "student.prereq_reason:" in output
    assert "Requires lab01_frame_and_headers" in output


def test_run_command_blocks_unmet_prereqs(capsys) -> None:
    assert main(["run", "lab02_mac_learning_switch"]) == 2
    output = capsys.readouterr().out
    assert "unmet prerequisites: lab01_frame_and_headers" in output


def test_run_command_allows_completed_prereq(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "routeforge.cli.run_lab",
        lambda lab_id: _passing_lab_result(lab_id, step_name="unknown_unicast_flood"),
    )
    assert (
        main(
            [
                "run",
                "lab02_mac_learning_switch",
                "--completed",
                "lab01_frame_and_headers",
            ]
        )
        == 0
    )


def test_run_command_checks_transitive_prereqs(capsys) -> None:
    assert (
        main(
            [
                "run",
                "lab03_vlan_and_trunks",
                "--completed",
                "lab02_mac_learning_switch",
            ]
        )
        == 2
    )
    output = capsys.readouterr().out
    assert "lab01_frame_and_headers" in output


def test_run_lab05_blocks_missing_earlier_labs(capsys) -> None:
    assert main(["run", "lab05_stp_convergence_and_protection", "--completed", "lab04_stp"]) == 2
    output = capsys.readouterr().out
    assert "lab01_frame_and_headers" in output
    assert "lab03_vlan_and_trunks" in output


def test_run_lab06_allows_when_prereqs_met(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "routeforge.cli.run_lab",
        lambda lab_id: _passing_lab_result(lab_id, step_name="arp_resolution"),
    )
    assert (
        main(
            [
                "run",
                "lab06_arp_and_adjacency",
                "--completed",
                "lab01_frame_and_headers",
                "--completed",
                "lab02_mac_learning_switch",
                "--completed",
                "lab03_vlan_and_trunks",
                "--completed",
                "lab04_stp",
                "--completed",
                "lab05_stp_convergence_and_protection",
            ]
        )
        == 0
    )


def test_run_lab10_blocks_missing_chain(capsys) -> None:
    assert main(["run", "lab10_ipv4_control_plane_diagnostics", "--completed", "lab09_icmp_and_control_responses"]) == 2
    output = capsys.readouterr().out
    assert "lab08_fib_forwarding_pipeline" in output
    assert "lab01_frame_and_headers" in output


def test_run_lab15_blocks_missing_chain(capsys) -> None:
    assert main(["run", "lab15_ospf_multi_area_abr", "--completed", "lab14_ospf_spf_and_route_install"]) == 2
    output = capsys.readouterr().out
    assert "lab10_ipv4_control_plane_diagnostics" in output
    assert "lab01_frame_and_headers" in output


def test_run_lab20_blocks_missing_chain(capsys) -> None:
    assert main(["run", "lab20_qos_marking_and_queueing", "--completed", "lab19_nat44_stateful_translation"]) == 2
    output = capsys.readouterr().out
    assert "lab15_ospf_multi_area_abr" in output
    assert "lab01_frame_and_headers" in output


def test_run_lab27_blocks_missing_chain(capsys) -> None:
    assert main(["run", "lab27_capstone_incident_drill", "--completed", "lab26_observability_and_ops"]) == 2
    output = capsys.readouterr().out
    assert "lab21_bgp_session_fsm_and_transport" in output
    assert "lab01_frame_and_headers" in output


def test_run_lab27_allows_when_prereqs_met(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "routeforge.cli.run_lab",
        lambda lab_id: _passing_lab_result(lab_id, step_name="incident_resolved"),
    )
    prereqs = [entry["id"] for entry in LABS if entry["id"] != "lab27_capstone_incident_drill"]
    argv = ["run", "lab27_capstone_incident_drill"]
    for prereq in prereqs:
        argv.extend(["--completed", prereq])
    assert main(argv) == 0


def test_check_command_rejects_unknown_target(capsys) -> None:
    assert main(["check", "nope"]) == 1
    output = capsys.readouterr().out
    assert "unknown check target" in output


def test_check_command_uses_stage_limit(monkeypatch, capsys) -> None:
    captured: dict[str, object] = {}

    def _fake_run_staged_student_checks(*, stage_max: int, repo_root):  # type: ignore[no-untyped-def]
        captured["stage_max"] = stage_max
        captured["repo_root"] = repo_root
        return StudentCheckRun(
            returncode=0,
            passed=1,
            total=1,
            failures=(),
            raw_output="1 passed in 0.01s",
        )

    monkeypatch.setattr("routeforge.cli.run_staged_student_checks", _fake_run_staged_student_checks)
    assert main(["check", "lab01"]) == 0
    output = capsys.readouterr().out
    assert "stage_max=1" in output
    assert "1 of 1 tests passed" in output
    assert captured["stage_max"] == 1


def test_check_command_formats_failures(monkeypatch, capsys) -> None:
    def _fake_run_staged_student_checks(*, stage_max: int, repo_root):  # type: ignore[no-untyped-def]
        return StudentCheckRun(
            returncode=1,
            passed=2,
            total=3,
            failures=(StudentCheckFailure("tests/student/test_stage_progression.py::test_lab03", "expected VLAN tag"),),
            raw_output="raw output",
        )

    monkeypatch.setattr("routeforge.cli.run_staged_student_checks", _fake_run_staged_student_checks)
    assert main(["check", "lab03"]) == 1
    output = capsys.readouterr().out
    assert "[FAIL] test_lab03: expected VLAN tag" in output
    assert "2 of 3 tests passed" in output


def test_check_command_verbose_prints_raw(monkeypatch, capsys) -> None:
    def _fake_run_staged_student_checks(*, stage_max: int, repo_root):  # type: ignore[no-untyped-def]
        return StudentCheckRun(
            returncode=1,
            passed=0,
            total=1,
            failures=(StudentCheckFailure("tests/student/test_stage_progression.py::test_lab01", "bad frame"),),
            raw_output="RAW PYTEST OUTPUT",
        )

    monkeypatch.setattr("routeforge.cli.run_staged_student_checks", _fake_run_staged_student_checks)
    assert main(["check", "lab01", "--verbose"]) == 1
    output = capsys.readouterr().out
    assert "RAW PYTEST OUTPUT" in output


def test_check_command_reports_startup_failure(monkeypatch, capsys) -> None:
    def _fake_run_staged_student_checks(*, stage_max: int, repo_root):  # type: ignore[no-untyped-def]
        return StudentCheckRun(
            returncode=1,
            passed=0,
            total=0,
            failures=(),
            raw_output="Traceback...\nModuleNotFoundError: No module named 'markupsafe'",
        )

    monkeypatch.setattr("routeforge.cli.run_staged_student_checks", _fake_run_staged_student_checks)
    assert main(["check", "lab01"]) == 1
    output = capsys.readouterr().out
    assert "[FAIL] pytest startup: ModuleNotFoundError: No module named 'markupsafe'" in output
    assert "staged checks failed before test collection" in output


def test_run_staged_student_checks_reads_junit_xml(monkeypatch) -> None:
    from routeforge.labs import student_checks

    captured: dict[str, object] = {}

    def _fake_run(command, cwd, check, capture_output, env, text):  # type: ignore[no-untyped-def]
        captured["env"] = env
        junit_path = Path(command[command.index("--junitxml") + 1])
        junit_path.write_text(
            """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
  <testsuite name="pytest" tests="3" failures="1" errors="0" skipped="0">
    <testcase classname="tests.student.test_stage_progression" name="test_stage01_edge_mac_and_ipv4_validation" />
    <testcase classname="tests.student.test_stage_progression" name="test_stage_lab[stage01_lab01_frame_and_headers]">
      <failure message="AssertionError: expected validation checkpoint" />
    </testcase>
    <testcase classname="tests.student.test_stage_progression" name="test_stage02_forwarding_plan_decisions" />
  </testsuite>
</testsuites>
""",
            encoding="utf-8",
        )
        return subprocess.CompletedProcess(command, 1, stdout="raw stdout", stderr="")

    monkeypatch.setattr(student_checks.subprocess, "run", _fake_run)
    result = student_checks.run_staged_student_checks(stage_max=1, repo_root=Path.cwd())

    assert result.returncode == 1
    assert result.passed == 2
    assert result.total == 3
    assert captured["env"]["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] == "1"
    assert result.failures == (
        StudentCheckFailure(
            "tests/student/test_stage_progression.py::test_stage_lab[stage01_lab01_frame_and_headers]",
            "expected validation checkpoint",
        ),
    )


def test_run_command_writes_trace(tmp_path) -> None:
    trace = tmp_path / "trace.jsonl"
    code = main(
        [
            "run",
            "lab01_frame_and_headers",
            "--trace-out",
            str(trace),
        ]
    )
    assert code == 0
    lines = trace.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2


def test_run_without_state_file_updates_default_progress(capsys) -> None:
    total_labs = len(LABS)

    assert main(["run", "lab01_frame_and_headers"]) == 0
    run_out = capsys.readouterr().out
    assert "progress updated:" in run_out

    assert main(["progress", "show"]) == 0
    show_out = capsys.readouterr().out
    assert f"labs.completed: 1/{total_labs}" in show_out


def test_progress_show_uses_legacy_local_fallback_when_default_missing(tmp_path, capsys) -> None:
    legacy_state = ProgressState(
        version=1,
        completed=("lab01_frame_and_headers",),
        run_counts={"lab01_frame_and_headers": 1},
        pass_counts={"lab01_frame_and_headers": 1},
        last_result={"lab01_frame_and_headers": "PASS"},
    )
    save_progress(legacy_state, tmp_path / ".routeforge_progress.json")

    assert main(["progress", "show"]) == 0
    output = capsys.readouterr().out
    assert "warning: using legacy local progress file" in output
    assert f"progress.file: {tmp_path / '.routeforge_progress.json'}" in output
    assert "labs.completed: 1/" in output


def test_run_command_shows_todo_for_not_implemented(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    from routeforge.labs import exercises as labs_exercises

    def _raise_todo() -> None:
        raise NotImplementedError("not yet implemented")

    monkeypatch.setitem(labs_exercises.LAB_RUNNERS, "lab01_frame_and_headers", _raise_todo)
    assert main(["run", "lab01_frame_and_headers"]) == 4
    output = capsys.readouterr().out
    assert "[TODO] implementation_todo:" in output
    assert "routeforge hint lab01_frame_and_headers" in output
    assert "checkpoints fired:" not in output


def test_run_command_shows_contract_mismatch_for_type_errors(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    from routeforge.labs import exercises as labs_exercises

    def _raise_type_error() -> None:
        raise TypeError("wrong return object")

    monkeypatch.setitem(labs_exercises.LAB_RUNNERS, "lab01_frame_and_headers", _raise_type_error)
    assert main(["run", "lab01_frame_and_headers"]) == 4
    output = capsys.readouterr().out
    assert "[FAIL] implementation_contract_error:" in output
    assert "step failed with TypeError" in output
    assert "check your return type matches the function signature" in output


def test_debug_replay_and_explain(tmp_path, capsys) -> None:
    trace = tmp_path / "trace.jsonl"
    assert main(["run", "lab01_frame_and_headers", "--trace-out", str(trace)]) == 0

    assert main(["debug", "replay", "--trace", str(trace)]) == 0
    replay_out = capsys.readouterr().out
    assert "seq=1" in replay_out
    assert "valid_frame_parses" in replay_out

    assert main(["debug", "explain", "--trace", str(trace), "--step", "invalid_frame_drops"]) == 0
    explain_out = capsys.readouterr().out
    assert "action: DROP" in explain_out
    assert "checkpoints: PARSE_DROP" in explain_out


def test_debug_explain_checkpoint_filter_and_list(tmp_path, capsys) -> None:
    trace = tmp_path / "trace.jsonl"
    assert main(["run", "lab01_frame_and_headers", "--trace-out", str(trace)]) == 0
    capsys.readouterr()

    assert main(["debug", "explain", "--trace", str(trace), "--checkpoint", "PARSE_DROP"]) == 0
    filtered = capsys.readouterr().out
    assert "records: 1" in filtered
    assert "PARSE_DROP" in filtered

    assert main(["debug", "explain", "--trace", str(trace), "--list-checkpoints"]) == 0
    listed = capsys.readouterr().out
    assert "PARSE_OK" in listed
    assert "PARSE_DROP" in listed


def test_validate_targets_command_runs(capsys) -> None:
    assert main(["validate-targets"]) == 0
    output = capsys.readouterr().out
    assert "student targets:" in output


def test_progress_show_mark_reset_and_report(tmp_path, capsys) -> None:
    state = tmp_path / "progress.json"
    total_labs = len(LABS)

    assert main(["progress", "show", "--state-file", str(state)]) == 0
    output = capsys.readouterr().out
    assert f"labs.completed: 0/{total_labs}" in output
    assert "labs.unlocked: lab01_frame_and_headers" in output

    assert main(["progress", "mark", "lab01_frame_and_headers", "--state-file", str(state)]) == 0
    mark_out = capsys.readouterr().out
    assert "marked complete: lab01_frame_and_headers" in mark_out

    assert main(["report", "--state-file", str(state)]) == 0
    report_out = capsys.readouterr().out
    assert f"labs.completed: 1/{total_labs}" in report_out
    assert "assessment.score:" in report_out
    assert "assessment.band:" in report_out
    assert "assessment.recommended_labs:" in report_out
    assert "assessment.remediation_docs:" in report_out
    assert "capstone.ready: no" in report_out

    assert main(["progress", "reset", "--state-file", str(state)]) == 0
    reset_out = capsys.readouterr().out
    assert "progress reset:" in reset_out


def test_run_with_state_file_updates_progress(tmp_path, capsys) -> None:
    state = tmp_path / "progress.json"
    total_labs = len(LABS)
    assert main(["run", "lab01_frame_and_headers", "--state-file", str(state)]) == 0
    run_out = capsys.readouterr().out
    assert "progress updated:" in run_out

    assert main(["progress", "show", "--state-file", str(state)]) == 0
    show_out = capsys.readouterr().out
    assert f"labs.completed: 1/{total_labs}" in show_out


def test_run_preserves_legacy_progress_and_upgrades_on_save(monkeypatch, tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "routeforge.cli.run_lab",
        lambda lab_id: _passing_lab_result(lab_id, step_name="unknown_unicast_flood"),
    )
    state = tmp_path / "legacy-progress.json"
    state.write_text(
        json.dumps(
            {
                "completed": ["lab01_frame_and_headers"],
                "run_counts": {"lab01_frame_and_headers": 1},
                "pass_counts": {"lab01_frame_and_headers": 1},
                "last_result": {"lab01_frame_and_headers": "PASS"},
            }
        ),
        encoding="utf-8",
    )

    assert main(["run", "lab02_mac_learning_switch", "--state-file", str(state)]) == 0
    output = capsys.readouterr().out
    assert "loaded legacy state" in output
    payload = json.loads(state.read_text(encoding="utf-8"))
    assert payload["version"] == 1
    assert payload["completed"][:2] == ["lab01_frame_and_headers", "lab02_mac_learning_switch"]
    assert payload["run_counts"]["lab01_frame_and_headers"] == 1
    assert payload["run_counts"]["lab02_mac_learning_switch"] == 1


def test_run_uses_saved_progress_for_prereqs(monkeypatch, tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "routeforge.cli.run_lab",
        lambda lab_id: _passing_lab_result(lab_id, step_name="unknown_unicast_flood"),
    )
    state = tmp_path / "progress.json"
    assert main(["progress", "mark", "lab01_frame_and_headers", "--state-file", str(state)]) == 0
    capsys.readouterr()

    assert main(["run", "lab02_mac_learning_switch", "--state-file", str(state)]) == 0
    output = capsys.readouterr().out
    assert "[PASS] unknown_unicast_flood" in output
    assert "progress updated:" in output


def test_report_writes_json_output(tmp_path, capsys) -> None:
    state = tmp_path / "progress.json"
    report = tmp_path / "report.json"
    rubric = load_assessment_rubric()
    total_weight = sum(lab.weight for lab in rubric.labs.values())
    lab01_weight = rubric.labs["lab01_frame_and_headers"].weight

    assert main(["progress", "mark", "lab01_frame_and_headers", "--state-file", str(state)]) == 0
    capsys.readouterr()

    assert main(["report", "--state-file", str(state), "--json-out", str(report)]) == 0
    out = capsys.readouterr().out
    assert "report written:" in out

    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["labs"]["completed"] == 1
    assert payload["labs"]["unlocked_ids"] == ["lab02_mac_learning_switch"]
    expected_score = 100.0 * lab01_weight / total_weight
    assert payload["assessment"]["overall_score"] == pytest.approx(expected_score)
    assert payload["assessment"]["band"] == "BELOW_PASS"
    assert payload["assessment"]["recommended_labs"] == []
    assert payload["assessment"]["remediation_docs"] == []
    assert payload["capstone_ready"] is False


def test_status_command_outputs_position_and_next(tmp_path, capsys) -> None:
    state = tmp_path / "progress.json"
    assert main(["progress", "mark", "lab01_frame_and_headers", "--state-file", str(state)]) == 0
    capsys.readouterr()
    assert main(["status", "--state-file", str(state)]) == 0
    output = capsys.readouterr().out
    assert "position: lab01_frame_and_headers" in output
    assert "next: lab02_mac_learning_switch" in output
    assert "score:" in output


def test_hint_reports_real_test_files(capsys) -> None:
    assert main(["hint", "lab01_frame_and_headers"]) == 0
    output = capsys.readouterr().out
    assert "staged learner gate: tests/student/test_stage_progression.py" in output
    assert "tests/contract/test_packet_and_interface.py" in output
    assert "tests/contract/test_src/routeforge/model/packet.py" not in output


def test_hint_reports_phase2_shim_contract_tests(capsys) -> None:
    assert main(["hint", "lab28_dhcp_snooping_and_dai"]) == 0
    lab28_output = capsys.readouterr().out
    assert "tests/contract/test_phase2_runtime.py" in lab28_output

    assert main(["hint", "lab39_bgp_evpn_vxlan_basics"]) == 0
    lab39_output = capsys.readouterr().out
    assert "tests/contract/test_phase2_runtime.py" in lab39_output
