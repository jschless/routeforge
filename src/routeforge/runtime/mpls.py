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

from typing import Literal, TypeAlias

VrfImportAction: TypeAlias = Literal["IMPORT", "REJECT"]
EvpnAction: TypeAlias = Literal["INSTALL", "REJECT"]


def lfib_mapping(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]:
    """Build LFIB mapping tuple used by forwarding pipeline."""
    return (fec, local_label, outgoing_label)


def mpls_ldp_lfib(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]:
    """Return deterministic LFIB tuple (FEC, local, outgoing labels)."""
    return lfib_mapping(fec=fec, local_label=local_label, outgoing_label=outgoing_label)


def vrf_import_action(*, import_rts: set[str], route_rt: str) -> VrfImportAction:
    """Compute VRF route-target import action."""
    return "IMPORT" if route_rt in import_rts else "REJECT"


def l3vpn_vrf_route_targets(
    *, import_rts: set[str], route_rt: str, prefix: str
) -> tuple[VrfImportAction, str]:
    """Return IMPORT/REJECT with original prefix based on RT membership."""
    if vrf_import_action(import_rts=import_rts, route_rt=route_rt) == "IMPORT":
        return "IMPORT", prefix
    return "REJECT", prefix


def evpn_type2_entry(*, mac: str, ip: str, vni: int) -> str:
    """Build deterministic EVPN type-2 key."""
    return f"{mac}|{ip}|{vni}"


def evpn_vxlan_control(
    *, mac: str, ip: str, vni: int, known_vnis: set[int]
) -> tuple[EvpnAction, str]:
    """Install EVPN type-2 tuple only for configured VNIs."""
    if vni not in known_vnis:
        return "REJECT", ""
    return "INSTALL", evpn_type2_entry(mac=mac, ip=ip, vni=vni)
