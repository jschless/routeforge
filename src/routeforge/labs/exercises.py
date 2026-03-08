"""Executable lab scenario dispatch and error normalization."""

from __future__ import annotations

from typing import Callable

from routeforge.labs.contracts import ErrorOutcome, LabRunResult, LabStepResult, build_result
from routeforge.labs.scenarios.phase1 import PHASE1_RUNNERS
from routeforge.labs.scenarios.phase2 import PHASE2_RUNNERS

LAB_RUNNERS: dict[str, Callable[[], LabRunResult]] = {
    **PHASE1_RUNNERS,
    **PHASE2_RUNNERS,
}


def run_lab(lab_id: str) -> LabRunResult:
    runner = LAB_RUNNERS.get(lab_id)
    if runner is None:
        raise KeyError(lab_id)
    try:
        return runner()
    except NotImplementedError as exc:
        return build_result(
            lab_id,
            [
                LabStepResult(
                    name="implementation_todo",
                    passed=False,
                    status="TODO",
                    detail=f"{exc} — run 'routeforge hint {lab_id}' for contracts",
                    outcome=ErrorOutcome(
                        action="TODO",
                        reason="NOT_IMPLEMENTED",
                        details={"exception": "NotImplementedError", "message": str(exc)},
                    ),
                )
            ],
        )
    except (AttributeError, TypeError) as exc:
        return build_result(
            lab_id,
            [
                LabStepResult(
                    name="implementation_contract_error",
                    passed=False,
                    detail=(
                        f"step failed with {type(exc).__name__}: check your return type "
                        f"matches the function signature — run 'routeforge hint {lab_id}'"
                    ),
                    outcome=ErrorOutcome(
                        action="ERROR",
                        reason="CONTRACT_MISMATCH",
                        details={"exception": type(exc).__name__, "message": str(exc)},
                    ),
                )
            ],
        )
