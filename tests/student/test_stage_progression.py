from __future__ import annotations

import pytest

from routeforge.labs.conformance import load_conformance_matrix
from routeforge.labs.exercises import run_lab
from routeforge.labs.manifest import LABS
from routeforge.model.packet import ETHERTYPE_IPV4, EthernetFrame, IPv4Header, is_valid_mac
from routeforge.runtime.adjacency import ArpAdjacencyTable
from routeforge.runtime.dataplane_sim import DataplaneSim
from routeforge.runtime.interface import Interface
from routeforge.runtime.observability import emit_telemetry, readiness_check
from routeforge.runtime.ospf import DrCandidate, _election_order, failover_dr_bdr
from routeforge.runtime.phase2 import (
    MpbgpPath,
    apply_policer,
    build_redistribution_tag,
    derive_slaac_host_id,
    dhcp_snooping_dai,
    evpn_type2_entry,
    evpn_vxlan_control,
    fhrp_track_failover,
    ipv6_nd_slaac_ra_guard,
    l3vpn_vrf_route_targets,
    learn_binding_if_trusted,
    lfib_mapping,
    mpls_ldp_lfib,
    mpbgp_ipv6_unicast,
    ospfv3_adjacency_lsdb,
    ospfv3_neighbor_result,
    port_security_ip_source_guard,
    qos_police_shape,
    qos_wred_decision,
    rank_mpbgp_path,
    redistribute_with_loop_guard,
    tracked_object_result,
    update_secure_mac_table,
    vrf_import_action,
    wred_decision_profile,
)
from routeforge.runtime.router import Router
from routeforge.runtime.stp import (
    Bridge,
    BridgeID,
    Link,
    PortRef,
    bpdu_guard_decision,
    compute_stp,
    remove_link,
    role_changes,
)
from routeforge.runtime.transport import classify_flow, validate_udp


def _required_checkpoints_for_lab(lab_id: str) -> set[str]:
    matrix = load_conformance_matrix()
    coverage = matrix.coverage_for_lab(lab_id)
    assert coverage is not None
    required: set[str] = set()
    for feature_id in coverage.must:
        required.update(matrix.features_by_id[feature_id].checkpoints)
    return required


def _assert_stage_lab(lab_id: str) -> None:
    result = run_lab(lab_id)
    assert result.passed is True
    assert _required_checkpoints_for_lab(lab_id) <= set(result.checkpoints)


@pytest.mark.stage(1)
def test_stage01_edge_mac_and_ipv4_validation() -> None:
    assert is_valid_mac("aa:bb:cc:dd:ee:ff") is True
    assert is_valid_mac("AA:BB:CC:DD:EE:FF") is True
    assert is_valid_mac("zz:bb:cc:dd:ee:ff") is False

    valid = EthernetFrame(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=64),
    )
    assert valid.validate() == []

    invalid = EthernetFrame(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.1", dst_ip="999.0.2.2", ttl=0),
    )
    errors = invalid.validate()
    assert "L3_INVALID_DST_IP" in errors
    assert "L3_INVALID_TTL" in errors


@pytest.mark.stage(2)
def test_stage02_forwarding_plan_decisions() -> None:
    router = Router(node_id="R1")
    router.add_interface(Interface(name="eth0", mode="access", access_vlan=1))
    router.add_interface(Interface(name="eth1", mode="access", access_vlan=1))
    router.add_interface(Interface(name="eth2", mode="access", access_vlan=1))
    sim = DataplaneSim(router)

    unknown = sim._determine_forwarding_plan(
        ingress_interface="eth0",
        ingress_vlan=1,
        destination_mac="00:bb:00:00:00:01",
    )
    assert unknown.action == "FLOOD"
    assert unknown.reason == "L2_UNKNOWN_UNICAST_FLOOD"
    assert unknown.checkpoint == "L2_FLOOD"
    assert set(unknown.egress_ports) == {"eth1", "eth2"}

    router.learn_mac(vlan=1, mac="00:cc:00:00:00:01", interface_name="eth1")
    known = sim._determine_forwarding_plan(
        ingress_interface="eth0",
        ingress_vlan=1,
        destination_mac="00:cc:00:00:00:01",
    )
    assert known.action == "FORWARD"
    assert known.reason == "L2_FDB_HIT"
    assert known.checkpoint == "L2_UNICAST_FORWARD"
    assert known.egress_ports == ("eth1",)

    same_port = sim._determine_forwarding_plan(
        ingress_interface="eth1",
        ingress_vlan=1,
        destination_mac="00:cc:00:00:00:01",
    )
    assert same_port.action == "DROP"
    assert same_port.reason == "L2_SAME_PORT_DESTINATION"
    assert same_port.checkpoint == "PARSE_DROP"


