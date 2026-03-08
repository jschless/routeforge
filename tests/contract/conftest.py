from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _patch_default_progress_paths(tmp_path, monkeypatch) -> None:
    progress_path = tmp_path / "home" / ".routeforge_progress.json"
    legacy_progress_path = tmp_path / ".routeforge_progress.json"
    tdl_progress_path = tmp_path / "home" / ".routeforge_tdl_progress.json"
    legacy_tdl_progress_path = tmp_path / ".routeforge_tdl_progress.json"

    monkeypatch.setattr("routeforge.labs.progress.DEFAULT_PROGRESS_PATH", progress_path)
    monkeypatch.setattr("routeforge.labs.progress.LEGACY_PROGRESS_PATH", legacy_progress_path)
    monkeypatch.setattr("routeforge.tdl.progress.DEFAULT_TDL_PROGRESS_PATH", tdl_progress_path)
    monkeypatch.setattr("routeforge.tdl.progress.LEGACY_TDL_PROGRESS_PATH", legacy_tdl_progress_path)

    monkeypatch.setattr("routeforge.cli.DEFAULT_PROGRESS_PATH", progress_path)
    monkeypatch.setattr("routeforge.cli.LEGACY_PROGRESS_PATH", legacy_progress_path)
    monkeypatch.setattr("routeforge.cli.DEFAULT_TDL_PROGRESS_PATH", tdl_progress_path)
    monkeypatch.setattr("routeforge.cli.LEGACY_TDL_PROGRESS_PATH", legacy_tdl_progress_path)
