"""Phase 2 deterministic helpers for security, IPv6, MPLS, and EVPN labs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, TypeAlias

DaiAction: TypeAlias = Literal["ALLOW", "DROP"]
PortSecurityAction: TypeAlias = Literal["ALLOW", "PORTSEC_VIOLATION", "IPSG_DENY"]
WredAction: TypeAlias = Literal["FORWARD", "MARK", "DROP"]
RedistributionAction: TypeAlias = Literal["IMPORT", "LOOP_SUPPRESS"]
TrackState: TypeAlias = Literal["UP", "DOWN"]
RaGuardAction: TypeAlias = Literal["ALLOW", "DROP"]
Ospfv3State: TypeAlias = Literal["DOWN", "FULL"]
VrfImportAction: TypeAlias = Literal["IMPORT", "REJECT"]
EvpnAction: TypeAlias = Literal["INSTALL", "REJECT"]


@dataclass(frozen=True)
class DhcpBinding:
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


def apply_policer(*, offered_kbps: int, cir_kbps: int) -> int:
    """Police offered rate to CIR with zero-floor normalization."""
    normalized_offered = max(offered_kbps, 0)
    normalized_cir = max(cir_kbps, 0)
    return min(normalized_offered, normalized_cir)


def qos_police_shape(*, offered_kbps: int, cir_kbps: int, shape_rate_kbps: int) -> tuple[int, int]:
    """Return admitted (policer) and released (shaper) rates."""
    admitted = apply_policer(offered_kbps=offered_kbps, cir_kbps=cir_kbps)
    released = min(admitted, max(shape_rate_kbps, 0))
    return admitted, released


def wred_decision_profile(
    *,
    queue_depth: int,
    min_threshold: int,
    max_threshold: int,
) -> Literal["BELOW_MIN", "BETWEEN_THRESHOLDS", "AT_OR_ABOVE_MAX"]:
    """Classify queue depth against WRED thresholds."""
    if queue_depth < min_threshold:
        return "BELOW_MIN"
    if queue_depth < max_threshold:
        return "BETWEEN_THRESHOLDS"
    return "AT_OR_ABOVE_MAX"


def qos_wred_decision(*, queue_depth: int, min_threshold: int, max_threshold: int, ecn_capable: bool) -> WredAction:
    """Return FORWARD/MARK/DROP based on profile and ECN capability."""
    profile = wred_decision_profile(
        queue_depth=queue_depth,
        min_threshold=min_threshold,
        max_threshold=max_threshold,
    )
    if profile == "BELOW_MIN":
        return "FORWARD"
    if profile == "BETWEEN_THRESHOLDS":
        return "MARK" if ecn_capable else "DROP"
    return "DROP"


def redistribute_with_loop_guard(
    *,
    source_prefix: str,
    source_protocol: str,
    existing_tags: set[str],
) -> tuple[set[str], RedistributionAction]:
    """Import once per source tag; suppress re-import loops."""
    tag = build_redistribution_tag(source_prefix=source_prefix, source_protocol=source_protocol)
    if tag in existing_tags:
        return existing_tags, "LOOP_SUPPRESS"
    updated = set(existing_tags)
    updated.add(tag)
    return updated, "IMPORT"


def build_redistribution_tag(*, source_prefix: str, source_protocol: str) -> str:
    """Build canonical redistribution tag used for loop guard."""
    return f"{source_protocol.upper()}:{source_prefix}"


def fhrp_track_failover(*, active_router: str, standby_router: str, tracked_object_up: bool) -> str:
    """Return active router choice based on tracked-object state."""
    if tracked_object_result(tracked_object_up=tracked_object_up) == "UP":
        return active_router
    return standby_router


def tracked_object_result(*, tracked_object_up: bool) -> TrackState:
    """Convert object boolean into explicit UP/DOWN state."""
    return "UP" if tracked_object_up else "DOWN"


def ipv6_nd_slaac_ra_guard(*, ra_trusted: bool, source_link_local: str, prefix: str) -> tuple[RaGuardAction, str]:
    """Apply RA guard and derive SLAAC host address when allowed."""
    if not ra_trusted:
        return "DROP", ""
    host = derive_slaac_host_id(source_link_local=source_link_local)
    address = f"{prefix}{host}"
    return "ALLOW", address


def derive_slaac_host_id(*, source_link_local: str) -> str:
    """Extract deterministic host-id from link-local address."""
    return source_link_local.split("::")[-1] or "1"


def ospfv3_adjacency_lsdb(*, hello_ok: bool, lsa_id: str, lsdb: set[str]) -> tuple[Ospfv3State, set[str]]:
    """Return adjacency state and LSDB snapshot after hello/LSA handling."""
    state = ospfv3_neighbor_result(hello_ok=hello_ok)
    if state == "DOWN":
        return state, set(lsdb)
    updated = set(lsdb)
    updated.add(lsa_id)
    return state, updated


def ospfv3_neighbor_result(*, hello_ok: bool) -> Ospfv3State:
    """Derive OSPFv3 adjacency state from hello acceptance."""
    return "FULL" if hello_ok else "DOWN"


@dataclass(frozen=True)
class MpbgpPath:
    prefix: str
    local_pref: int
    as_path_len: int
    next_hop: str


def mpbgp_ipv6_unicast(paths: list[MpbgpPath]) -> MpbgpPath:
    """Pick deterministic MP-BGP best path (local-pref, AS-path, next-hop)."""
    if not paths:
        raise ValueError("at least one path is required")
    return min(paths, key=rank_mpbgp_path)


def rank_mpbgp_path(path: MpbgpPath) -> tuple[int, int, str]:
    """Return stable rank tuple for MP-BGP path selection."""
    return (-path.local_pref, path.as_path_len, path.next_hop)


def mpls_ldp_lfib(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]:
    """Return deterministic LFIB tuple (FEC, local, outgoing labels)."""
    return lfib_mapping(fec=fec, local_label=local_label, outgoing_label=outgoing_label)


def lfib_mapping(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]:
    """Build LFIB mapping tuple used by forwarding pipeline."""
    return (fec, local_label, outgoing_label)


def l3vpn_vrf_route_targets(*, import_rts: set[str], route_rt: str, prefix: str) -> tuple[VrfImportAction, str]:
    """Return IMPORT/REJECT with original prefix based on RT membership."""
    if vrf_import_action(import_rts=import_rts, route_rt=route_rt) == "IMPORT":
        return "IMPORT", prefix
    return "REJECT", prefix


def vrf_import_action(*, import_rts: set[str], route_rt: str) -> VrfImportAction:
    """Compute VRF route-target import action."""
    return "IMPORT" if route_rt in import_rts else "REJECT"


def evpn_vxlan_control(*, mac: str, ip: str, vni: int, known_vnis: set[int]) -> tuple[EvpnAction, str]:
    """Install EVPN type-2 tuple only for configured VNIs."""
    if vni not in known_vnis:
        return "REJECT", ""
    return "INSTALL", evpn_type2_entry(mac=mac, ip=ip, vni=vni)


def evpn_type2_entry(*, mac: str, ip: str, vni: int) -> str:
    """Build deterministic EVPN type-2 key."""
    return f"{mac}|{ip}|{vni}"
