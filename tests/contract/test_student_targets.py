from __future__ import annotations

from routeforge.labs.exercises import LAB_RUNNERS
from routeforge.labs.student_targets import load_student_targets


def test_student_targets_cover_every_lab() -> None:
    targets = load_student_targets()
    assert set(targets) == set(LAB_RUNNERS)


def test_student_targets_have_contiguous_stage_numbers() -> None:
    targets = load_student_targets()
    stages = sorted(target.stage for target in targets.values())
    assert stages == list(range(1, len(LAB_RUNNERS) + 1))
