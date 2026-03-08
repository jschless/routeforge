from __future__ import annotations

from routeforge.labs.exercises import LAB_RUNNERS
from routeforge.labs.student_targets import load_student_targets, signatures_for_target, validate_student_targets


def test_student_targets_cover_every_lab() -> None:
    targets = load_student_targets()
    assert set(targets) == set(LAB_RUNNERS)


def test_student_targets_have_contiguous_stage_numbers() -> None:
    targets = load_student_targets()
    stages = sorted(target.stage for target in targets.values())
    assert stages == list(range(1, len(LAB_RUNNERS) + 1))


def test_student_target_signatures_are_rendered() -> None:
    targets = load_student_targets()
    sigs = signatures_for_target(targets["lab01_frame_and_headers"])
    assert any("is_valid_mac" in sig for sig in sigs)


def test_student_target_signatures_are_cleanly_formatted() -> None:
    targets = load_student_targets()
    sigs = signatures_for_target(targets["lab12_ospf_network_types_and_dr_bdr"])
    assert all("-> unknown" not in sig for sig in sigs)
    assert all(sig.count("->") == 1 for sig in sigs)
    assert all("routeforge." not in sig for sig in sigs)


def test_student_target_symbols_validate() -> None:
    assert validate_student_targets() == ()
