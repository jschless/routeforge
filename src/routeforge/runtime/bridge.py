"""Typed bridge messages, validation, and idempotent apply helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from routeforge.debug.events import TraceEvent, bridge_apply_event, bridge_emit_event


SIM_DATAPLANE = "DATAPLANE"
SIM_CONTROLPLANE = "CONTROLPLANE"
SIM_SCENARIO = "SCENARIO"


@dataclass(frozen=True)
class MessageSpec:
    allowed_sources: tuple[str, ...]
    allowed_targets: tuple[str, ...]
    required_payload: dict[str, type]


class BridgeValidationError(ValueError):
    """Raised when a bridge message does not satisfy the contract."""


MESSAGE_REGISTRY: dict[str, MessageSpec] = {
    "ROUTE_INSTALL": MessageSpec(
        allowed_sources=(SIM_CONTROLPLANE,),
        allowed_targets=(SIM_DATAPLANE,),
        required_payload={
            "prefix": str,
            "prefix_len": int,
            "protocol": str,
            "next_hop": str,
            "out_if": str,
            "admin_distance": int,
            "metric": int,
        },
    ),
    "ROUTE_WITHDRAW": MessageSpec(
        allowed_sources=(SIM_CONTROLPLANE,),
        allowed_targets=(SIM_DATAPLANE,),
        required_payload={
            "prefix": str,
            "prefix_len": int,
            "protocol": str,
            "reason": str,
        },
    ),
    "NEXTHOP_REWRITE_UPDATE": MessageSpec(
        allowed_sources=(SIM_CONTROLPLANE,),
        allowed_targets=(SIM_DATAPLANE,),
        required_payload={
            "next_hop": str,
            "resolved_mac": str,
            "out_if": str,
            "state": str,
        },
    ),
    "POLICY_PROGRAM_UPDATE": MessageSpec(
        allowed_sources=(SIM_CONTROLPLANE,),
        allowed_targets=(SIM_DATAPLANE,),
        required_payload={
            "policy_type": str,
            "program_id": str,
            "operation": str,
            "entries": list,
        },
    ),
    "INTERFACE_STATE_CHANGE": MessageSpec(
        allowed_sources=(SIM_DATAPLANE,),
        allowed_targets=(SIM_CONTROLPLANE,),
        required_payload={
            "if_name": str,
            "state": str,
            "reason": str,
        },
    ),
    "ADJACENCY_SIGNAL": MessageSpec(
        allowed_sources=(SIM_DATAPLANE,),
        allowed_targets=(SIM_CONTROLPLANE,),
        required_payload={
            "protocol": str,
            "peer_id": str,
            "if_name": str,
            "state": str,
        },
    ),
    "FORWARDING_FAILURE_SIGNAL": MessageSpec(
        allowed_sources=(SIM_DATAPLANE,),
        allowed_targets=(SIM_CONTROLPLANE,),
        required_payload={
            "flow_key": str,
            "reason_code": str,
            "drop_count_delta": int,
            "egress_if": str,
        },
    ),
    "TRAFFIC_OBSERVATION_SIGNAL": MessageSpec(
        allowed_sources=(SIM_DATAPLANE,),
        allowed_targets=(SIM_CONTROLPLANE,),
        required_payload={
            "flow_key": str,
            "pps": int,
            "bps": int,
            "dscp_histogram": dict,
            "sample_window_ms": int,
        },
    ),
    "FAIL_LINK": MessageSpec(
        allowed_sources=(SIM_SCENARIO,),
        allowed_targets=(SIM_DATAPLANE, SIM_CONTROLPLANE),
        required_payload={
            "scenario_id": str,
            "step_id": str,
            "target": str,
            "expected_effect": str,
        },
    ),
    "RECOVER_LINK": MessageSpec(
        allowed_sources=(SIM_SCENARIO,),
        allowed_targets=(SIM_DATAPLANE, SIM_CONTROLPLANE),
        required_payload={
            "scenario_id": str,
            "step_id": str,
            "target": str,
            "expected_effect": str,
        },
    ),
    "FAIL_PEER": MessageSpec(
        allowed_sources=(SIM_SCENARIO,),
        allowed_targets=(SIM_DATAPLANE, SIM_CONTROLPLANE),
        required_payload={
            "scenario_id": str,
            "step_id": str,
            "target": str,
            "expected_effect": str,
        },
    ),
    "RECOVER_PEER": MessageSpec(
        allowed_sources=(SIM_SCENARIO,),
        allowed_targets=(SIM_DATAPLANE, SIM_CONTROLPLANE),
        required_payload={
            "scenario_id": str,
            "step_id": str,
            "target": str,
            "expected_effect": str,
        },
    ),
}


@dataclass(frozen=True)
class BridgeMessage:
    schema_version: int
    message_id: str
    message_type: str
    source_sim: str
    target_sim: str
    sim_time_ms: int
    priority: int
    node_id: str
    correlation_id: str
    payload: dict[str, Any]


def _require_type(field_name: str, value: Any, expected_type: type) -> None:
    if not isinstance(value, expected_type):
        expected = expected_type.__name__
        actual = type(value).__name__
        raise BridgeValidationError(f"{field_name} must be {expected}, got {actual}")


def validate_message(message: BridgeMessage) -> None:
    """Validate envelope and payload against the bridge contract registry."""

    _require_type("schema_version", message.schema_version, int)
    if message.schema_version != 1:
        raise BridgeValidationError("schema_version must be 1")

    _require_type("message_id", message.message_id, str)
    _require_type("message_type", message.message_type, str)
    _require_type("source_sim", message.source_sim, str)
    _require_type("target_sim", message.target_sim, str)
    _require_type("sim_time_ms", message.sim_time_ms, int)
    _require_type("priority", message.priority, int)
    _require_type("node_id", message.node_id, str)
    _require_type("correlation_id", message.correlation_id, str)
    _require_type("payload", message.payload, dict)

    if not message.message_id:
        raise BridgeValidationError("message_id must not be empty")
    if not message.correlation_id:
        raise BridgeValidationError("correlation_id must not be empty")

    spec = MESSAGE_REGISTRY.get(message.message_type)
    if spec is None:
        raise BridgeValidationError(f"unknown message_type: {message.message_type}")

    if message.source_sim not in spec.allowed_sources:
        raise BridgeValidationError(
            f"message_type {message.message_type} does not allow source_sim {message.source_sim}"
        )

    if message.target_sim not in spec.allowed_targets:
        raise BridgeValidationError(
            f"message_type {message.message_type} does not allow target_sim {message.target_sim}"
        )

    unknown_keys = set(message.payload) - set(spec.required_payload)
    if unknown_keys:
        unknown = ", ".join(sorted(unknown_keys))
        raise BridgeValidationError(f"payload contains unknown keys: {unknown}")

    missing_keys = set(spec.required_payload) - set(message.payload)
    if missing_keys:
        missing = ", ".join(sorted(missing_keys))
        raise BridgeValidationError(f"payload missing required keys: {missing}")

    for key, expected_type in spec.required_payload.items():
        _require_type(f"payload.{key}", message.payload[key], expected_type)


@dataclass
class Bridge:
    """Bridge helper with message validation and idempotent apply semantics."""

    _applied_message_ids: set[str] = field(default_factory=set)
    _trace_events: list[TraceEvent] = field(default_factory=list)
    _next_trace_seq: int = 1

    @property
    def trace_events(self) -> tuple[TraceEvent, ...]:
        return tuple(self._trace_events)

    def _reserve_trace_seq(self) -> int:
        seq = self._next_trace_seq
        self._next_trace_seq += 1
        return seq

    def emit(self, message: BridgeMessage) -> TraceEvent:
        validate_message(message)
        event = bridge_emit_event(message, seq=self._reserve_trace_seq())
        self._trace_events.append(event)
        return event

    def apply(self, message: BridgeMessage) -> bool:
        validate_message(message)
        if message.message_id in self._applied_message_ids:
            return False
        event = bridge_apply_event(message, seq=self._reserve_trace_seq())
        self._trace_events.append(event)
        self._applied_message_ids.add(message.message_id)
        return True
