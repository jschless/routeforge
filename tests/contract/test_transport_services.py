from __future__ import annotations

from routeforge.runtime.bfd import BfdSession
from routeforge.runtime.nat44 import Nat44Table
from routeforge.runtime.policy_acl import AclRule, evaluate_acl
from routeforge.runtime.qos import QosEngine
from routeforge.runtime.transport import TcpFsm, classify_flow, validate_udp


def test_transport_classification_tcp_and_udp_validation() -> None:
    flow = classify_flow(
        src_ip="198.51.100.1",
        dst_ip="203.0.113.2",
        src_port=12345,
        dst_port=443,
        protocol="tcp",
    )
    assert flow.protocol == "TCP"

    tcp = TcpFsm()
    tcp.on_event("ACTIVE_OPEN")
    assert tcp.on_event("SYN_ACK_RX") == "ESTABLISHED"
    assert validate_udp(length_bytes=64, checksum_valid=True) is True
    assert validate_udp(length_bytes=4, checksum_valid=True) is False


def test_bfd_acl_nat_qos_primitives() -> None:
    bfd = BfdSession(detect_mult=3)
    assert bfd.receive_control() == "UP"
    bfd.tick(control_received=False)
    bfd.tick(control_received=False)
    assert bfd.tick(control_received=False) == "DOWN"

    rules = [
        AclRule(action="permit", src_prefix="10.0.0.0", src_prefix_len=8),
        AclRule(action="deny", src_prefix="0.0.0.0", src_prefix_len=0),
    ]
    assert evaluate_acl(rules=rules, src_ip="10.1.1.1") == "permit"
    assert evaluate_acl(rules=rules, src_ip="198.51.100.1") == "deny"

    nat = Nat44Table(public_ip="203.0.113.254")
    session = nat.outbound_translate(inside_ip="10.0.0.10", inside_port=1111, protocol="tcp", now=0)
    assert nat.inbound_translate(outside_port=session.outside_port, protocol="tcp", now=1) is not None
    assert len(nat.expire(now=100, timeout=30)) == 1

    qos = QosEngine()
    dscp = qos.remark_dscp(traffic_class="voice")
    assert dscp == 46
    assert qos.enqueue(packet_id="pkt1", dscp=dscp) == "high"
    packet, queue = qos.dequeue()
    assert (packet, queue) == ("pkt1", "high")
