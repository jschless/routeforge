"""Minimal frame/packet model used by the first labs."""

from __future__ import annotations

from dataclasses import dataclass
import re

MAC_RE = re.compile(r"^[0-9a-f]{2}(:[0-9a-f]{2}){5}$")
ETHERTYPE_IPV4 = 0x0800
BROADCAST_MAC = "ff:ff:ff:ff:ff:ff"


def normalize_mac(value: str) -> str:
    return value.strip().lower()


def is_valid_mac(value: str) -> bool:
    # TODO(student): return True only for valid colon-delimited MAC addresses.
    raise NotImplementedError("TODO: implement is_valid_mac")


@dataclass(frozen=True)
class IPv4Header:
    src_ip: str
    dst_ip: str
    ttl: int = 64

    def validate(self) -> list[str]:
        # TODO(student): validate src_ip, dst_ip, and ttl. Return error codes.
        raise NotImplementedError("TODO: implement IPv4Header.validate")


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
        # TODO(student): validate L2 MACs/ethertype/VLAN and extend with payload errors.
        raise NotImplementedError("TODO: implement EthernetFrame.validate")
