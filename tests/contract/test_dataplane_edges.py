from __future__ import annotations

from routeforge.model.packet import ETHERTYPE_IPV4, EthernetFrame, IPv4Header
from routeforge.runtime.dataplane_sim import DataplaneSim
from routeforge.runtime.interface import Interface
from routeforge.runtime.router import Router


def _frame(*, src_mac: str, dst_mac: str, vlan_id: int | None = None) -> EthernetFrame:
    return EthernetFrame(
        src_mac=src_mac,
        dst_mac=dst_mac,
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=64),
        vlan_id=vlan_id,
    )


def test_dataplane_unknown_ingress_interface_drops() -> None:
    router = Router(node_id="R1")
    router.add_interface(Interface(name="eth0", mode="access", access_vlan=1))
    sim = DataplaneSim(router)

    outcome = sim.process_frame(ingress_interface="eth99", frame=_frame(src_mac="00:11:22:33:44:55", dst_mac="00:11:22:33:44:66"))

    assert outcome.action == "DROP"
    assert outcome.reason == "L2_UNKNOWN_INGRESS_IF"
    assert outcome.checkpoints == ("PARSE_DROP",)


def test_dataplane_same_port_destination_drops() -> None:
    router = Router(node_id="R1")
    router.add_interface(Interface(name="eth0", mode="access", access_vlan=1))
    router.add_interface(Interface(name="eth1", mode="access", access_vlan=1))
    sim = DataplaneSim(router)

    # Learn host A on eth0.
    sim.process_frame(ingress_interface="eth0", frame=_frame(src_mac="00:aa:00:00:00:01", dst_mac="00:bb:00:00:00:01"))
    # Now traffic from eth0 to host A should drop due to same-port destination.
    outcome = sim.process_frame(ingress_interface="eth0", frame=_frame(src_mac="00:cc:00:00:00:01", dst_mac="00:aa:00:00:00:01"))

    assert outcome.action == "DROP"
    assert outcome.reason == "L2_SAME_PORT_DESTINATION"
    assert "PARSE_DROP" in outcome.checkpoints


def test_dataplane_no_eligible_egress_drops() -> None:
    router = Router(node_id="R1")
    router.add_interface(Interface(name="eth0", mode="access", access_vlan=10))
    router.add_interface(Interface(name="eth1", mode="access", access_vlan=20))
    sim = DataplaneSim(router)

    outcome = sim.process_frame(ingress_interface="eth0", frame=_frame(src_mac="00:10:00:00:00:01", dst_mac="00:10:00:00:00:ff"))

    assert outcome.action == "DROP"
    assert outcome.reason == "L2_NO_ELIGIBLE_EGRESS"
    assert "L2_FLOOD" in outcome.checkpoints
    assert "PARSE_DROP" in outcome.checkpoints


def test_dataplane_native_vlan_to_native_vlan_has_no_tag_translation_checkpoints() -> None:
    router = Router(node_id="R1")
    router.add_interface(Interface(name="eth0", mode="trunk", native_vlan=1, allowed_vlans={1}))
    router.add_interface(Interface(name="eth1", mode="trunk", native_vlan=1, allowed_vlans={1}))
    sim = DataplaneSim(router)

    outcome = sim.process_frame(
        ingress_interface="eth0",
        frame=_frame(src_mac="00:11:22:33:44:55", dst_mac="00:aa:bb:cc:dd:ee", vlan_id=None),
    )

    assert outcome.action == "FLOOD"
    assert "VLAN_TAG_PUSH" not in outcome.checkpoints
    assert "VLAN_TAG_POP" not in outcome.checkpoints
