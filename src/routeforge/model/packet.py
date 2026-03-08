"""Minimal frame/packet model used by the first labs."""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Address
import re

MAC_RE = re.compile(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$")
ETHERTYPE_IPV4 = 0x0800
BROADCAST_MAC = "ff:ff:ff:ff:ff:ff"

# Lab 01 validation codes. Keep these as exact string contracts.
L2_INVALID_SRC_MAC = "L2_INVALID_SRC_MAC"
L2_INVALID_DST_MAC = "L2_INVALID_DST_MAC"
L2_UNSUPPORTED_ETHERTYPE = "L2_UNSUPPORTED_ETHERTYPE"
L2_INVALID_VLAN = "L2_INVALID_VLAN"
L3_INVALID_SRC_IP = "L3_INVALID_SRC_IP"
L3_INVALID_DST_IP = "L3_INVALID_DST_IP"
L3_INVALID_TTL = "L3_INVALID_TTL"


def normalize_mac(value: str) -> str:
    return value.strip().lower()


def is_valid_mac(value: str) -> bool:
    return bool(MAC_RE.match(normalize_mac(value)))


@dataclass(frozen=True)
class IPv4Header:
    src_ip: str
    dst_ip: str
    ttl: int = 64

    def validate(self) -> list[str]:
        """Return zero or more L3 error codes from the module-level Lab 01 contract."""
        errors: list[str] = []
        try:
            IPv4Address(self.src_ip)
        except ValueError:
            errors.append(L3_INVALID_SRC_IP)
        try:
            IPv4Address(self.dst_ip)
        except ValueError:
            errors.append(L3_INVALID_DST_IP)
        if self.ttl <= 1:
            errors.append(L3_INVALID_TTL)
        return errors


@dataclass(frozen=True)
class EthernetFrame:
    src_mac: str
    dst_mac: str
    ethertype: int
    payload: IPv4Header
    vlan_id: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.ethertype, int) or isinstance(self.ethertype, bool):
            raise ValueError("ethertype must be an int in range 0..65535")
        if not 0 <= self.ethertype <= 65535:
            raise ValueError("ethertype must be in range 0..65535")
        if self.vlan_id is not None:
            if not isinstance(self.vlan_id, int) or isinstance(self.vlan_id, bool):
                raise ValueError("vlan_id must be None or an int in range 1..4094")
            if not 1 <= self.vlan_id <= 4094:
                raise ValueError("vlan_id must be None or in range 1..4094")

    def normalized(self) -> EthernetFrame:
        return EthernetFrame(
            src_mac=normalize_mac(self.src_mac),
            dst_mac=normalize_mac(self.dst_mac),
            ethertype=self.ethertype,
            payload=self.payload,
            vlan_id=self.vlan_id,
        )

    def validate(self) -> list[str]:
        """Return zero or more L2/L3 error codes from the module-level Lab 01 contract."""
        frame = self.normalized()
        errors: list[str] = []

        if not is_valid_mac(frame.src_mac):
            errors.append(L2_INVALID_SRC_MAC)
        if not is_valid_mac(frame.dst_mac):
            errors.append(L2_INVALID_DST_MAC)

        if frame.ethertype != ETHERTYPE_IPV4:
            errors.append(L2_UNSUPPORTED_ETHERTYPE)

        errors.extend(frame.payload.validate())
        return errors
