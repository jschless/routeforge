"""Scenario registries grouped by curriculum phase."""

from __future__ import annotations

from typing import Callable

from routeforge.labs.contracts import LabRunResult
from routeforge.labs.scenarios.phase2 import PHASE2_RUNNERS


def build_lab_registry(phase1_runners: dict[str, Callable[[], LabRunResult]]) -> dict[str, Callable[[], LabRunResult]]:
    merged = dict(phase1_runners)
    merged.update(PHASE2_RUNNERS)
    return merged
