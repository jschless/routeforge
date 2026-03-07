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
    # TODO(student): learn a binding only on trusted ingress when missing.
    raise NotImplementedError("TODO: implement learn_binding_if_trusted")


def dhcp_snooping_dai(
    *,
    trusted_port: bool,
    binding: DhcpBinding | None,
    arp_mac: str,
    arp_ip: str,
) -> tuple[DhcpBinding | None, DaiAction]:
    # TODO(student): return ALLOW/DROP using binding learn + ARP binding validation.
    raise NotImplementedError("TODO: implement dhcp_snooping_dai")


def update_secure_mac_table(
    *,
    max_macs: int,
    learned_macs: tuple[str, ...],
    source_mac: str,
) -> tuple[tuple[str, ...], bool]:
    # TODO(student): update learned MAC tuple and signal capacity violation.
    raise NotImplementedError("TODO: implement update_secure_mac_table")


def port_security_ip_source_guard(
    *,
    max_macs: int,
    learned_macs: tuple[str, ...],
    source_mac: str,
    source_ip_allowed: bool,
) -> tuple[tuple[str, ...], PortSecurityAction]:
    # TODO(student): apply port-security learning then IP source guard decision.
    raise NotImplementedError("TODO: implement port_security_ip_source_guard")


def apply_policer(*, offered_kbps: int, cir_kbps: int) -> int:
    # TODO(student): police offered rate to CIR with deterministic zero-floor normalization.
    raise NotImplementedError("TODO: implement apply_policer")


def qos_police_shape(*, offered_kbps: int, cir_kbps: int, shape_rate_kbps: int) -> tuple[int, int]:
    # TODO(student): return admitted and released rates from policer + shaper stages.
    raise NotImplementedError("TODO: implement qos_police_shape")


def wred_decision_profile(
    *,
    queue_depth: int,
    min_threshold: int,
    max_threshold: int,
) -> Literal["BELOW_MIN", "BETWEEN_THRESHOLDS", "AT_OR_ABOVE_MAX"]:
    # TODO(student): classify queue depth into deterministic WRED profile buckets.
    raise NotImplementedError("TODO: implement wred_decision_profile")


def qos_wred_decision(*, queue_depth: int, min_threshold: int, max_threshold: int, ecn_capable: bool) -> WredAction:
    # TODO(student): map WRED profile + ECN into FORWARD, MARK, or DROP.
    raise NotImplementedError("TODO: implement qos_wred_decision")


def build_redistribution_tag(*, source_prefix: str, source_protocol: str) -> str:
    # TODO(student): build canonical redistribution tag in PROTOCOL:prefix format.
    raise NotImplementedError("TODO: implement build_redistribution_tag")


def redistribute_with_loop_guard(
    *,
    source_prefix: str,
    source_protocol: str,
    existing_tags: set[str],
) -> tuple[set[str], RedistributionAction]:
    # TODO(student): import once per canonical tag and suppress looped re-import.
    raise NotImplementedError("TODO: implement redistribute_with_loop_guard")


def tracked_object_result(*, tracked_object_up: bool) -> TrackState:
    # TODO(student): convert tracked-object boolean into UP/DOWN state.
    raise NotImplementedError("TODO: implement tracked_object_result")


def fhrp_track_failover(*, active_router: str, standby_router: str, tracked_object_up: bool) -> str:
    # TODO(student): choose active/standby outcome from tracked-object state.
    raise NotImplementedError("TODO: implement fhrp_track_failover")


def derive_slaac_host_id(*, source_link_local: str) -> str:
    # TODO(student): derive deterministic SLAAC host-id from link-local address.
    raise NotImplementedError("TODO: implement derive_slaac_host_id")


def ipv6_nd_slaac_ra_guard(*, ra_trusted: bool, source_link_local: str, prefix: str) -> tuple[RaGuardAction, str]:
    # TODO(student): enforce RA guard and return ALLOW/DROP with derived SLAAC address.
    raise NotImplementedError("TODO: implement ipv6_nd_slaac_ra_guard")


def ospfv3_neighbor_result(*, hello_ok: bool) -> Ospfv3State:
    # TODO(student): map hello acceptance to DOWN/FULL adjacency state.
    raise NotImplementedError("TODO: implement ospfv3_neighbor_result")


def ospfv3_adjacency_lsdb(*, hello_ok: bool, lsa_id: str, lsdb: set[str]) -> tuple[Ospfv3State, set[str]]:
    # TODO(student): return adjacency state and LSDB snapshot with conditional LSA install.
    raise NotImplementedError("TODO: implement ospfv3_adjacency_lsdb")


@dataclass(frozen=True)
class MpbgpPath:
    prefix: str
    local_pref: int
    as_path_len: int
    next_hop: str


def rank_mpbgp_path(path: MpbgpPath) -> tuple[int, int, str]:
    # TODO(student): return stable MP-BGP rank tuple (local-pref, AS-path, next-hop).
    raise NotImplementedError("TODO: implement rank_mpbgp_path")


def mpbgp_ipv6_unicast(paths: list[MpbgpPath]) -> MpbgpPath:
    # TODO(student): select best path using rank tuple, raising ValueError on empty input.
    raise NotImplementedError("TODO: implement mpbgp_ipv6_unicast")


def lfib_mapping(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]:
    # TODO(student): build deterministic LFIB tuple in (FEC, local, outgoing) order.
    raise NotImplementedError("TODO: implement lfib_mapping")


def mpls_ldp_lfib(*, fec: str, local_label: int, outgoing_label: int) -> tuple[str, int, int]:
    # TODO(student): return MPLS forwarding tuple via LFIB mapping contract.
    raise NotImplementedError("TODO: implement mpls_ldp_lfib")


def vrf_import_action(*, import_rts: set[str], route_rt: str) -> VrfImportAction:
    # TODO(student): return IMPORT when route-target matches VRF import set, else REJECT.
    raise NotImplementedError("TODO: implement vrf_import_action")


def l3vpn_vrf_route_targets(*, import_rts: set[str], route_rt: str, prefix: str) -> tuple[VrfImportAction, str]:
    # TODO(student): return (IMPORT/REJECT, prefix) without mutating prefix.
    raise NotImplementedError("TODO: implement l3vpn_vrf_route_targets")


def evpn_type2_entry(*, mac: str, ip: str, vni: int) -> str:
    # TODO(student): build deterministic EVPN type-2 key mac|ip|vni.
    raise NotImplementedError("TODO: implement evpn_type2_entry")


def evpn_vxlan_control(*, mac: str, ip: str, vni: int, known_vnis: set[int]) -> tuple[EvpnAction, str]:
    # TODO(student): return INSTALL for known VNI and REJECT with empty payload otherwise.
    raise NotImplementedError("TODO: implement evpn_vxlan_control")
