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
    """Learn a DHCP snooping binding only on trusted ingress when no binding exists yet.

    - ``trusted_port=False`` → return ``binding`` unchanged (never learn on untrusted).
    - ``trusted_port=True, binding is not None`` → return ``binding`` unchanged (already learned).
    - ``trusted_port=True, binding is None`` → create and return a new
      ``DhcpBinding(mac=arp_mac, ip=arp_ip, vlan=default_vlan)``.

    # TODO(student): implement learn_binding_if_trusted.
    """
    raise NotImplementedError("TODO: implement learn_binding_if_trusted")


def update_secure_mac_table(
    *,
    max_macs: int,
    learned_macs: tuple[str, ...],
    source_mac: str,
) -> tuple[tuple[str, ...], bool]:
    """Update the secure-MAC learning table and report capacity violations.

    Steps:
    1. If ``source_mac`` is already in ``learned_macs`` → return ``(learned_macs, False)``.
    2. If ``len(learned_macs) >= max_macs`` → return ``(learned_macs, True)`` (violation).
    3. Otherwise → return ``(learned_macs + (source_mac,), False)``.

    # TODO(student): implement update_secure_mac_table.
    """
    raise NotImplementedError("TODO: implement update_secure_mac_table")


def dhcp_snooping_dai(
    *,
    trusted_port: bool,
    binding: DhcpBinding | None,
    arp_mac: str,
    arp_ip: str,
) -> tuple[DhcpBinding | None, str]:
    """Learn DHCP bindings and enforce DAI on untrusted ports.

    Behavior:
    - **Trusted port** (``trusted_port=True``): always ALLOW, and if no
      binding exists yet, create one from the ARP fields with ``vlan=10``
      (the lab's default management VLAN).  Return ``(new_binding, "ALLOW")``.
    - **Untrusted port, no binding** (``binding=None``): no entry to validate
      against; return ``(None, "DROP")``.
    - **Untrusted port, binding present**: compare ``arp_mac`` against
      ``binding.mac``.  If they match return ``(binding, "ALLOW")``;
      if not return ``(binding, "DROP")``.

    Return tuple: ``(learned_or_existing_binding | None, "ALLOW" | "DROP")``.

    See ``docs/tutorial/lab28_dhcp_snooping_and_dai.md`` for the walkthrough.

    # TODO(student): implement dhcp_snooping_dai using the rules above.
    """
    raise NotImplementedError("TODO: implement dhcp_snooping_dai")


def port_security_ip_source_guard(
    *,
    max_macs: int,
    learned_macs: tuple[str, ...],
    source_mac: str,
    source_ip_allowed: bool,
) -> tuple[tuple[str, ...], str]:
    """Enforce per-port MAC limits and IP source guard policy.

    Steps (apply in order):

    1. If ``source_mac`` is already in ``learned_macs``:
       - If ``source_ip_allowed`` is False: return ``(learned_macs, "IPSG_DENY")``.
       - Otherwise: return ``(learned_macs, "ALLOW")``.

    2. If ``len(learned_macs) >= max_macs``:
       return ``(learned_macs, "PORTSEC_VIOLATION")`` — cannot learn a new MAC.

    3. Learn the new MAC: new_macs = learned_macs + (source_mac,).
       - If ``source_ip_allowed`` is False: return ``(new_macs, "IPSG_DENY")``.
       - Otherwise: return ``(new_macs, "ALLOW")``.

    See ``docs/tutorial/lab29_port_security_and_ip_source_guard.md``.

    # TODO(student): implement port_security_ip_source_guard using the steps above.
    """
    raise NotImplementedError("TODO: implement port_security_ip_source_guard")
