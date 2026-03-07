"""Phase 2 deterministic helpers for security, IPv6, MPLS, and EVPN labs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DhcpBinding:
    mac: str
    ip: str
    vlan: int


def dhcp_snooping_dai(*, trusted_port: bool, binding: DhcpBinding | None, arp_mac: str, arp_ip: str) -> tuple[DhcpBinding | None, str]:
    # TODO(student): learn DHCP bindings and enforce deterministic DAI allow/drop.
    raise NotImplementedError("TODO: implement dhcp_snooping_dai")


def port_security_ip_source_guard(
    *,
    max_macs: int,
    learned_macs: tuple[str, ...],
    source_mac: str,
    source_ip_allowed: bool,
) -> tuple[tuple[str, ...], str]:
    # TODO(student): enforce secure-MAC limits and IP source guard policy.
    raise NotImplementedError("TODO: implement port_security_ip_source_guard")


def qos_police_shape(*, offered_kbps: int, cir_kbps: int, shape_rate_kbps: int) -> tuple[int, int]:
    # TODO(student): model deterministic policing and shaping rates.
    raise NotImplementedError("TODO: implement qos_police_shape")


def qos_wred_decision(*, queue_depth: int, min_threshold: int, max_threshold: int, ecn_capable: bool) -> str:
    # TODO(student): apply WRED/ECN decision logic from queue thresholds.
    raise NotImplementedError("TODO: implement qos_wred_decision")


def redistribute_with_loop_guard(
    *,
    source_prefix: str,
    source_protocol: str,
    existing_tags: set[str],
) -> tuple[set[str], str]:
    # TODO(student): tag redistributed routes and suppress looped re-imports.
    raise NotImplementedError("TODO: implement redistribute_with_loop_guard")


def fhrp_track_failover(*, active_router: str, standby_router: str, tracked_object_up: bool) -> str:
    # TODO(student): choose active router based on tracked object state.
    raise NotImplementedError("TODO: implement fhrp_track_failover")


def ipv6_nd_slaac_ra_guard(*, ra_trusted: bool, source_link_local: str, prefix: str) -> tuple[str, str]:
    # TODO(student): enforce RA guard and derive deterministic SLAAC address.
    raise NotImplementedError("TODO: implement ipv6_nd_slaac_ra_guard")


def ospfv3_adjacency_lsdb(*, hello_ok: bool, lsa_id: str, lsdb: set[str]) -> tuple[str, set[str]]:
    # TODO(student): transition adjacency state and install LSAs into LSDB.
    raise NotImplementedError("TODO: implement ospfv3_adjacency_lsdb")


@dataclass(frozen=True)
class MpbgpPath:
    prefix: str
    local_pref: int
    as_path_len: int
    next_hop: str


def mpbgp_ipv6_unicast(paths: list[MpbgpPath]) -> MpbgpPath:
    # TODO(student): choose deterministic MP-BGP best path for IPv6 unicast.
    raise NotImplementedError("TODO: implement mpbgp_ipv6_unicast")


def mpls_ldp_lfib(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]:
    # TODO(student): return deterministic LFIB mapping for learned LDP label.
    raise NotImplementedError("TODO: implement mpls_ldp_lfib")


def l3vpn_vrf_route_targets(*, import_rts: set[str], route_rt: str, prefix: str) -> tuple[str, str]:
    # TODO(student): import/reject VRF routes based on route-target policy.
    raise NotImplementedError("TODO: implement l3vpn_vrf_route_targets")


def evpn_vxlan_control(*, mac: str, ip: str, vni: int, known_vnis: set[int]) -> tuple[str, str]:
    # TODO(student): install EVPN MAC/IP entry only for known VNIs.
    raise NotImplementedError("TODO: implement evpn_vxlan_control")
