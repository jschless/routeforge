from __future__ import annotations

from pathlib import Path

from routeforge.tdl.manifest import TDL_CHALLENGES

REPO_ROOT = Path(__file__).resolve().parents[2]
TDL_DOC = REPO_ROOT / "docs" / "tdl.md"


def test_tdl_doc_exists_and_lists_all_challenges() -> None:
    assert TDL_DOC.exists()
    text = TDL_DOC.read_text(encoding="utf-8")
    for entry in TDL_CHALLENGES:
        assert f"`{entry['id']}`" in text


def test_tdl_doc_lists_core_cli_commands() -> None:
    text = TDL_DOC.read_text(encoding="utf-8")
    assert "routeforge tdl list" in text
    assert "routeforge tdl show" in text
    assert "routeforge tdl check" in text
    assert "routeforge tdl run" in text
    assert "routeforge tdl progress show" in text
