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
    ordered = {name: counters[name] for name in sorted(counters)}
    return {
        "component": component,
        "timestamp_s": timestamp_s,
        "counters": ordered,
    }
