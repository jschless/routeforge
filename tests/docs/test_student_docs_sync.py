from __future__ import annotations

from pathlib import Path
import re

from routeforge.labs.conformance import load_conformance_matrix
from routeforge.labs.student_targets import load_student_targets

REPO_ROOT = Path(__file__).resolve().parents[2]
STUDENT_TASK_MAP = REPO_ROOT / "docs" / "student_task_map.md"
TUTORIAL_DIR = REPO_ROOT / "docs" / "tutorial"
SCENARIO_DIR = REPO_ROOT / "src" / "routeforge" / "labs" / "scenarios"


def test_student_task_map_matches_student_targets_yaml() -> None:
    text = STUDENT_TASK_MAP.read_text(encoding="utf-8")
    for lab_id, target in load_student_targets().items():
        expected_row = (
            f"| {target.stage} | `{lab_id}` | `{target.path}` | "
            + ", ".join(f"`{symbol}`" for symbol in target.symbols)
            + " |"
        )
        assert expected_row in text


def test_tutorial_file_paths_match_student_targets_yaml() -> None:
    for lab_id, target in load_student_targets().items():
        text = (TUTORIAL_DIR / f"{lab_id}.md").read_text(encoding="utf-8")
        assert f"- File: `{target.path}`" in text


def test_tutorial_checkpoint_tokens_exist_in_canonical_sources() -> None:
    canonical = _canonical_checkpoints()
    for chapter in sorted(TUTORIAL_DIR.glob("lab*.md")):
        tokens = _checkpoint_tokens(chapter.read_text(encoding="utf-8"))
        assert tokens <= canonical, f"{chapter.name} has unknown checkpoint tokens: {sorted(tokens - canonical)}"


def _canonical_checkpoints() -> set[str]:
    matrix = load_conformance_matrix()
    checkpoints: set[str] = set()
    for feature in matrix.features_by_id.values():
        checkpoints.update(feature.checkpoints)

    for scenario in SCENARIO_DIR.glob("*.py"):
        text = scenario.read_text(encoding="utf-8")
        for match in re.finditer(r"checkpoints=\(([^)]*)\)", text, re.DOTALL):
            checkpoints.update(re.findall(r'"([A-Z][A-Z0-9_]+)"', match.group(1)))
    return checkpoints


def _checkpoint_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for line in text.splitlines():
        if "checkpoint" not in line.lower():
            continue
        match = re.match(r"\s*-\s*`([A-Z][A-Z0-9_]+)`:", line)
        if match is not None and "_" in match.group(1):
            tokens.add(match.group(1))
        if "checkpoints:" in line.lower():
            _, _, suffix = line.partition(":")
            tokens.update(token for token in re.findall(r"[A-Z][A-Z0-9_]+", suffix) if "_" in token)
    return tokens
