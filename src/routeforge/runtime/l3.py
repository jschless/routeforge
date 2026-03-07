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
        ip = IPv4Address(destination_ip)
        candidates = [route for route in self.routes if ip in route.network]
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda route: (
                -route.prefix_len,
                route.admin_distance,
                route.metric,
                int(route.network.network_address),
                route.next_hop,
            ),
        )


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
    if route is None:
        return ForwardingDecision(
            action="DROP",
            reason="NO_ROUTE",
            ttl_after=None,
            out_if=None,
            next_hop=None,
        )
    if packet.ttl <= 1:
        return ForwardingDecision(
            action="DROP",
            reason="TTL_EXPIRED",
            ttl_after=0,
            out_if=None,
            next_hop=None,
        )
    return ForwardingDecision(
        action="FORWARD",
        reason="FIB_HIT",
        ttl_after=packet.ttl - 1,
        out_if=route.out_if,
        next_hop=route.next_hop,
    )


@dataclass(frozen=True)
class IcmpControlDecision:
    action: str
    reason: str
    icmp_type: str


def icmp_control(packet: IPv4Packet, route: RouteEntry | None) -> IcmpControlDecision:
    if packet.ttl <= 1:
        return IcmpControlDecision(
            action="GENERATE",
            reason="TTL_EXPIRED",
            icmp_type="time_exceeded",
        )
    if route is None:
        return IcmpControlDecision(
            action="GENERATE",
            reason="NO_ROUTE",
            icmp_type="unreachable",
        )
    if packet.protocol == "ICMP" and packet.icmp_type == "echo_request":
        return IcmpControlDecision(
            action="GENERATE",
            reason="ECHO_REQUEST",
            icmp_type="echo_reply",
        )
    return IcmpControlDecision(
        action="NONE",
        reason="NOT_APPLICABLE",
        icmp_type="none",
    )


def explain_drop(decision: ForwardingDecision) -> str:
    if decision.action != "DROP":
        return "forward path healthy"
    return f"drop_reason={decision.reason}"
