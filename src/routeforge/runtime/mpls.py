"""MPLS and overlay control plane: LDP, L3VPN, and BGP EVPN/VXLAN.

MPLS (Multi-Protocol Label Switching) and modern overlays build scalable,
multi-tenant networks on top of IP infrastructure:

- **MPLS/LDP** — Label Distribution Protocol assigns labels to FECs
  (Forwarding Equivalence Classes, typically IP prefixes).  The LFIB (Label
  Forwarding Information Base) maps incoming labels to outgoing labels + ports.
- **L3VPN** — BGP carries per-VRF (Virtual Routing and Forwarding) routes
  tagged with Route Targets (RTs).  A PE router imports routes from remote
  PEs only if the route's RT matches the VRF's import policy.
- **BGP EVPN / VXLAN** — EVPN (Ethernet VPN) uses BGP to distribute MAC/IP
  reachability across VXLAN tunnels.  Only frames destined for known VNIs
  (VXLAN Network Identifiers) are installed into the local forwarding table.
"""

from __future__ import annotations

from typing import Literal

VrfImportAction = Literal["IMPORT", "REJECT"]
EvpnAction = Literal["INSTALL", "REJECT"]


def lfib_mapping(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]:
    """Build an LFIB mapping tuple used by the forwarding pipeline.

    Returns ``(fec, local_label, outgoing_label)`` unchanged — this helper
    makes the intent explicit when constructing LFIB entries.

    # TODO(student): implement lfib_mapping.
    """
    raise NotImplementedError("TODO: implement lfib_mapping")


def vrf_import_action(*, import_rts: set[str], route_rt: str) -> VrfImportAction:
    """Compute VRF route-target import action.

    - ``route_rt in import_rts`` → ``"IMPORT"``
    - otherwise → ``"REJECT"``

    # TODO(student): implement vrf_import_action.
    """
    raise NotImplementedError("TODO: implement vrf_import_action")


def evpn_type2_entry(*, mac: str, ip: str, vni: int) -> str:
    """Build a deterministic EVPN type-2 key in ``mac|ip|vni`` format.

    Example: ``evpn_type2_entry(mac="00:50:56:aa:bb:cc", ip="10.39.0.10", vni=5000)``
    → ``"00:50:56:aa:bb:cc|10.39.0.10|5000"``

    # TODO(student): implement evpn_type2_entry.
    """
    raise NotImplementedError("TODO: implement evpn_type2_entry")


def mpls_ldp_lfib(
    *, fec: str, local_label: int, outgoing_label: int
) -> tuple[str, int, int]:
    """Return the deterministic LFIB mapping for a learned LDP label binding.

    The LFIB entry is a simple passthrough in this lab:
    return ``(fec, local_label, outgoing_label)`` unchanged.

    This models the lookup step: given a FEC (prefix) and its label pair,
    confirm the binding is installed by returning it.

    See ``docs/tutorial/lab37_mpls_ldp_label_forwarding.md``.

    # TODO(student): implement mpls_ldp_lfib.
    """
    raise NotImplementedError("TODO: implement mpls_ldp_lfib")


def l3vpn_vrf_route_targets(
    *, import_rts: set[str], route_rt: str, prefix: str
) -> tuple[str, str]:
    """Import or reject a VRF route based on Route Target policy.

    - If ``route_rt`` is in ``import_rts`` → return ``("IMPORT", prefix)``.
    - Otherwise → return ``("REJECT", prefix)``.

    Route Targets are ``"<asn>:<value>"`` strings (e.g., ``"65000:100"``).

    See ``docs/tutorial/lab38_l3vpn_vrf_and_route_targets.md``.

    # TODO(student): implement l3vpn_vrf_route_targets.
    """
    raise NotImplementedError("TODO: implement l3vpn_vrf_route_targets")


def evpn_vxlan_control(
    *, mac: str, ip: str, vni: int, known_vnis: set[int]
) -> tuple[str, str]:
    """Install an EVPN MAC/IP entry only for known VNIs.

    - If ``vni`` is in ``known_vnis`` → install the entry.
      Return ``("INSTALL", f"{mac}|{ip}|{vni}")``.
    - Otherwise → reject.
      Return ``("REJECT", "")``.

    See ``docs/tutorial/lab39_bgp_evpn_vxlan_basics.md``.

    # TODO(student): implement evpn_vxlan_control.
    """
    raise NotImplementedError("TODO: implement evpn_vxlan_control")
