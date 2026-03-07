"""Deterministic capstone scenario helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioState:
    label: str
    routes: dict[str, str]
    alarms: tuple[str, ...]


def apply_step(
    state: ScenarioState,
    *,
    label: str,
    route_updates: dict[str, str] | None = None,
    clear_alarms: tuple[str, ...] = (),
    raise_alarms: tuple[str, ...] = (),
) -> ScenarioState:
    # TODO(student): apply deterministic scenario route/alarm state updates.
    raise NotImplementedError("TODO: implement apply_step")


def convergence_assert(*, state: ScenarioState, expected_routes: dict[str, str], expected_alarms: tuple[str, ...]) -> bool:
    return state.routes == expected_routes and state.alarms == tuple(sorted(expected_alarms))
