from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
TUTORIAL_DIR = REPO_ROOT / "docs" / "tutorial"


def test_checkpoint_guide_lines_do_not_merge_multiple_descriptions() -> None:
    for chapter in sorted(TUTORIAL_DIR.glob("lab*.md")):
        for line in chapter.read_text(encoding="utf-8").splitlines():
            assert ".;" not in line
