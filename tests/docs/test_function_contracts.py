from __future__ import annotations

from pathlib import Path

from routeforge.labs.manifest import LABS

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_DOC = REPO_ROOT / "docs" / "function_contracts.md"


def test_function_contracts_doc_exists_and_lists_all_labs() -> None:
    assert CONTRACT_DOC.exists()
    text = CONTRACT_DOC.read_text(encoding="utf-8")
    for entry in LABS:
        assert f"`{entry['id']}`" in text


def test_function_contracts_doc_lists_target_signature_column() -> None:
    text = CONTRACT_DOC.read_text(encoding="utf-8")
    assert "Target Signatures" in text
    assert "Required MUST Checkpoints" in text
