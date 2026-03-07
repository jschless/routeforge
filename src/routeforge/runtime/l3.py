"""Minimal L3 routing/forwarding helpers for foundational IPv4 labs."""

from __future__ import annotations

from dataclasses import dataclass, field
from ipaddress import IPv4Network


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
        """Return the best matching route for ``destination_ip``, or None.

        Tiebreak chain (apply in order; first difference wins):

        1. **Longest prefix length** — higher ``prefix_len`` wins (most specific).
        2. **Lowest admin_distance** — lower value wins (more trusted protocol).
        3. **Lowest metric** — lower value wins (shorter path).
        4. **Lowest next_hop** — lexicographic string compare; lower wins.

        Return ``None`` if no route matches.

        Use ``route.network`` (an ``IPv4Network``) and its ``.supernet_of()``
        or the ``in`` operator to test membership, e.g.:
            ``IPv4Address(destination_ip) in route.network``

        See ``docs/tutorial/lab07_ipv4_subnet_and_rib.md`` for the walkthrough.

        # TODO(student): implement RibTable.lookup using the tiebreak chain above.
        """
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
    """Decide how to forward or drop an IPv4 packet.

    Rules (apply in order):

    1. If ``route`` is None:
       return ``ForwardingDecision(action="DROP", reason="NO_ROUTE",
       ttl_after=None, out_if=None, next_hop=None)``.

    2. If ``packet.ttl <= 1`` (TTL exhausted before decrement):
       return ``ForwardingDecision(action="DROP", reason="TTL_EXPIRED",
       ttl_after=None, out_if=None, next_hop=None)``.

    3. Otherwise (normal forward): decrement TTL by 1 and return
       ``ForwardingDecision(action="FORWARD", reason="ROUTE_FOUND",
       ttl_after=packet.ttl - 1, out_if=route.out_if, next_hop=route.next_hop)``.

    # TODO(student): implement forward_packet using the rules above.
    """
    raise NotImplementedError("TODO: implement forward_packet")


@dataclass(frozen=True)
class IcmpControlDecision:
    action: str
    reason: str
    icmp_type: str


def icmp_control(packet: IPv4Packet, route: RouteEntry | None) -> IcmpControlDecision:
    """Determine the ICMP control-plane response for a received packet.

    Rules (apply in order):

    1. TTL expired (``packet.ttl <= 1``):
       ``IcmpControlDecision(action="SEND_ICMP", reason="TTL_EXPIRED",
       icmp_type="TIME_EXCEEDED")``.

    2. No route (``route is None``):
       ``IcmpControlDecision(action="SEND_ICMP", reason="NO_ROUTE",
       icmp_type="DEST_UNREACHABLE")``.

    3. Echo request (``packet.icmp_type == "ECHO_REQUEST"``):
       ``IcmpControlDecision(action="SEND_ICMP", reason="ECHO_REPLY",
       icmp_type="ECHO_REPLY")``.

    4. Otherwise:
       ``IcmpControlDecision(action="FORWARD", reason="ROUTE_FOUND",
       icmp_type="NONE")``.

    # TODO(student): implement icmp_control using the rules above.
    """
    raise NotImplementedError("TODO: implement icmp_control")


def explain_drop(decision: ForwardingDecision) -> str:
    """Return a stable, machine-readable string explaining a DROP decision.

    Format: ``"DROP:<reason>"`` where ``reason`` is ``decision.reason``.
    Example: ``"DROP:NO_ROUTE"`` or ``"DROP:TTL_EXPIRED"``.

    If ``decision.action != "DROP"``, return ``"NOT_A_DROP"``.

    # TODO(student): implement explain_drop.
    """
    raise NotImplementedError("TODO: implement explain_drop")
