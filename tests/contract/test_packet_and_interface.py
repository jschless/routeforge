from __future__ import annotations

import pytest

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


# Note: ``EthernetFrame`` contains an intentional student bug around ethertype
# range validation. Try ``ethertype=70000`` and verify constructor behavior.
@pytest.mark.xfail(reason="intentional student bug — fix ethertype validator in packet.py")
def test_ethertype_bug_is_present() -> None:
    with pytest.raises(ValueError):
        EthernetFrame(
            src_mac="00:11:22:33:44:55",
            dst_mac="00:11:22:33:44:66",
            ethertype=70000,
            payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=64),
        )


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
