from __future__ import annotations

import json

from routeforge.tdl.progress import load_tdl_progress, migrate_tdl_progress


def test_load_legacy_tdl_progress_without_version_preserves_state(tmp_path, capsys) -> None:
    path = tmp_path / "legacy-tdl.json"
    path.write_text(
        json.dumps(
            {
                "completed": ["tdl_auto_01_yang_path_validation"],
                "total_xp": 100,
                "badges": [],
                "run_counts": {"tdl_auto_01_yang_path_validation": 1},
                "pass_counts": {"tdl_auto_01_yang_path_validation": 1},
                "last_result": {"tdl_auto_01_yang_path_validation": "PASS"},
            }
        ),
        encoding="utf-8",
    )
    state = load_tdl_progress(path)
    output = capsys.readouterr().out
    assert "loaded legacy state" in output
    assert state.version == 1
    assert state.completed == ("tdl_auto_01_yang_path_validation",)
    assert state.total_xp == 100
    assert state.run_counts == {"tdl_auto_01_yang_path_validation": 1}
    assert state.pass_counts == {"tdl_auto_01_yang_path_validation": 1}
    assert state.last_result == {"tdl_auto_01_yang_path_validation": "PASS"}


def test_load_older_tdl_progress_version_preserves_state(tmp_path, capsys) -> None:
    path = tmp_path / "older-tdl.json"
    path.write_text(
        json.dumps(
            {
                "version": 0,
                "completed": ["tdl_auto_01_yang_path_validation"],
                "total_xp": 100,
                "badges": [],
                "run_counts": {"tdl_auto_01_yang_path_validation": 1},
                "pass_counts": {"tdl_auto_01_yang_path_validation": 1},
                "last_result": {"tdl_auto_01_yang_path_validation": "PASS"},
            }
        ),
        encoding="utf-8",
    )
    state = load_tdl_progress(path)
    output = capsys.readouterr().out
    assert "older than supported version" in output
    assert state.version == 1
    assert state.completed == ("tdl_auto_01_yang_path_validation",)


def test_migrate_tdl_progress_adds_current_version(tmp_path) -> None:
    path = tmp_path / "legacy-tdl.json"
    path.write_text(
        json.dumps(
            {
                "completed": ["tdl_auto_01_yang_path_validation"],
                "total_xp": 100,
                "badges": [],
                "run_counts": {"tdl_auto_01_yang_path_validation": 1},
                "pass_counts": {"tdl_auto_01_yang_path_validation": 1},
                "last_result": {"tdl_auto_01_yang_path_validation": "PASS"},
            }
        ),
        encoding="utf-8",
    )
    migrated_path = migrate_tdl_progress(path)
    state = load_tdl_progress(migrated_path)
    assert state.version == 1
    assert state.completed == ("tdl_auto_01_yang_path_validation",)
    assert state.total_xp == 100
