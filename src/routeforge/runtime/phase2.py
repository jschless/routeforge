"""Phase 2 deterministic helpers for security, IPv6, MPLS, and EVPN labs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DhcpBinding:
    mac: str
    ip: str
    vlan: int


def dhcp_snooping_dai(*, trusted_port: bool, binding: DhcpBinding | None, arp_mac: str, arp_ip: str) -> tuple[DhcpBinding | None, str]:
    if trusted_port and binding is None:
        learned = DhcpBinding(mac=arp_mac, ip=arp_ip, vlan=10)
    else:
        learned = binding
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
) -> tuple[tuple[str, ...], str]:
    if source_mac in learned_macs:
        updated = learned_macs
    elif len(learned_macs) < max_macs:
        updated = tuple(sorted((*learned_macs, source_mac)))
    else:
        return learned_macs, "PORTSEC_VIOLATION"

    if not source_ip_allowed:
        return updated, "IPSG_DENY"
    return updated, "ALLOW"


def qos_police_shape(*, offered_kbps: int, cir_kbps: int, shape_rate_kbps: int) -> tuple[int, int]:
    admitted = min(offered_kbps, cir_kbps)
    released = min(admitted, shape_rate_kbps)
    return admitted, released


def qos_wred_decision(*, queue_depth: int, min_threshold: int, max_threshold: int, ecn_capable: bool) -> str:
    if queue_depth < min_threshold:
        return "FORWARD"
    if queue_depth < max_threshold:
        return "MARK" if ecn_capable else "DROP"
    return "DROP"


def redistribute_with_loop_guard(
    *,
    source_prefix: str,
    source_protocol: str,
    existing_tags: set[str],
) -> tuple[set[str], str]:
    tag = f"{source_protocol}:{source_prefix}"
    if tag in existing_tags:
        return existing_tags, "LOOP_SUPPRESS"
    updated = set(existing_tags)
    updated.add(tag)
    return updated, "IMPORT"


def fhrp_track_failover(*, active_router: str, standby_router: str, tracked_object_up: bool) -> str:
    if tracked_object_up:
        return active_router
    return standby_router


def ipv6_nd_slaac_ra_guard(*, ra_trusted: bool, source_link_local: str, prefix: str) -> tuple[str, str]:
    if not ra_trusted:
        return "DROP", ""
    host = source_link_local.split("::")[-1] or "1"
    address = f"{prefix}{host}"
    return "ALLOW", address


def ospfv3_adjacency_lsdb(*, hello_ok: bool, lsa_id: str, lsdb: set[str]) -> tuple[str, set[str]]:
    if not hello_ok:
        return "DOWN", lsdb
    updated = set(lsdb)
    updated.add(lsa_id)
    return "FULL", updated


@dataclass(frozen=True)
class MpbgpPath:
    prefix: str
    local_pref: int
    as_path_len: int
    next_hop: str


def mpbgp_ipv6_unicast(paths: list[MpbgpPath]) -> MpbgpPath:
    if not paths:
        raise ValueError("at least one path is required")
    return min(paths, key=lambda path: (-path.local_pref, path.as_path_len, path.next_hop))


def mpls_ldp_lfib(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]:
    return fec, local_label, outgoing_label


def l3vpn_vrf_route_targets(*, import_rts: set[str], route_rt: str, prefix: str) -> tuple[str, str]:
    if route_rt in import_rts:
        return "IMPORT", prefix
    return "REJECT", prefix


def evpn_vxlan_control(*, mac: str, ip: str, vni: int, known_vnis: set[int]) -> tuple[str, str]:
    if vni not in known_vnis:
        return "REJECT", ""
    return "INSTALL", f"{mac}|{ip}|{vni}"
