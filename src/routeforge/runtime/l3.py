"""Minimal L3 routing/forwarding helpers for foundational IPv4 labs."""

from __future__ import annotations

from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv4Network


@dataclass(frozen=True)
class RouteEntry:
    prefix: str
    prefix_len: int
    next_hop: str
    out_if: str
    protocol: str
    admin_distance: int
    metric: int

    @property
    def network(self) -> IPv4Network:
        return IPv4Network(f"{self.prefix}/{self.prefix_len}", strict=False)


@dataclass
class RibTable:
    routes: list[RouteEntry] = field(default_factory=list)

    def install(self, route: RouteEntry) -> None:
        self.routes.append(route)

    def lookup(self, destination_ip: str) -> RouteEntry | None:
        # TODO(student): return best route via deterministic longest-prefix match policy.
        raise NotImplementedError("TODO: implement RibTable.lookup")


@dataclass(frozen=True)
class IPv4Packet:
    src_ip: str
    dst_ip: str
    ttl: int
    protocol: str = "ICMP"
    icmp_type: str | None = None


@dataclass(frozen=True)
class ForwardingDecision:
    action: str
    reason: str
    ttl_after: int | None
    out_if: str | None
    next_hop: str | None


def forward_packet(packet: IPv4Packet, route: RouteEntry | None) -> ForwardingDecision:
    # TODO(student): implement forwarding/drop decision with TTL behavior.
    raise NotImplementedError("TODO: implement forward_packet")


@dataclass(frozen=True)
class IcmpControlDecision:
    action: str
    reason: str
    icmp_type: str


def icmp_control(packet: IPv4Packet, route: RouteEntry | None) -> IcmpControlDecision:
    # TODO(student): implement deterministic ICMP control-plane response logic.
    raise NotImplementedError("TODO: implement icmp_control")


def explain_drop(decision: ForwardingDecision) -> str:
    # TODO(student): explain drop decisions in a stable machine-readable string.
    raise NotImplementedError("TODO: implement explain_drop")
