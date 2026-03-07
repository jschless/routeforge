"""Debug trace events for deterministic runtime checkpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from routeforge.runtime.bridge import BridgeMessage


@dataclass(frozen=True)
class TraceEvent:
    """Normalized event emitted across both simulation domains."""

    seq: int
    sim_time_ms: int
    node_id: str
    sim_domain: str
    checkpoint: str
    message_id: str
    message_type: str
    correlation_id: str
    details: dict[str, Any] = field(default_factory=dict)


def bridge_emit_event(message: BridgeMessage, seq: int) -> TraceEvent:
    """Create a bridge-emit checkpoint event."""

    return TraceEvent(
        seq=seq,
        sim_time_ms=message.sim_time_ms,
        node_id=message.node_id,
        sim_domain=message.source_sim,
        checkpoint="BRIDGE_EMIT",
        message_id=message.message_id,
        message_type=message.message_type,
        correlation_id=message.correlation_id,
        details={"target_sim": message.target_sim},
    )


def bridge_apply_event(message: BridgeMessage, seq: int) -> TraceEvent:
    """Create a bridge-apply checkpoint event."""

    return TraceEvent(
        seq=seq,
        sim_time_ms=message.sim_time_ms,
        node_id=message.node_id,
        sim_domain=message.target_sim,
        checkpoint="BRIDGE_APPLY",
        message_id=message.message_id,
        message_type=message.message_type,
        correlation_id=message.correlation_id,
        details={"source_sim": message.source_sim},
    )
