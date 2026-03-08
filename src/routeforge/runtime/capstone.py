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

    # TODO(student): implement apply_step.
    """
    raise NotImplementedError("TODO: implement apply_step")


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

    # TODO(student): implement rollback_step.
    """
    raise NotImplementedError("TODO: implement rollback_step")


def convergence_assert(*, state: ScenarioState, expected_routes: dict[str, str], expected_alarms: tuple[str, ...]) -> bool:
    return state.routes == expected_routes and state.alarms == tuple(sorted(expected_alarms))
