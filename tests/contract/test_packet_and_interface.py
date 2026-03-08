from __future__ import annotations

from routeforge.model.packet import ETHERTYPE_IPV4, EthernetFrame, IPv4Header
from routeforge.runtime.interface import Interface


def test_packet_validation_accepts_well_formed_ipv4_frame() -> None:
    frame = EthernetFrame(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=64),
    )
    assert frame.validate() == []


def test_packet_validation_rejects_bad_mac_and_ttl() -> None:
    frame = EthernetFrame(
        src_mac="xx:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=0),
    )
    errors = frame.validate()
    assert "L2_INVALID_SRC_MAC" in errors
    assert "L3_INVALID_TTL" in errors


def test_packet_validation_rejects_ttl_one() -> None:
    frame = EthernetFrame(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=1),
    )
    assert "L3_INVALID_TTL" in frame.validate()


def test_packet_validation_rejects_unsupported_but_in_range_ethertype() -> None:
    frame = EthernetFrame(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=0x86DD,
        payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=64),
    )
    assert "L2_UNSUPPORTED_ETHERTYPE" in frame.validate()


def test_packet_constructor_rejects_out_of_range_ethertype() -> None:
    try:
        EthernetFrame(
            src_mac="00:11:22:33:44:55",
            dst_mac="00:11:22:33:44:66",
            ethertype=70000,
            payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=64),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for out-of-range ethertype")


def test_packet_constructor_rejects_reserved_vlan() -> None:
    try:
        EthernetFrame(
            src_mac="00:11:22:33:44:55",
            dst_mac="00:11:22:33:44:66",
            ethertype=ETHERTYPE_IPV4,
            payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=64),
            vlan_id=4095,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for reserved vlan")


def test_interface_access_and_trunk_vlan_admission() -> None:
    access = Interface(name="eth0", mode="access", access_vlan=10)
    vlan, error = access.ingress_vlan(None)
    assert (vlan, error) == (10, None)
    tagged_vlan, tagged_error = access.ingress_vlan(10)
    assert (tagged_vlan, tagged_error) == (None, "L2_TAGGED_ON_ACCESS")

    trunk = Interface(name="eth1", mode="trunk", native_vlan=1, allowed_vlans={1, 10, 20})
    vlan, error = trunk.ingress_vlan(20)
    assert (vlan, error) == (20, None)
    vlan, error = trunk.ingress_vlan(30)
    assert (vlan, error) == (None, "L2_VLAN_NOT_ALLOWED")
