from __future__ import annotations

import pytest

from routeforge.tdl.exercises import run_tdl_challenge
from routeforge.tdl.manifest import TDL_CHALLENGES

CHALLENGE_IDS = [entry["id"] for entry in TDL_CHALLENGES]


@pytest.mark.parametrize(
    "challenge_id",
    [pytest.param(challenge_id, marks=pytest.mark.tdl(challenge_id)) for challenge_id in CHALLENGE_IDS],
)
def test_tdl_challenge_runner_passes(challenge_id: str) -> None:
    result = run_tdl_challenge(challenge_id)
    assert result.challenge_id == challenge_id
    assert result.passed is True
    assert result.steps
    assert all(step.passed for step in result.steps)
    assert result.checkpoints
    assert len(result.checkpoints) == len(set(result.checkpoints))


def test_run_tdl_challenge_rejects_unknown_id() -> None:
    with pytest.raises(KeyError, match="unknown tdl challenge"):
        run_tdl_challenge("tdl_unknown")
