from __future__ import annotations

import pytest

from routeforge.runtime.ipv6 import (
    MpbgpPath,
    derive_slaac_host_id,
    ipv6_nd_slaac_ra_guard,
    mpbgp_ipv6_unicast,
    ospfv3_adjacency_lsdb,
    ospfv3_neighbor_result,
    rank_mpbgp_path,
)
from routeforge.runtime.mpls import (
    evpn_type2_entry,
    evpn_vxlan_control,
    l3vpn_vrf_route_targets,
    lfib_mapping,
    mpls_ldp_lfib,
    vrf_import_action,
)
from routeforge.runtime.qos_advanced import (
    apply_policer,
    qos_police_shape,
    qos_wred_decision,
    wred_decision_profile,
)
from routeforge.runtime.routing_policy import (
    build_redistribution_tag,
    fhrp_track_failover,
    redistribute_with_loop_guard,
    tracked_object_result,
)
from routeforge.runtime.security import (
    DhcpBinding,
    dhcp_snooping_dai,
    learn_binding_if_trusted,
    port_security_ip_source_guard,
    update_secure_mac_table,
)


def test_learn_binding_if_trusted_only_when_missing() -> None:
    learned = learn_binding_if_trusted(
        trusted_port=True,
        binding=None,
        arp_mac="00:aa:00:00:00:01",
        arp_ip="10.10.10.10",
    )
    assert learned == DhcpBinding(mac="00:aa:00:00:00:01", ip="10.10.10.10", vlan=10)

    preserved = learn_binding_if_trusted(
        trusted_port=True,
        binding=learned,
        arp_mac="00:bb:00:00:00:01",
        arp_ip="10.10.10.11",
    )
    assert preserved == learned


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

    missing, drop = dhcp_snooping_dai(
        trusted_port=False,
        binding=None,
        arp_mac="00:aa:00:00:00:01",
        arp_ip="10.10.10.10",
    )
    assert missing is None
    assert drop == "DROP"


def test_update_secure_mac_table_and_ip_source_guard() -> None:
    learned, violated = update_secure_mac_table(
        max_macs=2,
        learned_macs=(),
        source_mac="00:11:22:33:44:55",
    )
    assert violated is False
    assert learned == ("00:11:22:33:44:55",)

    learned_same, violated_same = update_secure_mac_table(
        max_macs=2,
        learned_macs=learned,
        source_mac="00:11:22:33:44:55",
    )
    assert violated_same is False
    assert learned_same == learned

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


def test_apply_policer_and_qos_police_shape_limits() -> None:
    assert apply_policer(offered_kbps=2000, cir_kbps=1500) == 1500
    assert apply_policer(offered_kbps=-1, cir_kbps=1000) == 0
    assert apply_policer(offered_kbps=800, cir_kbps=-10) == 0

    admitted, released = qos_police_shape(offered_kbps=2000, cir_kbps=1500, shape_rate_kbps=1200)
    assert admitted == 1500
    assert released == 1200

    admitted_zero, released_zero = qos_police_shape(offered_kbps=1000, cir_kbps=1000, shape_rate_kbps=-1)
    assert admitted_zero == 1000
    assert released_zero == 0


def test_wred_profile_and_decision_thresholds() -> None:
    assert wred_decision_profile(queue_depth=40, min_threshold=50, max_threshold=100) == "BELOW_MIN"
    assert wred_decision_profile(queue_depth=50, min_threshold=50, max_threshold=100) == "BETWEEN_THRESHOLDS"
    assert wred_decision_profile(queue_depth=100, min_threshold=50, max_threshold=100) == "AT_OR_ABOVE_MAX"

    assert qos_wred_decision(queue_depth=40, min_threshold=50, max_threshold=100, ecn_capable=False) == "FORWARD"
    assert qos_wred_decision(queue_depth=60, min_threshold=50, max_threshold=100, ecn_capable=True) == "MARK"
    assert qos_wred_decision(queue_depth=60, min_threshold=50, max_threshold=100, ecn_capable=False) == "DROP"
    assert qos_wred_decision(queue_depth=120, min_threshold=50, max_threshold=100, ecn_capable=True) == "DROP"


