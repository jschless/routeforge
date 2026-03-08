"""Layer 2 security features: DHCP Snooping, DAI, and IP Source Guard.

These mechanisms protect the network from spoofing and rogue devices at the
access layer:

- **DHCP Snooping** — intercepts DHCP traffic to build an authoritative
  binding table (MAC → IP → VLAN) and blocks DHCP server messages on
  untrusted ports.
- **Dynamic ARP Inspection (DAI)** — validates ARP packets against the DHCP
  snooping binding table; drops ARPs that don't match a known binding on
  untrusted ports to prevent ARP poisoning.
- **IP Source Guard** — enforces that the source MAC and source IP of frames
  arriving on a port match the learned or configured bindings, preventing IP
  spoofing.
- **Port Security** — limits the number of MAC addresses that can be learned
  on a port; exceeding the limit triggers a violation action.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

DaiAction: TypeAlias = Literal["ALLOW", "DROP"]
PortSecurityAction: TypeAlias = Literal["ALLOW", "PORTSEC_VIOLATION", "IPSG_DENY"]


@dataclass(frozen=True)
class DhcpBinding:
    """A DHCP snooping binding entry mapping a MAC address to an IP on a VLAN."""

    mac: str
    ip: str
    vlan: int


def learn_binding_if_trusted(
    *,
    trusted_port: bool,
    binding: DhcpBinding | None,
    arp_mac: str,
    arp_ip: str,
    default_vlan: int = 10,
) -> DhcpBinding | None:
    """Learn a binding only on trusted ingress when no binding exists yet."""
    if trusted_port and binding is None:
        return DhcpBinding(mac=arp_mac, ip=arp_ip, vlan=default_vlan)
    return binding


def dhcp_snooping_dai(
    *,
    trusted_port: bool,
    binding: DhcpBinding | None,
    arp_mac: str,
    arp_ip: str,
) -> tuple[DhcpBinding | None, DaiAction]:
    """Return ALLOW/DROP after binding learn + ARP binding validation."""
    learned = learn_binding_if_trusted(
        trusted_port=trusted_port,
        binding=binding,
        arp_mac=arp_mac,
        arp_ip=arp_ip,
    )
    if learned is None:
        return learned, "DROP"
    if learned.mac == arp_mac and learned.ip == arp_ip:
        return learned, "ALLOW"
    return learned, "DROP"


def update_secure_mac_table(
    *,
    max_macs: int,
    learned_macs: tuple[str, ...],
    source_mac: str,
) -> tuple[tuple[str, ...], bool]:
    """Update learned MACs deterministically; bool indicates capacity violation."""
    if source_mac in learned_macs:
        return learned_macs, False
    if len(learned_macs) >= max_macs:
        return learned_macs, True
    return tuple(sorted((*learned_macs, source_mac))), False


def port_security_ip_source_guard(
    *,
    max_macs: int,
    learned_macs: tuple[str, ...],
    source_mac: str,
    source_ip_allowed: bool,
) -> tuple[tuple[str, ...], PortSecurityAction]:
    """Apply port-security learning first, then IP source guard decision."""
    updated, violated = update_secure_mac_table(
        max_macs=max_macs,
        learned_macs=learned_macs,
        source_mac=source_mac,
    )
    if violated:
        return learned_macs, "PORTSEC_VIOLATION"
    if not source_ip_allowed:
        return updated, "IPSG_DENY"
    return updated, "ALLOW"
