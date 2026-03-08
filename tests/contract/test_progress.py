from __future__ import annotations

import json

from routeforge.labs.progress import (
    ProgressState,
    apply_run_result,
    clear_progress,
    load_progress,
    migrate_progress,
    mark_completed,
    save_progress,
    unlocked_labs,
)


def test_load_missing_progress_returns_empty(tmp_path) -> None:
    state = load_progress(tmp_path / "missing.json")
    assert state.version == 1
    assert state.completed == ()
    assert state.run_counts == {}


def test_save_and_load_roundtrip(tmp_path) -> None:
    path = tmp_path / "progress.json"
    original = ProgressState(
        version=1,
        completed=("lab01_frame_and_headers",),
        run_counts={"lab01_frame_and_headers": 2},
        pass_counts={"lab01_frame_and_headers": 1},
        last_result={"lab01_frame_and_headers": "PASS"},
    )
    save_progress(original, path)
    loaded = load_progress(path)
    assert loaded == original


def test_apply_run_result_and_unlock_flow() -> None:
    state = clear_progress()
    state = apply_run_result(state, lab_id="lab01_frame_and_headers", passed=True)
    state = apply_run_result(state, lab_id="lab02_mac_learning_switch", passed=False)
    state = mark_completed(state, "lab02_mac_learning_switch")

    assert state.completed[:2] == ("lab01_frame_and_headers", "lab02_mac_learning_switch")
    assert state.run_counts["lab01_frame_and_headers"] == 1
    assert state.run_counts["lab02_mac_learning_switch"] == 1
    assert state.pass_counts["lab01_frame_and_headers"] == 1
    assert state.last_result["lab02_mac_learning_switch"] == "FAIL"
    assert unlocked_labs(state)[0] == "lab03_vlan_and_trunks"


def test_load_legacy_progress_without_version_preserves_state(tmp_path, capsys) -> None:
    path = tmp_path / "legacy.json"
    path.write_text(
        json.dumps(
            {
                "completed": ["lab01_frame_and_headers"],
                "run_counts": {"lab01_frame_and_headers": 2},
                "pass_counts": {"lab01_frame_and_headers": 1},
                "last_result": {"lab01_frame_and_headers": "PASS"},
            }
        ),
        encoding="utf-8",
    )
    state = load_progress(path)
    output = capsys.readouterr().out
    assert "loaded legacy state" in output
    assert state.version == 1
    assert state.completed == ("lab01_frame_and_headers",)
    assert state.run_counts == {"lab01_frame_and_headers": 2}
    assert state.pass_counts == {"lab01_frame_and_headers": 1}
    assert state.last_result == {"lab01_frame_and_headers": "PASS"}


def test_load_older_progress_version_preserves_state(tmp_path, capsys) -> None:
    path = tmp_path / "older.json"
    path.write_text(
        json.dumps(
            {
                "version": 0,
                "completed": ["lab01_frame_and_headers"],
                "run_counts": {"lab01_frame_and_headers": 2},
                "pass_counts": {"lab01_frame_and_headers": 1},
                "last_result": {"lab01_frame_and_headers": "PASS"},
            }
        ),
        encoding="utf-8",
    )
    state = load_progress(path)
    output = capsys.readouterr().out
    assert "older than supported version" in output
    assert state.version == 1
    assert state.completed == ("lab01_frame_and_headers",)


def test_migrate_progress_adds_current_version(tmp_path) -> None:
    path = tmp_path / "legacy.json"
    path.write_text(
        json.dumps(
            {
                "completed": ["lab01_frame_and_headers"],
                "run_counts": {"lab01_frame_and_headers": 2},
                "pass_counts": {"lab01_frame_and_headers": 1},
                "last_result": {"lab01_frame_and_headers": "PASS"},
            }
        ),
        encoding="utf-8",
    )
    migrated_path = migrate_progress(path)
    migrated = load_progress(migrated_path)
    assert migrated.version == 1
    assert migrated.completed == ("lab01_frame_and_headers",)
