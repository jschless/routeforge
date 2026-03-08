"""Minimal frame/packet model used by the first labs."""

from __future__ import annotations

from dataclasses import dataclass
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
        import ipaddress

        errs = []
        try:
            ipaddress.IPv4Address(self.src_ip)
        except Exception:
            errs.append(L3_INVALID_SRC_IP)
        try:
            ipaddress.IPv4Address(self.dst_ip)
        except Exception:
            errs.append(L3_INVALID_DST_IP)
        if self.ttl <= 1:
            errs.append(L3_INVALID_TTL)
        return errs


@dataclass(frozen=True)
class EthernetFrame:
    src_mac: str
    dst_mac: str
    ethertype: int
    payload: IPv4Header
    vlan_id: int | None = None

    def __post_init__(self) -> None:
        # TODO(student): enforce ethertype and VLAN structural ranges at construction time.
        # Desired end state:
        #   - ethertype must be an int in range 0..65535
        #   - vlan_id must be None or an int in range 1..4094
        return None

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
        # L2_INVALID_SRC_MAC, L2_INVALID_DST_MAC, L2_UNSUPPORTED_ETHERTYPE, L2_INVALID_VLAN,
        # L3_INVALID_SRC_IP, L3_INVALID_DST_IP, L3_INVALID_TTL.
        errs = []
        if not is_valid_mac(self.src_mac):
            errs.append(L2_INVALID_SRC_MAC)
        if not is_valid_mac(self.dst_mac):
            errs.append(L2_INVALID_DST_MAC)
        # BUG(student): operator precedence error - parses as `(not (ethertype >= 0)) and ethertype < 65536`.
        # This only rejects negative values; ethertypes >= 65536 pass silently.
        # TODO(student): fix to `if not (0 <= self.ethertype < 65536):` and separate structural range
        # validation from semantic unsupported-protocol checks.
        if not self.ethertype >= 0 and self.ethertype < 65536:
            errs.append(L2_UNSUPPORTED_ETHERTYPE)
        if self.payload.validate():
            errs.extend(self.payload.validate())
        if self.vlan_id is not None and (self.vlan_id <= 0 or self.vlan_id > 4094):
            errs.append(L2_INVALID_VLAN)
        return errs
