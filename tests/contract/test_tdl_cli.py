from __future__ import annotations

from routeforge.cli import main
from routeforge.tdl.manifest import TDL_CHALLENGES


def test_tdl_list_and_show_commands(capsys) -> None:
    assert main(["tdl", "list"]) == 0
    list_output = capsys.readouterr().out
    assert "tdl_auto_01_yang_path_validation" in list_output
    assert "status=UNLOCKED" in list_output

    assert main(["tdl", "show", "tdl_mcast_01_rpf_check"]) == 0
    show_output = capsys.readouterr().out
    assert "id: tdl_mcast_01_rpf_check" in show_output
    assert "tdl.target: src/routeforge/runtime/tdl.py" in show_output
    assert "conformance.overlap:" in show_output


def test_tdl_run_blocks_unmet_prereqs(capsys, tmp_path) -> None:
    state = tmp_path / "tdl-progress.json"
    assert main(["tdl", "run", "tdl_auto_02_netconf_edit_merge_replace", "--state-file", str(state)]) == 2
    output = capsys.readouterr().out
    assert "unmet prerequisites: tdl_auto_01_yang_path_validation" in output


def test_tdl_run_updates_progress_and_xp(capsys, tmp_path) -> None:
    state = tmp_path / "tdl-progress.json"
    assert main(["tdl", "run", "tdl_auto_01_yang_path_validation", "--state-file", str(state)]) == 0
    run_output = capsys.readouterr().out
    assert "tdl progress updated:" in run_output

    assert main(["tdl", "progress", "show", "--state-file", str(state)]) == 0
    show_output = capsys.readouterr().out
    assert f"tdl.completed: 1/{len(TDL_CHALLENGES)}" in show_output
    assert "tdl.xp: 100" in show_output


def test_tdl_check_command_rejects_unknown_target(capsys) -> None:
    assert main(["tdl", "check", "nope"]) == 1
    output = capsys.readouterr().out
    assert "unknown tdl check target" in output


def test_tdl_check_command_calls_runner(monkeypatch, capsys) -> None:
    captured: dict[str, object] = {}

    def _fake_run_tdl_checks(*, target: str, repo_root):  # type: ignore[no-untyped-def]
        captured["target"] = target
        captured["repo_root"] = repo_root
        return 0

    monkeypatch.setattr("routeforge.cli.run_tdl_checks", _fake_run_tdl_checks)
    assert main(["tdl", "check", "tdl_wlan_04_wmm_queue_mapping"]) == 0
    output = capsys.readouterr().out
    assert "running tdl checks: target=tdl_wlan_04_wmm_queue_mapping" in output
    assert captured["target"] == "tdl_wlan_04_wmm_queue_mapping"


def test_tdl_run_handles_unimplemented_challenge(monkeypatch, capsys, tmp_path) -> None:
    def _fake_run_tdl_challenge(challenge_id: str):  # type: ignore[no-untyped-def]
        raise NotImplementedError("TODO: implement validate_yang_path")

    monkeypatch.setattr("routeforge.cli.run_tdl_challenge", _fake_run_tdl_challenge)
    state = tmp_path / "tdl-progress.json"
    assert main(["tdl", "run", "tdl_auto_01_yang_path_validation", "--state-file", str(state)]) == 4
    output = capsys.readouterr().out
    assert "challenge implementation missing:" in output
