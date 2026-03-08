"""Deterministic observability and readiness helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadinessResult:
    ready: bool
    failed_checks: tuple[str, ...]


def readiness_check(*, checks: dict[str, bool]) -> ReadinessResult:
    failed = tuple(name for name, passed in sorted(checks.items()) if not passed)
    return ReadinessResult(ready=not failed, failed_checks=failed)


def emit_telemetry(*, component: str, counters: dict[str, int], timestamp_s: int) -> dict[str, object]:
    """Emit a telemetry snapshot with deterministically ordered counters.

    Return a dict with keys:

    - ``"component"``: the ``component`` string unchanged.
    - ``"timestamp_s"``: the ``timestamp_s`` integer unchanged.
    - ``"counters"``: a new dict with the same counter key-value pairs as
      ``counters``, but sorted by counter name (ascending alphabetical order).

    Deterministic ordering ensures that two calls with the same counters in
    different insertion order produce identical output.

    See ``docs/tutorial/lab26_observability_and_ops.md`` for the walkthrough.
    """
    ordered = {name: counters[name] for name in sorted(counters)}
    return {
        "component": component,
        "timestamp_s": timestamp_s,
        "counters": ordered,
    }


def diff_telemetry_snapshots(
    *, before: dict[str, int], after: dict[str, int]
) -> dict[str, int]:
    """Compute the counter delta between two telemetry snapshots.

    For every counter key that appears in either ``before`` or ``after``:

    - ``delta = after.get(key, 0) - before.get(key, 0)``
    - Include the key in the result **only if** ``delta != 0``.

    Examples:
    - Counter increases: ``before={"rx": 10}``, ``after={"rx": 15}`` → ``{"rx": 5}``
    - Counter disappears: ``before={"rx": 10}``, ``after={}`` → ``{"rx": -10}``
    - Counter appears: ``before={}``, ``after={"rx": 5}`` → ``{"rx": 5}``
    - No change: ``before={"rx": 10}``, ``after={"rx": 10}`` → ``{}``

    Return the result sorted by counter name (ascending alphabetical).

    See ``docs/tutorial/lab26_observability_and_ops.md`` for the walkthrough.
    """
    all_keys = set(before) | set(after)
    result = {}
    for key in sorted(all_keys):
        delta = after.get(key, 0) - before.get(key, 0)
        if delta != 0:
            result[key] = delta
    return result
