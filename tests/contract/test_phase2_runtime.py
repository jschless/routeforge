from __future__ import annotations

import pytest

from routeforge.runtime.phase2 import (
    DhcpBinding,
    MpbgpPath,
    dhcp_snooping_dai,
    evpn_vxlan_control,
    fhrp_track_failover,
    ipv6_nd_slaac_ra_guard,
    l3vpn_vrf_route_targets,
    mpls_ldp_lfib,
    mpbgp_ipv6_unicast,
    ospfv3_adjacency_lsdb,
    port_security_ip_source_guard,
    qos_police_shape,
    qos_wred_decision,
    redistribute_with_loop_guard,
)


def test_dhcp_snooping_dai_learning_and_validation() -> None:
    learned, action = dhcp_snooping_dai(
        trusted_port=True,
        binding=None,
        arp_mac="00:aa:00:00:00:01",
        arp_ip="10.10.10.10",
    )
    assert action == "ALLOW"
    assert learned == DhcpBinding(mac="00:aa:00:00:00:01", ip="10.10.10.10", vlan=10)

    _, mismatch = dhcp_snooping_dai(
        trusted_port=False,
        binding=learned,
        arp_mac="00:bb:00:00:00:01",
        arp_ip="10.10.10.10",
    )
    assert mismatch == "DROP"


def test_dhcp_snooping_dai_drops_when_no_binding_on_untrusted_port() -> None:
    learned, action = dhcp_snooping_dai(
        trusted_port=False,
        binding=None,
        arp_mac="00:aa:00:00:00:01",
        arp_ip="10.10.10.10",
    )
    assert learned is None
    assert action == "DROP"


def test_port_security_and_ip_source_guard_enforcement() -> None:
    learned, action = port_security_ip_source_guard(
        max_macs=1,
        learned_macs=(),
        source_mac="00:11:22:33:44:55",
        source_ip_allowed=True,
    )
    assert action == "ALLOW"
    assert learned == ("00:11:22:33:44:55",)

    _, violation = port_security_ip_source_guard(
        max_macs=1,
        learned_macs=learned,
        source_mac="00:11:22:33:44:66",
        source_ip_allowed=True,
    )
    assert violation == "PORTSEC_VIOLATION"

    _, ipsg = port_security_ip_source_guard(
        max_macs=1,
        learned_macs=learned,
        source_mac="00:11:22:33:44:55",
        source_ip_allowed=False,
    )
    assert ipsg == "IPSG_DENY"


def test_qos_police_shape_limits_offered_rate() -> None:
    admitted, released = qos_police_shape(offered_kbps=2000, cir_kbps=1500, shape_rate_kbps=1200)
    assert admitted == 1500
    assert released == 1200


def test_qos_wred_decision_thresholds() -> None:
    assert qos_wred_decision(queue_depth=40, min_threshold=50, max_threshold=100, ecn_capable=False) == "FORWARD"
    assert qos_wred_decision(queue_depth=60, min_threshold=50, max_threshold=100, ecn_capable=True) == "MARK"
    assert qos_wred_decision(queue_depth=60, min_threshold=50, max_threshold=100, ecn_capable=False) == "DROP"
    assert qos_wred_decision(queue_depth=120, min_threshold=50, max_threshold=100, ecn_capable=True) == "DROP"


def test_redistribute_with_loop_guard_tags_and_suppresses() -> None:
    tags, action = redistribute_with_loop_guard(
        source_prefix="10.40.0.0/16",
        source_protocol="OSPF",
        existing_tags=set(),
    )
    assert action == "IMPORT"
    assert "OSPF:10.40.0.0/16" in tags

    second_tags, second_action = redistribute_with_loop_guard(
        source_prefix="10.40.0.0/16",
        source_protocol="OSPF",
        existing_tags=tags,
    )
    assert second_action == "LOOP_SUPPRESS"
    assert second_tags == tags


def test_fhrp_track_failover_switches_active_router() -> None:
    assert fhrp_track_failover(active_router="R1", standby_router="R2", tracked_object_up=True) == "R1"
    assert fhrp_track_failover(active_router="R1", standby_router="R2", tracked_object_up=False) == "R2"


def test_ipv6_nd_slaac_ra_guard_allows_only_trusted_ras() -> None:
    allow, address = ipv6_nd_slaac_ra_guard(
        ra_trusted=True,
        source_link_local="fe80::10",
        prefix="2001:db8:100::",
    )
    assert allow == "ALLOW"
    assert address == "2001:db8:100::10"

    drop, dropped_address = ipv6_nd_slaac_ra_guard(
        ra_trusted=False,
        source_link_local="fe80::20",
        prefix="2001:db8:100::",
    )
    assert drop == "DROP"
    assert dropped_address == ""


def test_ospfv3_adjacency_lsdb_transitions() -> None:
    state_down, lsdb_down = ospfv3_adjacency_lsdb(hello_ok=False, lsa_id="lsa-1", lsdb=set())
    assert state_down == "DOWN"
    assert lsdb_down == set()

    state_full, lsdb_full = ospfv3_adjacency_lsdb(hello_ok=True, lsa_id="lsa-1", lsdb=set())
    assert state_full == "FULL"
    assert lsdb_full == {"lsa-1"}


def test_mpbgp_ipv6_unicast_best_path_and_empty_input() -> None:
    with pytest.raises(ValueError):
        mpbgp_ipv6_unicast([])

    best = mpbgp_ipv6_unicast(
        [
            MpbgpPath(prefix="2001:db8:1::/64", local_pref=150, as_path_len=3, next_hop="2001:db8::2"),
            MpbgpPath(prefix="2001:db8:1::/64", local_pref=150, as_path_len=2, next_hop="2001:db8::3"),
            MpbgpPath(prefix="2001:db8:1::/64", local_pref=200, as_path_len=5, next_hop="2001:db8::4"),
        ]
    )
    assert best.next_hop == "2001:db8::4"


def test_mpls_l3vpn_and_evpn_helpers() -> None:
    assert mpls_ldp_lfib(fec="10.70.0.0/16", local_label=16001, outgoing_label=24001) == ("10.70.0.0/16", 16001, 24001)

    assert l3vpn_vrf_route_targets(import_rts={"65000:100"}, route_rt="65000:100", prefix="172.16.10.0/24") == (
        "IMPORT",
        "172.16.10.0/24",
    )
    assert l3vpn_vrf_route_targets(import_rts={"65000:100"}, route_rt="65000:200", prefix="172.16.10.0/24") == (
        "REJECT",
        "172.16.10.0/24",
    )

    assert evpn_vxlan_control(mac="00:50:56:aa:bb:cc", ip="10.39.0.10", vni=5000, known_vnis={5000}) == (
        "INSTALL",
        "00:50:56:aa:bb:cc|10.39.0.10|5000",
    )
    assert evpn_vxlan_control(mac="00:50:56:aa:bb:cc", ip="10.39.0.10", vni=5001, known_vnis={5000}) == (
        "REJECT",
        "",
    )
