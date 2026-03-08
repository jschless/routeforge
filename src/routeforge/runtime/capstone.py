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
    """Apply a scenario step to produce the next state.

    Rules (apply in order):

    1. Merge route updates: start with ``state.routes``, then overlay
       ``route_updates`` (if not None).  Keys in ``route_updates`` replace or
       add entries; existing keys not mentioned are kept.
    2. Compute new alarms: start with ``state.alarms``, remove entries in
       ``clear_alarms``, then add entries in ``raise_alarms`` that are not
       already present.  Result must be **sorted** (deterministic order).
    3. Return a new ``ScenarioState(label=label, routes=new_routes, alarms=new_alarms)``.

    ``ScenarioState`` is a frozen dataclass — never mutate in place; always
    return a new instance.

    See ``docs/tutorial/lab27_capstone_incident_drill.md`` for the walkthrough.
    """
    routes = dict(state.routes)
    routes.update(route_updates or {})

    alarm_set = set(state.alarms)
    for alarm in clear_alarms:
        alarm_set.discard(alarm)
    for alarm in raise_alarms:
        alarm_set.add(alarm)

    return replace(state, label=label, routes=routes, alarms=tuple(sorted(alarm_set)))


def rollback_step(state: ScenarioState, *, snapshot: ScenarioState) -> ScenarioState:
    """Restore scenario state to a previous snapshot.

    Returns a new ``ScenarioState`` with:

    - ``label``: ``f"rollback:{snapshot.label}"`` — indicates this is a rollback
      and identifies the checkpoint being restored.
    - ``routes``: ``snapshot.routes`` — restore the previous routing table.
    - ``alarms``: ``snapshot.alarms`` — restore the previous alarm set.

    Use this after a failed ``apply_step`` to undo the change.  The current
    state's label and fields are discarded; only the snapshot's routes and
    alarms survive.

    ``ScenarioState`` is a frozen dataclass — return a new instance, never
    mutate.

    See ``docs/tutorial/lab27_capstone_incident_drill.md`` for the walkthrough.
    """
    return ScenarioState(
        label=f"rollback:{snapshot.label}",
        routes=snapshot.routes,
        alarms=snapshot.alarms,
    )


def convergence_assert(*, state: ScenarioState, expected_routes: dict[str, str], expected_alarms: tuple[str, ...]) -> bool:
    return state.routes == expected_routes and state.alarms == tuple(sorted(expected_alarms))
