"""Shared contracts for executable lab scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class TraceableOutcome(Protocol):
    checkpoints: tuple[str, ...]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        ...


@dataclass(frozen=True)
class LabStepResult:
    name: str
    passed: bool
    detail: str
    outcome: TraceableOutcome
    status: str | None = None


@dataclass(frozen=True)
class LabRunResult:
    lab_id: str
    passed: bool
    steps: tuple[LabStepResult, ...]
    checkpoints: tuple[str, ...]
    trace_records: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class StpOutcome:
    action: str
    reason: str
    root_node_id: str
    port_roles: dict[tuple[str, str], str]
    checkpoints: tuple[str, ...]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "root_node_id": self.root_node_id,
            "port_roles": [f"{node}:{port}={role}" for (node, port), role in sorted(self.port_roles.items())],
            "checkpoints": list(self.checkpoints),
        }


@dataclass(frozen=True)
class ArpOutcome:
    action: str
    reason: str
    next_hop_ip: str
    checkpoints: tuple[str, ...]
    released_packets: tuple[str, ...] = ()

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "next_hop_ip": self.next_hop_ip,
            "released_packets": list(self.released_packets),
            "checkpoints": list(self.checkpoints),
        }


@dataclass(frozen=True)
class L3Outcome:
    action: str
    reason: str
    destination_ip: str
    checkpoints: tuple[str, ...]
    details: dict[str, Any]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "destination_ip": self.destination_ip,
            "details": self.details,
            "checkpoints": list(self.checkpoints),
        }


@dataclass(frozen=True)
class OspfOutcome:
    action: str
    reason: str
    checkpoints: tuple[str, ...]
    details: dict[str, Any]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "details": self.details,
            "checkpoints": list(self.checkpoints),
        }


@dataclass(frozen=True)
class FeatureOutcome:
    action: str
    reason: str
    checkpoints: tuple[str, ...]
    details: dict[str, Any]

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "details": self.details,
            "checkpoints": list(self.checkpoints),
        }


@dataclass(frozen=True)
class ErrorOutcome:
    action: str
    reason: str
    checkpoints: tuple[str, ...] = ()
    details: dict[str, Any] | None = None

    def to_trace_record(self, *, step: str, sequence: int) -> dict[str, Any]:
        return {
            "seq": sequence,
            "step": step,
            "action": self.action,
            "reason": self.reason,
            "details": self.details or {},
            "checkpoints": list(self.checkpoints),
        }


def _unique_checkpoints(outcomes: list[TraceableOutcome]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for outcome in outcomes:
        for checkpoint in outcome.checkpoints:
            if checkpoint not in seen:
                seen.add(checkpoint)
                ordered.append(checkpoint)
    return tuple(ordered)


def build_result(lab_id: str, steps: list[LabStepResult]) -> LabRunResult:
    outcomes = [step.outcome for step in steps]
    checkpoints = _unique_checkpoints(outcomes)
    traces = tuple(
        step.outcome.to_trace_record(step=step.name, sequence=index + 1)
        for index, step in enumerate(steps)
    )
    return LabRunResult(
        lab_id=lab_id,
        passed=all(step.passed for step in steps),
        steps=tuple(steps),
        checkpoints=checkpoints,
        trace_records=traces,
    )
