from __future__ import annotations

from routeforge.runtime.l3 import IPv4Packet, RibTable, RouteEntry, forward_packet, icmp_control


def test_rib_lookup_prefers_longest_prefix_then_policy() -> None:
    rib = RibTable()
    rib.install(
        RouteEntry(
            prefix="10.0.0.0",
            prefix_len=8,
            next_hop="192.0.2.1",
            out_if="eth0",
            protocol="static",
            admin_distance=1,
            metric=10,
        )
    )
    rib.install(
        RouteEntry(
            prefix="10.1.0.0",
            prefix_len=16,
            next_hop="192.0.2.2",
            out_if="eth1",
            protocol="ospf",
            admin_distance=110,
            metric=1,
        )
    )
    selected = rib.lookup("10.1.2.3")
    assert selected is not None
    assert selected.prefix_len == 16
    assert selected.out_if == "eth1"


def test_forward_packet_handles_ttl_and_no_route() -> None:
    route = RouteEntry(
        prefix="203.0.113.0",
        prefix_len=24,
        next_hop="192.0.2.1",
        out_if="eth0",
        protocol="connected",
        admin_distance=0,
        metric=0,
    )

    forwarded = forward_packet(IPv4Packet(src_ip="198.51.100.1", dst_ip="203.0.113.10", ttl=3), route)
    assert forwarded.action == "FORWARD"
    assert forwarded.ttl_after == 2

    dropped_ttl = forward_packet(IPv4Packet(src_ip="198.51.100.1", dst_ip="203.0.113.10", ttl=1), route)
    assert dropped_ttl.action == "DROP"
    assert dropped_ttl.reason == "TTL_EXPIRED"

    dropped_route = forward_packet(IPv4Packet(src_ip="198.51.100.1", dst_ip="198.18.0.1", ttl=10), None)
    assert dropped_route.action == "DROP"
    assert dropped_route.reason == "NO_ROUTE"


def test_icmp_control_outcomes() -> None:
    route = RouteEntry(
        prefix="203.0.113.0",
        prefix_len=24,
        next_hop="192.0.2.1",
        out_if="eth0",
        protocol="connected",
        admin_distance=0,
        metric=0,
    )

    echo = icmp_control(
        IPv4Packet(src_ip="198.51.100.1", dst_ip="203.0.113.10", ttl=64, icmp_type="echo_request"),
        route,
    )
    assert echo.icmp_type == "echo_reply"

    unreachable = icmp_control(
        IPv4Packet(src_ip="198.51.100.1", dst_ip="198.18.0.10", ttl=64, icmp_type="echo_request"),
        None,
    )
    assert unreachable.icmp_type == "unreachable"

    ttl = icmp_control(
        IPv4Packet(src_ip="198.51.100.1", dst_ip="203.0.113.10", ttl=1, icmp_type="echo_request"),
        route,
    )
    assert ttl.icmp_type == "time_exceeded"
