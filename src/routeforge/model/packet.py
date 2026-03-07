"""Minimal frame/packet model used by the first labs."""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Address
import re

MAC_RE = re.compile(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$")
ETHERTYPE_IPV4 = 0x0800
BROADCAST_MAC = "ff:ff:ff:ff:ff:ff"


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
        errors: list[str] = []
        try:
            IPv4Address(self.src_ip)
        except ValueError:
            errors.append("L3_INVALID_SRC_IP")
        try:
            IPv4Address(self.dst_ip)
        except ValueError:
            errors.append("L3_INVALID_DST_IP")
        if self.ttl < 1:
            errors.append("L3_INVALID_TTL")
        return errors


@dataclass(frozen=True)
class EthernetFrame:
    src_mac: str
    dst_mac: str
    ethertype: int
    payload: IPv4Header
    vlan_id: int | None = None

    def normalized(self) -> EthernetFrame:
        return EthernetFrame(
            src_mac=normalize_mac(self.src_mac),
            dst_mac=normalize_mac(self.dst_mac),
            ethertype=self.ethertype,
            payload=self.payload,
            vlan_id=self.vlan_id,
        )

    def validate(self) -> list[str]:
        frame = self.normalized()
        errors: list[str] = []

        if not is_valid_mac(frame.src_mac):
            errors.append("L2_INVALID_SRC_MAC")
        if not is_valid_mac(frame.dst_mac):
            errors.append("L2_INVALID_DST_MAC")

        if frame.ethertype != ETHERTYPE_IPV4:
            errors.append("L2_UNSUPPORTED_ETHERTYPE")

        if frame.vlan_id is not None and frame.vlan_id < 1:
            errors.append("L2_INVALID_VLAN")

        errors.extend(frame.payload.validate())
        return errors
