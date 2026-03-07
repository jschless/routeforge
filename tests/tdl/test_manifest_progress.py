from __future__ import annotations

from routeforge.tdl.exercises import TDL_RUNNERS
from routeforge.tdl.manifest import TDL_CHALLENGES, get_tdl_challenge, tdl_missing_prereqs
from routeforge.tdl.progress import (
    apply_tdl_run_result,
    clear_tdl_progress,
    load_tdl_progress,
    save_tdl_progress,
    unlocked_tdl_challenges,
)
import pytest


def test_manifest_ids_are_unique_and_prereqs_exist() -> None:
    challenge_ids = [entry["id"] for entry in TDL_CHALLENGES]
    assert len(challenge_ids) == len(set(challenge_ids))

    all_ids = set(challenge_ids)
    for entry in TDL_CHALLENGES:
        assert entry["xp"] > 0
        assert entry["symbols"]
        assert entry["summary"]
        for prereq in entry["prereqs"]:
            assert prereq in all_ids


def test_runner_registry_matches_manifest() -> None:
    manifest_ids = {entry["id"] for entry in TDL_CHALLENGES}
    runner_ids = set(TDL_RUNNERS)
    assert runner_ids == manifest_ids


def test_tdl_missing_prereqs_reports_only_unsatisfied() -> None:
    entry = get_tdl_challenge("tdl_auto_02_netconf_edit_merge_replace")
    assert entry is not None
    assert tdl_missing_prereqs(entry["id"], set()) == ["tdl_auto_01_yang_path_validation"]
    assert tdl_missing_prereqs(entry["id"], {"tdl_auto_01_yang_path_validation"}) == []


def test_tdl_progress_round_trip_and_unlocks(tmp_path) -> None:
    progress_path = tmp_path / "tdl-progress.json"
    state = clear_tdl_progress()
    assert unlocked_tdl_challenges(state) == (
        "tdl_auto_01_yang_path_validation",
        "tdl_mcast_01_rpf_check",
        "tdl_wlan_01_client_join_state_machine",
    )

    state = apply_tdl_run_result(
        state,
        challenge_id="tdl_auto_01_yang_path_validation",
        passed=True,
    )
    assert state.completed == ("tdl_auto_01_yang_path_validation",)
    assert state.total_xp == 100
    assert state.run_counts["tdl_auto_01_yang_path_validation"] == 1
    assert state.pass_counts["tdl_auto_01_yang_path_validation"] == 1
    assert state.last_result["tdl_auto_01_yang_path_validation"] == "PASS"
    assert "tdl_auto_02_netconf_edit_merge_replace" in unlocked_tdl_challenges(state)

    state = apply_tdl_run_result(
        state,
        challenge_id="tdl_auto_02_netconf_edit_merge_replace",
        passed=False,
    )
    assert "tdl_auto_02_netconf_edit_merge_replace" not in state.completed
    assert state.run_counts["tdl_auto_02_netconf_edit_merge_replace"] == 1
    assert "tdl_auto_02_netconf_edit_merge_replace" not in state.pass_counts
    assert state.last_result["tdl_auto_02_netconf_edit_merge_replace"] == "FAIL"

    save_tdl_progress(state, progress_path)
    loaded = load_tdl_progress(progress_path)
    assert loaded == state


def test_tdl_badges_and_master_completion() -> None:
    state = clear_tdl_progress()
    for entry in TDL_CHALLENGES:
        state = apply_tdl_run_result(state, challenge_id=entry["id"], passed=True)

    assert state.total_xp == sum(entry["xp"] for entry in TDL_CHALLENGES)
    assert "automation_complete" in state.badges
    assert "multicast_complete" in state.badges
    assert "wireless_complete" in state.badges
    assert "tdl_master" in state.badges


def test_apply_tdl_run_result_rejects_unknown_challenge() -> None:
    with pytest.raises(KeyError, match="unknown tdl challenge"):
        apply_tdl_run_result(clear_tdl_progress(), challenge_id="tdl_unknown", passed=True)
