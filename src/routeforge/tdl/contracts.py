"""TDL scenario contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TdlOutcome:
    action: str
    reason: str
    checkpoints: tuple[str, ...]
    details: dict[str, Any]


@dataclass(frozen=True)
class TdlStepResult:
    name: str
    passed: bool
    detail: str
    outcome: TdlOutcome


@dataclass(frozen=True)
class TdlRunResult:
    challenge_id: str
    passed: bool
    steps: tuple[TdlStepResult, ...]
    checkpoints: tuple[str, ...]


def build_tdl_result(challenge_id: str, steps: list[TdlStepResult]) -> TdlRunResult:
    seen: set[str] = set()
    checkpoints: list[str] = []
    for step in steps:
        for checkpoint in step.outcome.checkpoints:
            if checkpoint not in seen:
                seen.add(checkpoint)
                checkpoints.append(checkpoint)
    return TdlRunResult(
        challenge_id=challenge_id,
        passed=all(step.passed for step in steps),
        steps=tuple(steps),
        checkpoints=tuple(checkpoints),
    )
