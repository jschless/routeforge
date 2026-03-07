"""Deterministic capstone scenario helpers."""

from __future__ import annotations

from dataclasses import dataclass, replace


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
    routes = dict(state.routes)
    routes.update(route_updates or {})

    alarm_set = set(state.alarms)
    for alarm in clear_alarms:
        alarm_set.discard(alarm)
    for alarm in raise_alarms:
        alarm_set.add(alarm)

    return replace(state, label=label, routes=routes, alarms=tuple(sorted(alarm_set)))


def convergence_assert(*, state: ScenarioState, expected_routes: dict[str, str], expected_alarms: tuple[str, ...]) -> bool:
    return state.routes == expected_routes and state.alarms == tuple(sorted(expected_alarms))
