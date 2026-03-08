"""Shared scenario helper utilities."""

from __future__ import annotations

from routeforge.labs.contracts import L3Outcome
from routeforge.runtime.l3 import ForwardingDecision, IcmpControlDecision, IPv4Packet


def forward_outcome(packet: IPv4Packet, decision: ForwardingDecision, checkpoints: tuple[str, ...]) -> L3Outcome:
    return L3Outcome(
        action=decision.action,
        reason=decision.reason,
        destination_ip=packet.dst_ip,
        checkpoints=checkpoints,
        details={
            "ttl_after": decision.ttl_after,
            "out_if": decision.out_if,
            "next_hop": decision.next_hop,
        },
    )


def icmp_outcome(packet: IPv4Packet, decision: IcmpControlDecision, checkpoint: str) -> L3Outcome:
    return L3Outcome(
        action=decision.action,
        reason=decision.reason,
        destination_ip=packet.dst_ip,
        checkpoints=(checkpoint,),
        details={"icmp_type": decision.icmp_type},
    )
