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
    if re.match(MAC_RE, normalize_mac(value)):
        return True
    return False


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
            errs.append("L3_INVALID_SRC_IP")
        try:
            ipaddress.IPv4Address(self.dst_ip)
        except Exception:
            errs.append("L3_INVALID_DST_IP")
        if self.ttl <= 1:
            errs.append("L3_INVALID_TTL")
        return errs


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
        # L2_INVALID_SRC_MAC, L2_INVALID_DST_MAC, L2_UNSUPPORTED_ETHERTYPE, L2_INVALID_VLAN, L3_INVALID_SRC_IP, L3_INVALID_DST_IP, L3_INVALID_TTL.
        errs = []
        if not is_valid_mac(self.src_mac):
            errs.append("L2_INVALID_SRC_MAC")
        if not is_valid_mac(self.dst_mac):
            errs.append("L2_INVALID_DST_MAC")
        # BUG(student): operator precedence error — parses as `(not (ethertype >= 0)) and ethertype < 65536`.
        # This only rejects negative values; ethertypes >= 65536 pass silently.
        # TODO(student): fix to `if not (0 <= self.ethertype < 65536):` to enforce the full valid range.
        if not self.ethertype >= 0 and self.ethertype < 65536:
            errs.append("L2_UNSUPPORTED_ETHERTYPE")
        if not len(self.payload.validate()) == 0:
            for err in self.payload.validate():
                errs.append(err)
        if self.vlan_id is not None and (self.vlan_id <= 0 or self.vlan_id > 4094):
            errs.append("L2_INVALID_VLAN")
        return errs
