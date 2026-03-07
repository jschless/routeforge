from __future__ import annotations

from pathlib import Path
import re

from routeforge.labs.exercises import LAB_RUNNERS

REPO_ROOT = Path(__file__).resolve().parents[2]
TUTORIAL_DIR = REPO_ROOT / "docs" / "tutorial"

REQUIRED_HEADINGS = [
    "## Learning objectives",
    "## Prerequisite recap",
    "## Concept walkthrough",
    "## Implementation TODO map",
    "## Verification commands and expected outputs",
    "## Debug trace checkpoints and interpretation guidance",
    "## Failure drills and troubleshooting flow",
    "## Standards and references",
]


def test_phase1_tutorial_chapters_use_required_template() -> None:
    chapters = [TUTORIAL_DIR / f"{lab_id}.md" for lab_id in sorted(LAB_RUNNERS)]
    for chapter in chapters:
        assert chapter.exists(), f"missing tutorial chapter: {chapter.name}"
        text = chapter.read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            assert heading in text, f"{chapter.name} missing heading: {heading}"


def test_docs_markdown_local_links_resolve() -> None:
    link_re = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for markdown in (REPO_ROOT / "docs").rglob("*.md"):
        text = markdown.read_text(encoding="utf-8")
        for target in link_re.findall(text):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            normalized = target.split("#", 1)[0]
            if not normalized:
                continue
            resolved = (markdown.parent / normalized).resolve()
            assert resolved.exists(), f"{markdown} has broken link: {target}"
