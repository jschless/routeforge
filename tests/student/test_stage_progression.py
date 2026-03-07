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


@pytest.mark.parametrize(
    ("stage", "lab_id"),
    [
        pytest.param(index, entry["id"], marks=pytest.mark.stage(index), id=f"stage{index:02d}_{entry['id']}")
        for index, entry in enumerate(LABS, start=1)
    ],
)
def test_stage_lab(stage: int, lab_id: str) -> None:
    _assert_stage_lab(lab_id)