def test_redistribute_with_loop_guard_tags_and_suppresses() -> None:
    tag = build_redistribution_tag(source_prefix="10.40.0.0/16", source_protocol="ospf")
    assert tag == "OSPF:10.40.0.0/16"

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


def test_tracked_object_state_and_failover() -> None:
    assert tracked_object_result(tracked_object_up=True) == "UP"
    assert tracked_object_result(tracked_object_up=False) == "DOWN"
    assert fhrp_track_failover(active_router="R1", standby_router="R2", tracked_object_up=True) == "R1"
    assert fhrp_track_failover(active_router="R1", standby_router="R2", tracked_object_up=False) == "R2"


def test_ipv6_nd_slaac_ra_guard_allows_only_trusted_ras() -> None:
    assert derive_slaac_host_id(source_link_local="fe80::10") == "10"
    assert derive_slaac_host_id(source_link_local="fe80::") == "1"

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


def test_ospfv3_neighbor_and_lsdb_transitions() -> None:
    assert ospfv3_neighbor_result(hello_ok=False) == "DOWN"
    assert ospfv3_neighbor_result(hello_ok=True) == "FULL"

    state_down, lsdb_down = ospfv3_adjacency_lsdb(hello_ok=False, lsa_id="lsa-1", lsdb={"lsa-0"})
    assert state_down == "DOWN"
    assert lsdb_down == {"lsa-0"}

    state_full, lsdb_full = ospfv3_adjacency_lsdb(hello_ok=True, lsa_id="lsa-1", lsdb=set())
    assert state_full == "FULL"
    assert lsdb_full == {"lsa-1"}


def test_mpbgp_ipv6_unicast_best_path_and_empty_input() -> None:
    with pytest.raises(ValueError):
        mpbgp_ipv6_unicast([])

    candidate = MpbgpPath(prefix="2001:db8:1::/64", local_pref=150, as_path_len=3, next_hop="2001:db8::2")
    assert rank_mpbgp_path(candidate) == (-150, 3, "2001:db8::2")

    best = mpbgp_ipv6_unicast(
        [
            candidate,
            MpbgpPath(prefix="2001:db8:1::/64", local_pref=150, as_path_len=2, next_hop="2001:db8::3"),
            MpbgpPath(prefix="2001:db8:1::/64", local_pref=200, as_path_len=5, next_hop="2001:db8::4"),
        ]
    )
    assert best.next_hop == "2001:db8::4"


def test_mpls_l3vpn_and_evpn_helpers() -> None:
    assert lfib_mapping(fec="10.70.0.0/16", local_label=16001, outgoing_label=24001) == ("10.70.0.0/16", 16001, 24001)
    assert mpls_ldp_lfib(fec="10.70.0.0/16", local_label=16001, outgoing_label=24001) == ("10.70.0.0/16", 16001, 24001)

    assert vrf_import_action(import_rts={"65000:100"}, route_rt="65000:100") == "IMPORT"
    assert vrf_import_action(import_rts={"65000:100"}, route_rt="65000:200") == "REJECT"
    assert l3vpn_vrf_route_targets(import_rts={"65000:100"}, route_rt="65000:100", prefix="172.16.10.0/24") == (
        "IMPORT",
        "172.16.10.0/24",
    )
    assert l3vpn_vrf_route_targets(import_rts={"65000:100"}, route_rt="65000:200", prefix="172.16.10.0/24") == (
        "REJECT",
        "172.16.10.0/24",
    )

    assert evpn_type2_entry(mac="00:50:56:aa:bb:cc", ip="10.39.0.10", vni=5000) == "00:50:56:aa:bb:cc|10.39.0.10|5000"
    assert evpn_vxlan_control(mac="00:50:56:aa:bb:cc", ip="10.39.0.10", vni=5000, known_vnis={5000}) == (
        "INSTALL",
        "00:50:56:aa:bb:cc|10.39.0.10|5000",
    )
    assert evpn_vxlan_control(mac="00:50:56:aa:bb:cc", ip="10.39.0.10", vni=5001, known_vnis={5000}) == (
        "REJECT",
        "",
    )
