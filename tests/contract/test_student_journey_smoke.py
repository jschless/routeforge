from __future__ import annotations

from routeforge.cli import main


def test_student_journey_smoke_progresses_across_early_labs(tmp_path, capsys) -> None:
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
