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
    assert selected is not None, "Expected a route match for 10.1.2.3 but got None; both 10.0.0.0/8 and 10.1.0.0/16 should match"
    assert selected.prefix_len == 16, (
        f"Expected /16 route (longest prefix match) but got /{selected.prefix_len}; "
        "LPM must prefer the more specific prefix (10.1.0.0/16) over 10.0.0.0/8"
    )
    assert selected.out_if == "eth1", (
        f"Expected out_if=eth1 for the /16 route but got {selected.out_if!r}"
    )


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
    assert forwarded.action == "FORWARD", f"Expected FORWARD for TTL=3 with valid route but got {forwarded.action!r}"
    assert forwarded.ttl_after == 2, f"Expected ttl_after=2 (decremented from 3) but got {forwarded.ttl_after}"

    dropped_ttl = forward_packet(IPv4Packet(src_ip="198.51.100.1", dst_ip="203.0.113.10", ttl=1), route)
    assert dropped_ttl.action == "DROP", f"Expected DROP for TTL=1 but got {dropped_ttl.action!r}; TTL=1 expires when decremented to 0"
    assert dropped_ttl.reason == "TTL_EXPIRED", f"Expected reason TTL_EXPIRED but got {dropped_ttl.reason!r}"

    dropped_route = forward_packet(IPv4Packet(src_ip="198.51.100.1", dst_ip="198.18.0.1", ttl=10), None)
    assert dropped_route.action == "DROP", f"Expected DROP when route=None (no matching route) but got {dropped_route.action!r}"
    assert dropped_route.reason == "NO_ROUTE", f"Expected reason NO_ROUTE but got {dropped_route.reason!r}"


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