@pytest.mark.stage(3)
def test_stage03_egress_vlan_plan_decisions() -> None:
    router = Router(node_id="R1")
    router.add_interface(Interface(name="eth0", mode="access", access_vlan=10))
    router.add_interface(Interface(name="eth1", mode="trunk", native_vlan=1, allowed_vlans={1, 10, 20}))
    router.add_interface(Interface(name="eth2", mode="access", access_vlan=20))
    sim = DataplaneSim(router)

    push = sim._determine_egress_vlan_plan(
        ingress_vlan=10,
        ingress_tag=None,
        egress_port_name="eth1",
    )
    assert push.allowed is True
    assert push.egress_vlan_id == 10
    assert push.checkpoint == "VLAN_TAG_PUSH"

    pop = sim._determine_egress_vlan_plan(
        ingress_vlan=20,
        ingress_tag=20,
        egress_port_name="eth2",
    )
    assert pop.allowed is True
    assert pop.egress_vlan_id is None
    assert pop.checkpoint == "VLAN_TAG_POP"

    deny = sim._determine_egress_vlan_plan(
        ingress_vlan=20,
        ingress_tag=20,
        egress_port_name="eth0",
    )
    assert deny.allowed is False


@pytest.mark.stage(5)
def test_stage05_stp_role_changes_and_bpdu_guard() -> None:
    bridges = [
        Bridge(node_id="S1", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:01")),
        Bridge(node_id="S2", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:02")),
        Bridge(node_id="S3", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:03")),
    ]
    links = [
        Link(a=PortRef("S1", "Gi0/1"), b=PortRef("S2", "Gi0/1"), cost=4),
        Link(a=PortRef("S1", "Gi0/2"), b=PortRef("S3", "Gi0/1"), cost=4),
        Link(a=PortRef("S2", "Gi0/2"), b=PortRef("S3", "Gi0/2"), cost=4),
    ]
    before = compute_stp(bridges, links)
    after = compute_stp(bridges, remove_link(links, a=("S1", "Gi0/2"), b=("S3", "Gi0/1")))

    changes = role_changes(before, after)
    assert changes
    assert ("S3", "Gi0/1") in changes

    tripped = bpdu_guard_decision(port=("S2", "Gi0/10"), edge_port=True, bpdu_received=True)
    assert tripped.action == "ERRDISABLE"
    assert tripped.reason == "STP_BPDU_GUARD_TRIPPED"

    clear = bpdu_guard_decision(port=("S2", "Gi0/10"), edge_port=False, bpdu_received=True)
    assert clear.action == "FORWARD"
    assert clear.reason == "STP_GUARD_CLEAR"


@pytest.mark.stage(6)
def test_stage06_arp_queue_and_resolve() -> None:
    table = ArpAdjacencyTable()
    assert table.queue_packet(next_hop_ip="192.0.2.1", packet_id="pkt-1") is True
    assert table.queue_packet(next_hop_ip="192.0.2.1", packet_id="pkt-2") is False
    released = table.resolve(next_hop_ip="192.0.2.1", mac="00:de:ad:be:ef:01")
    assert released == ["pkt-1", "pkt-2"]
    assert table.lookup("192.0.2.1") == "00:de:ad:be:ef:01"


@pytest.mark.stage(12)
def test_stage12_ospf_election_order_and_failover() -> None:
    candidates = [
        DrCandidate(router_id="1.1.1.1", priority=90),
        DrCandidate(router_id="2.2.2.2", priority=100),
        DrCandidate(router_id="3.3.3.3", priority=100),
    ]
    ordered = _election_order(candidates)
    assert [candidate.router_id for candidate in ordered] == ["3.3.3.3", "2.2.2.2", "1.1.1.1"]

    dr, bdr = failover_dr_bdr(candidates, active_router_ids={"1.1.1.1", "3.3.3.3"})
    assert dr == "3.3.3.3"
    assert bdr == "1.1.1.1"


@pytest.mark.stage(16)
def test_stage16_classify_flow_and_validate_udp() -> None:
    flow = classify_flow(
        src_ip="198.51.100.10",
        dst_ip="203.0.113.20",
        src_port=40000,
        dst_port=53,
        protocol="udp",
    )
    assert flow.protocol == "UDP"
    assert flow.src_port == 40000
    assert flow.dst_port == 53

    assert validate_udp(length_bytes=8, checksum_valid=True) is True
    assert validate_udp(length_bytes=7, checksum_valid=True) is False
    assert validate_udp(length_bytes=8, checksum_valid=False) is False


@pytest.mark.stage(26)
def test_stage26_readiness_and_telemetry() -> None:
    readiness = readiness_check(checks={"bgp": True, "isis": False, "nve": True})
    assert readiness.ready is False
    assert readiness.failed_checks == ("isis",)

    telemetry = emit_telemetry(
        component="edge-1",
        counters={"drops": 5, "forwarded": 200},
        timestamp_s=1700000000,
    )
    assert telemetry["component"] == "edge-1"
    assert list(telemetry["counters"].keys()) == ["drops", "forwarded"]


@pytest.mark.stage(28)
def test_stage28_dhcp_binding_and_dai() -> None:
    learned = learn_binding_if_trusted(
        trusted_port=True,
        binding=None,
        arp_mac="00:aa:00:00:00:01",
        arp_ip="10.10.10.10",
    )
    assert learned is not None
    assert learned.vlan == 10

    _, action = dhcp_snooping_dai(
        trusted_port=False,
        binding=learned,
        arp_mac="00:aa:00:00:00:01",
        arp_ip="10.10.10.10",
    )
    assert action == "ALLOW"


@pytest.mark.stage(29)
def test_stage29_port_security_and_ipsg() -> None:
    learned, violated = update_secure_mac_table(
        max_macs=1,
        learned_macs=(),
        source_mac="00:11:22:33:44:55",
    )
    assert violated is False
    assert learned == ("00:11:22:33:44:55",)

    _, action = port_security_ip_source_guard(
        max_macs=1,
        learned_macs=learned,
        source_mac="00:11:22:33:44:66",
        source_ip_allowed=True,
    )
    assert action == "PORTSEC_VIOLATION"


@pytest.mark.stage(30)
def test_stage30_policing_and_shaping() -> None:
    assert apply_policer(offered_kbps=2000, cir_kbps=1500) == 1500
    admitted, released = qos_police_shape(offered_kbps=2000, cir_kbps=1500, shape_rate_kbps=1200)
    assert admitted == 1500
    assert released == 1200


@pytest.mark.stage(31)
def test_stage31_wred_profile_and_decision() -> None:
    assert wred_decision_profile(queue_depth=60, min_threshold=50, max_threshold=100) == "BETWEEN_THRESHOLDS"
    assert qos_wred_decision(queue_depth=60, min_threshold=50, max_threshold=100, ecn_capable=True) == "MARK"
    assert qos_wred_decision(queue_depth=120, min_threshold=50, max_threshold=100, ecn_capable=True) == "DROP"


@pytest.mark.stage(32)
def test_stage32_redistribution_loop_guard() -> None:
    tag = build_redistribution_tag(source_prefix="10.40.0.0/16", source_protocol="ospf")
    assert tag == "OSPF:10.40.0.0/16"

    tags, action = redistribute_with_loop_guard(
        source_prefix="10.40.0.0/16",
        source_protocol="OSPF",
        existing_tags=set(),
    )
    assert action == "IMPORT"
    assert tag in tags


@pytest.mark.stage(33)
def test_stage33_fhrp_track_state() -> None:
    assert tracked_object_result(tracked_object_up=True) == "UP"
    assert tracked_object_result(tracked_object_up=False) == "DOWN"
    assert fhrp_track_failover(active_router="R1", standby_router="R2", tracked_object_up=False) == "R2"


@pytest.mark.stage(34)
def test_stage34_ipv6_ra_guard_and_slaac() -> None:
    assert derive_slaac_host_id(source_link_local="fe80::10") == "10"
    action, address = ipv6_nd_slaac_ra_guard(
        ra_trusted=True,
        source_link_local="fe80::10",
        prefix="2001:db8:100::",
    )
    assert action == "ALLOW"
    assert address == "2001:db8:100::10"


@pytest.mark.stage(35)
def test_stage35_ospfv3_state_and_lsdb() -> None:
    assert ospfv3_neighbor_result(hello_ok=False) == "DOWN"
    state, lsdb = ospfv3_adjacency_lsdb(hello_ok=True, lsa_id="lsa-1", lsdb=set())
    assert state == "FULL"
    assert lsdb == {"lsa-1"}


@pytest.mark.stage(36)
def test_stage36_mpbgp_rank_and_select() -> None:
    path = MpbgpPath(prefix="2001:db8:1::/64", local_pref=150, as_path_len=3, next_hop="2001:db8::2")
    assert rank_mpbgp_path(path) == (-150, 3, "2001:db8::2")
    best = mpbgp_ipv6_unicast(
        [
            path,
            MpbgpPath(prefix="2001:db8:1::/64", local_pref=200, as_path_len=5, next_hop="2001:db8::4"),
        ]
    )
    assert best.next_hop == "2001:db8::4"


@pytest.mark.stage(37)
def test_stage37_lfib_mapping() -> None:
    assert lfib_mapping(fec="10.70.0.0/16", local_label=16001, outgoing_label=24001) == ("10.70.0.0/16", 16001, 24001)
    assert mpls_ldp_lfib(fec="10.70.0.0/16", local_label=16001, outgoing_label=24001) == ("10.70.0.0/16", 16001, 24001)


@pytest.mark.stage(38)
def test_stage38_vrf_import_action() -> None:
    assert vrf_import_action(import_rts={"65000:100"}, route_rt="65000:100") == "IMPORT"
    assert l3vpn_vrf_route_targets(import_rts={"65000:100"}, route_rt="65000:200", prefix="172.16.10.0/24") == (
        "REJECT",
        "172.16.10.0/24",
    )


@pytest.mark.stage(39)
def test_stage39_evpn_entry_and_control() -> None:
    assert evpn_type2_entry(mac="00:50:56:aa:bb:cc", ip="10.39.0.10", vni=5000) == "00:50:56:aa:bb:cc|10.39.0.10|5000"
    assert evpn_vxlan_control(mac="00:50:56:aa:bb:cc", ip="10.39.0.10", vni=5000, known_vnis={5000}) == (
        "INSTALL",
        "00:50:56:aa:bb:cc|10.39.0.10|5000",
    )


@pytest.mark.parametrize(
    ("stage", "lab_id"),
    [
        pytest.param(index, entry["id"], marks=pytest.mark.stage(index), id=f"stage{index:02d}_{entry['id']}")
        for index, entry in enumerate(LABS, start=1)
    ],
)
def test_stage_lab(stage: int, lab_id: str) -> None:
    _assert_stage_lab(lab_id)
