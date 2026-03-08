from __future__ import annotations

from routeforge.cli import main
from routeforge.labs.contracts import FeatureOutcome, LabStepResult, build_result


def _passing_lab_result(lab_id: str, *, step_name: str) -> object:
    return build_result(
        lab_id,
        [
            LabStepResult(
                name=step_name,
                passed=True,
                detail="stubbed lab result for learner journey smoke coverage",
                outcome=FeatureOutcome(
                    action="PASS",
                    reason="stubbed lab result for learner journey smoke coverage",
                    checkpoints=("CLI_TEST_PASS",),
                    details={},
                ),
            )
        ],
    )


def test_student_journey_smoke_progresses_across_early_labs(monkeypatch, tmp_path, capsys) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        "routeforge.cli.run_lab",
        lambda lab_id: _passing_lab_result(lab_id, step_name="unknown_unicast_flood")
        if lab_id == "lab02_mac_learning_switch"
        else _passing_lab_result(lab_id, step_name="valid_frame_parses"),
    )
    state = tmp_path / "journey-progress.json"

    assert main(["show", "lab01_frame_and_headers"]) == 0
    show_out = capsys.readouterr().out
    assert "student.target: src/routeforge/model/packet.py" in show_out

    assert main(["check", "lab01"]) == 0
    capsys.readouterr()

    assert main(["run", "lab01_frame_and_headers", "--state-file", str(state)]) == 0
    capsys.readouterr()
    assert main(["run", "lab02_mac_learning_switch", "--state-file", str(state)]) == 0
    capsys.readouterr()

    assert main(["progress", "show", "--state-file", str(state)]) == 0
    progress_out = capsys.readouterr().out
    assert "labs.completed: 2/" in progress_out
    assert "lab03_vlan_and_trunks" in progress_out


def test_student_journey_smoke_blocks_unmet_prereqs(tmp_path, capsys) -> None:
    state = tmp_path / "journey-blocked.json"

    assert main(["run", "lab03_vlan_and_trunks", "--state-file", str(state)]) == 2
    output = capsys.readouterr().out
    assert "blocked:" in output
    assert "lab01_frame_and_headers" in output
