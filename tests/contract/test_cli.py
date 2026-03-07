import json

from routeforge.cli import main
from routeforge.labs.manifest import LABS


def test_labs_command_runs() -> None:
    assert main(["labs"]) == 0


def test_show_command_includes_conformance(capsys) -> None:
    assert main(["show", "lab01_frame_and_headers"]) == 0
    output = capsys.readouterr().out
    assert "id: lab01_frame_and_headers" in output
    assert "conformance.must: L2_FRAME_VALIDATION" in output


def test_run_command_blocks_unmet_prereqs(capsys) -> None:
    assert main(["run", "lab02_mac_learning_switch"]) == 2
    output = capsys.readouterr().out
    assert "unmet prerequisites: lab01_frame_and_headers" in output


def test_run_command_allows_completed_prereq() -> None:
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


def test_run_lab06_allows_when_prereqs_met() -> None:
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


def test_run_lab27_allows_when_prereqs_met() -> None:
    prereqs = [entry["id"] for entry in LABS if entry["id"] != "lab27_capstone_incident_drill"]
    argv = ["run", "lab27_capstone_incident_drill"]
    for prereq in prereqs:
        argv.extend(["--completed", prereq])
    assert main(argv) == 0


def test_run_student_mode_unavailable_for_lab02(capsys) -> None:
    assert main(["run", "lab02_mac_learning_switch", "--student", "--completed", "lab01_frame_and_headers"]) == 3
    output = capsys.readouterr().out
    assert "student coding checks not available yet" in output


def test_run_student_mode_lab01_surfaces_not_implemented(capsys) -> None:
    assert main(["run", "lab01_frame_and_headers", "--student"]) == 4
    output = capsys.readouterr().out.lower()
    assert "not implemented: validate_mac" in output
    assert "edit src/routeforge/student/lab01.py" in output


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


def test_progress_show_mark_reset_and_report(tmp_path, capsys) -> None:
    state = tmp_path / "progress.json"

    assert main(["progress", "show", "--state-file", str(state)]) == 0
    output = capsys.readouterr().out
    assert "labs.completed: 0/27" in output
    assert "labs.unlocked: lab01_frame_and_headers" in output

    assert main(["progress", "mark", "lab01_frame_and_headers", "--state-file", str(state)]) == 0
    mark_out = capsys.readouterr().out
    assert "marked complete: lab01_frame_and_headers" in mark_out

    assert main(["report", "--state-file", str(state)]) == 0
    report_out = capsys.readouterr().out
    assert "labs.completed: 1/27" in report_out
    assert "assessment.score:" in report_out
    assert "assessment.band:" in report_out
    assert "assessment.remediation_docs:" in report_out
    assert "capstone.ready: no" in report_out

    assert main(["progress", "reset", "--state-file", str(state)]) == 0
    reset_out = capsys.readouterr().out
    assert "progress reset:" in reset_out


def test_run_with_state_file_updates_progress(tmp_path, capsys) -> None:
    state = tmp_path / "progress.json"
    assert main(["run", "lab01_frame_and_headers", "--state-file", str(state)]) == 0
    run_out = capsys.readouterr().out
    assert "progress updated:" in run_out

    assert main(["progress", "show", "--state-file", str(state)]) == 0
    show_out = capsys.readouterr().out
    assert "labs.completed: 1/27" in show_out


def test_run_uses_saved_progress_for_prereqs(tmp_path, capsys) -> None:
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
    assert main(["progress", "mark", "lab01_frame_and_headers", "--state-file", str(state)]) == 0
    capsys.readouterr()

    assert main(["report", "--state-file", str(state), "--json-out", str(report)]) == 0
    out = capsys.readouterr().out
    assert "report written:" in out

    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["labs"]["completed"] == 1
    assert payload["labs"]["unlocked_ids"] == ["lab02_mac_learning_switch"]
    assert payload["assessment"]["overall_score"] == 3.0
    assert payload["assessment"]["band"] == "BELOW_PASS"
    assert payload["assessment"]["remediation_docs"] == []
    assert payload["capstone_ready"] is False
