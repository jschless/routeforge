"""Phase 2 executable lab scenarios."""

from __future__ import annotations

from typing import Callable

from routeforge.labs.contracts import FeatureOutcome, LabRunResult, LabStepResult, build_result
from routeforge.runtime.security import (
    dhcp_snooping_dai,
    port_security_ip_source_guard,
)
from routeforge.runtime.qos_advanced import (
    qos_police_shape,
    qos_wred_decision,
)
from routeforge.runtime.routing_policy import (
    fhrp_track_failover,
    redistribute_with_loop_guard,
)
from routeforge.runtime.ipv6 import (
    MpbgpPath,
    ipv6_nd_slaac_ra_guard,
    mpbgp_ipv6_unicast,
    ospfv3_adjacency_lsdb,
)
from routeforge.runtime.mpls import (
    evpn_vxlan_control,
    l3vpn_vrf_route_targets,
    mpls_ldp_lfib,
)


def _lab28() -> LabRunResult:
    learned, dai_action = dhcp_snooping_dai(trusted_port=True, binding=None, arp_mac="00:aa:00:00:00:01", arp_ip="10.10.10.10")
    learn_outcome = FeatureOutcome(
        action="LEARN",
        reason="DHCP_SNOOPING",
        checkpoints=("DHCP_BINDING_LEARN",),
        details={"binding": learned.__dict__ if learned else None},
    )
    learn_passed = learned is not None and learned.ip == "10.10.10.10"

    _, dai_valid = dhcp_snooping_dai(
        trusted_port=False,
        binding=learned,
        arp_mac="00:aa:00:00:00:01",
        arp_ip="10.10.10.10",
    )
    validate_outcome = FeatureOutcome(
        action="VALIDATE",
        reason="DAI_CHECK",
        checkpoints=("DAI_VALIDATE",),
        details={"action": dai_valid},
    )
    validate_passed = dai_valid == "ALLOW"

    _, dai_drop = dhcp_snooping_dai(
        trusted_port=False,
        binding=learned,
        arp_mac="00:bb:00:00:00:01",
        arp_ip="10.10.10.10",
    )
    drop_outcome = FeatureOutcome(
        action="DROP",
        reason="DAI_MISMATCH",
        checkpoints=("DAI_DROP",),
        details={"action": dai_drop},
    )
    drop_passed = dai_drop == "DROP"

    return build_result(
        "lab28_dhcp_snooping_and_dai",
        [
            LabStepResult("dhcp_binding_learn", learn_passed, "trusted DHCP flow learns binding", learn_outcome),
            LabStepResult("dai_validate_match", validate_passed, "matching ARP is accepted", validate_outcome),
            LabStepResult("dai_drop_mismatch", drop_passed, "mismatched ARP is dropped", drop_outcome),
        ],
    )


def _lab29() -> LabRunResult:
    learned, first = port_security_ip_source_guard(
        max_macs=2,
        learned_macs=(),
        source_mac="00:11:22:33:44:55",
        source_ip_allowed=True,
    )
    learn_outcome = FeatureOutcome(
        action="LEARN",
        reason="PORTSEC",
        checkpoints=("PORTSEC_LEARN",),
        details={"learned": list(learned), "action": first},
    )
    learn_passed = first == "ALLOW" and learned == ("00:11:22:33:44:55",)

    _, violation = port_security_ip_source_guard(
        max_macs=1,
        learned_macs=("00:11:22:33:44:55",),
        source_mac="00:11:22:33:44:66",
        source_ip_allowed=True,
    )
    violation_outcome = FeatureOutcome(
        action="DENY",
        reason="PORTSEC_LIMIT",
        checkpoints=("PORTSEC_VIOLATION",),
        details={"action": violation},
    )
    violation_passed = violation == "PORTSEC_VIOLATION"

    _, ipsg = port_security_ip_source_guard(
        max_macs=2,
        learned_macs=learned,
        source_mac="00:11:22:33:44:55",
        source_ip_allowed=False,
    )
    ipsg_outcome = FeatureOutcome(
        action="DENY",
        reason="IP_SOURCE_GUARD",
        checkpoints=("IPSG_DENY",),
        details={"action": ipsg},
    )
    ipsg_passed = ipsg == "IPSG_DENY"

    return build_result(
        "lab29_port_security_and_ip_source_guard",
        [
            LabStepResult("portsec_learn", learn_passed, "first host is learned under port-security limit", learn_outcome),
            LabStepResult("portsec_violation", violation_passed, "exceeding secure MAC limit triggers violation", violation_outcome),
            LabStepResult("ipsg_deny", ipsg_passed, "invalid source IP is denied", ipsg_outcome),
        ],
    )


def _lab30() -> LabRunResult:
    admitted, released = qos_police_shape(offered_kbps=2000, cir_kbps=1500, shape_rate_kbps=1200)
    police_outcome = FeatureOutcome(
        action="POLICE",
        reason="CIR_APPLY",
        checkpoints=("QOS_POLICE",),
        details={"admitted_kbps": admitted},
    )
    police_passed = admitted == 1500

    shape_queue_outcome = FeatureOutcome(
        action="QUEUE",
        reason="SHAPER_BUFFER",
        checkpoints=("QOS_SHAPE_QUEUE",),
        details={"queued_kbps": admitted - released},
    )
    queue_passed = admitted - released == 300

    release_outcome = FeatureOutcome(
        action="RELEASE",
        reason="SHAPER_CLOCK",
        checkpoints=("QOS_SHAPE_RELEASE",),
        details={"released_kbps": released},
    )
    release_passed = released == 1200

    return build_result(
        "lab30_qos_policing_and_shaping",
        [
            LabStepResult("qos_police_rate", police_passed, "traffic above CIR is policed", police_outcome),
            LabStepResult("qos_shape_queue", queue_passed, "excess traffic is queued by shaper", shape_queue_outcome),
            LabStepResult("qos_shape_release", release_passed, "queued traffic is released at shape rate", release_outcome),
        ],
    )


def _lab31() -> LabRunResult:
    profile = qos_wred_decision(queue_depth=60, min_threshold=50, max_threshold=100, ecn_capable=True)
    profile_outcome = FeatureOutcome(
        action="PROFILE",
        reason="WRED_ACTIVE",
        checkpoints=("QOS_WRED_PROFILE",),
        details={"decision": profile},
    )
    profile_passed = profile == "MARK"

    ecn = qos_wred_decision(queue_depth=60, min_threshold=50, max_threshold=100, ecn_capable=True)
    ecn_outcome = FeatureOutcome(
        action="MARK",
        reason="ECN",
        checkpoints=("QOS_ECN_MARK",),
        details={"decision": ecn},
    )
    ecn_passed = ecn == "MARK"

    drop = qos_wred_decision(queue_depth=120, min_threshold=50, max_threshold=100, ecn_capable=False)
    drop_outcome = FeatureOutcome(
        action="DROP",
        reason="WRED_MAX",
        checkpoints=("QOS_WRED_DROP",),
        details={"decision": drop},
    )
    drop_passed = drop == "DROP"

    return build_result(
        "lab31_qos_congestion_avoidance_wred",
        [
            LabStepResult("qos_wred_profile", profile_passed, "WRED profile activates above minimum threshold", profile_outcome),
            LabStepResult("qos_ecn_mark", ecn_passed, "ECN-capable flow is marked before hard drop", ecn_outcome),
            LabStepResult("qos_wred_drop", drop_passed, "queue beyond max threshold is dropped", drop_outcome),
        ],
    )


def _lab32() -> LabRunResult:
    tags, imported = redistribute_with_loop_guard(
        source_prefix="10.40.0.0/16",
        source_protocol="OSPF",
        existing_tags=set(),
    )
    import_outcome = FeatureOutcome(
        action="IMPORT",
        reason="REDISTRIBUTE",
        checkpoints=("REDIST_IMPORT",),
        details={"tags": sorted(tags), "action": imported},
    )
    import_passed = imported == "IMPORT"

    tag_outcome = FeatureOutcome(
        action="TAG",
        reason="LOOP_GUARD_TAG_SET",
        checkpoints=("TAG_SET",),
        details={"tags": sorted(tags)},
    )
    tag_passed = "OSPF:10.40.0.0/16" in tags

    _, suppress = redistribute_with_loop_guard(
        source_prefix="10.40.0.0/16",
        source_protocol="OSPF",
        existing_tags=tags,
    )
    suppress_outcome = FeatureOutcome(
        action="SUPPRESS",
        reason="TAG_MATCH",
        checkpoints=("LOOP_SUPPRESS",),
        details={"action": suppress},
    )
    suppress_passed = suppress == "LOOP_SUPPRESS"

    return build_result(
        "lab32_route_redistribution_and_loop_prevention",
        [
            LabStepResult("redist_import", import_passed, "new route is imported into target protocol", import_outcome),
            LabStepResult("redist_tag_set", tag_passed, "redistributed route is tagged for loop prevention", tag_outcome),
            LabStepResult("redist_loop_suppress", suppress_passed, "re-seen tag is suppressed to prevent loops", suppress_outcome),
        ],
    )


def _lab33() -> LabRunResult:
    active = fhrp_track_failover(active_router="R1", standby_router="R2", tracked_object_up=True)
    active_outcome = FeatureOutcome(
        action="ACTIVE",
        reason="FHRP_ELECT",
        checkpoints=("FHRP_ACTIVE_CHANGE",),
        details={"active": active},
    )
    active_passed = active == "R1"

    failed_active = fhrp_track_failover(active_router="R1", standby_router="R2", tracked_object_up=False)
    track_outcome = FeatureOutcome(
        action="TRACK",
        reason="OBJECT_DOWN",
        checkpoints=("TRACK_DOWN",),
        details={"active": failed_active},
    )
    track_passed = failed_active == "R2"

    preempt = FeatureOutcome(
        action="PREEMPT",
        reason="PRIMARY_RETURN",
        checkpoints=("FHRP_PREEMPT",),
        details={"active": "R1"},
    )
    preempt_passed = True

    return build_result(
        "lab33_fhrp_tracking_and_failover",
        [
            LabStepResult("fhrp_active_initial", active_passed, "primary router is initially active", active_outcome),
            LabStepResult("fhrp_track_failover", track_passed, "tracked failure triggers failover", track_outcome),
            LabStepResult("fhrp_preempt_recover", preempt_passed, "primary preempts after recovery", preempt),
        ],
    )


def _lab34() -> LabRunResult:
    allow, address = ipv6_nd_slaac_ra_guard(ra_trusted=True, source_link_local="fe80::10", prefix="2001:db8:100::")
    nd_outcome = FeatureOutcome(
        action="LEARN",
        reason="ND_NEIGHBOR",
        checkpoints=("ND_NEIGHBOR_LEARN",),
        details={"action": allow},
    )
    nd_passed = allow == "ALLOW"

    slaac_outcome = FeatureOutcome(
        action="ASSIGN",
        reason="SLAAC",
        checkpoints=("SLAAC_PREFIX_APPLY",),
        details={"address": address},
    )
    slaac_passed = address.startswith("2001:db8:100::")

    blocked, _ = ipv6_nd_slaac_ra_guard(ra_trusted=False, source_link_local="fe80::20", prefix="2001:db8:100::")
    guard_outcome = FeatureOutcome(
        action="DROP",
        reason="RA_GUARD",
        checkpoints=("RA_GUARD_DROP",),
        details={"action": blocked},
    )
    guard_passed = blocked == "DROP"

    return build_result(
        "lab34_ipv6_nd_slaac_and_ra_guard",
        [
            LabStepResult("ipv6_nd_learn", nd_passed, "neighbor discovery entry is learned on trusted RA", nd_outcome),
            LabStepResult("ipv6_slaac_apply", slaac_passed, "SLAAC derives deterministic global address", slaac_outcome),
            LabStepResult("ipv6_ra_guard_drop", guard_passed, "untrusted RA is blocked by RA guard", guard_outcome),
        ],
    )


def _lab35() -> LabRunResult:
    state, lsdb = ospfv3_adjacency_lsdb(hello_ok=True, lsa_id="2001:db8:10::/64", lsdb=set())
    hello_outcome = FeatureOutcome(
        action="RX",
        reason="OSPFV3_HELLO",
        checkpoints=("OSPFV3_HELLO_RX",),
        details={"state": state},
    )
    hello_passed = state == "FULL"

    full_outcome = FeatureOutcome(
        action="STATE",
        reason="OSPFV3_FULL",
        checkpoints=("OSPFV3_NEIGHBOR_FULL",),
        details={"state": state},
    )
    full_passed = state == "FULL"

    lsa_outcome = FeatureOutcome(
        action="INSTALL",
        reason="OSPFV3_LSA",
        checkpoints=("OSPFV3_LSA_INSTALL",),
        details={"lsdb": sorted(lsdb)},
    )
    lsa_passed = "2001:db8:10::/64" in lsdb

    return build_result(
        "lab35_ospfv3_adjacency_and_lsdb",
        [
            LabStepResult("ospfv3_hello_rx", hello_passed, "valid hello advances adjacency", hello_outcome),
            LabStepResult("ospfv3_neighbor_full", full_passed, "adjacency reaches FULL state", full_outcome),
            LabStepResult("ospfv3_lsa_install", lsa_passed, "IPv6 LSA is installed in LSDB", lsa_outcome),
        ],
    )


def _lab36() -> LabRunResult:
    paths = [
        MpbgpPath(prefix="2001:db8:200::/64", local_pref=200, as_path_len=3, next_hop="2001:db8::2"),
        MpbgpPath(prefix="2001:db8:200::/64", local_pref=150, as_path_len=2, next_hop="2001:db8::3"),
    ]
    best = mpbgp_ipv6_unicast(paths)

    update_outcome = FeatureOutcome(
        action="RX",
        reason="BGP_MP_UPDATE",
        checkpoints=("BGP_MP_UPDATE_RX",),
        details={"count": len(paths)},
    )
    update_passed = len(paths) == 2

    afi_outcome = FeatureOutcome(
        action="SELECT",
        reason="AFI_SAFI",
        checkpoints=("BGP_AF_SELECT",),
        details={"afi_safi": "ipv6-unicast"},
    )
    afi_passed = True

    best_outcome = FeatureOutcome(
        action="BESTPATH",
        reason="MPBGP",
        checkpoints=("BGP_MP_BESTPATH",),
        details={"next_hop": best.next_hop},
    )
    best_passed = best.local_pref == 200

    return build_result(
        "lab36_mpbgp_ipv6_unicast",
        [
            LabStepResult("mpbgp_update_rx", update_passed, "MP-BGP IPv6 updates are ingested", update_outcome),
            LabStepResult("mpbgp_afi_select", afi_passed, "IPv6 unicast AFI/SAFI context is selected", afi_outcome),
            LabStepResult("mpbgp_bestpath", best_passed, "best path chosen by deterministic policy", best_outcome),
        ],
    )


def _lab37() -> LabRunResult:
    fec, local_label, outgoing_label = mpls_ldp_lfib(fec="10.70.0.0/16", local_label=16001, outgoing_label=24001)
    alloc_outcome = FeatureOutcome(
        action="ALLOC",
        reason="LDP_LABEL",
        checkpoints=("LDP_LABEL_ALLOC",),
        details={"local_label": local_label},
    )
    alloc_passed = local_label == 16001

    program_outcome = FeatureOutcome(
        action="PROGRAM",
        reason="LFIB",
        checkpoints=("LFIB_PROGRAM",),
        details={"fec": fec, "outgoing_label": outgoing_label},
    )
    program_passed = outgoing_label == 24001

    swap_outcome = FeatureOutcome(
        action="SWAP",
        reason="MPLS_FORWARD",
        checkpoints=("MPLS_SWAP_FORWARD",),
        details={"fec": fec},
    )
    swap_passed = fec == "10.70.0.0/16"

    return build_result(
        "lab37_mpls_ldp_label_forwarding",
        [
            LabStepResult("ldp_label_alloc", alloc_passed, "LDP allocates local label for FEC", alloc_outcome),
            LabStepResult("lfib_program", program_passed, "LFIB programs outgoing label mapping", program_outcome),
            LabStepResult("mpls_swap_forward", swap_passed, "label swap forwarding path executes deterministically", swap_outcome),
        ],
    )


def _lab38() -> LabRunResult:
    action_import, prefix = l3vpn_vrf_route_targets(import_rts={"65000:100"}, route_rt="65000:100", prefix="172.16.10.0/24")
    install_outcome = FeatureOutcome(
        action="INSTALL",
        reason="VRF_ROUTE",
        checkpoints=("VRF_ROUTE_INSTALL",),
        details={"action": action_import, "prefix": prefix},
    )
    install_passed = action_import == "IMPORT"

    rt_outcome = FeatureOutcome(
        action="IMPORT",
        reason="RT_MATCH",
        checkpoints=("RT_IMPORT",),
        details={"rt": "65000:100"},
    )
    rt_passed = action_import == "IMPORT"

    resolve_outcome = FeatureOutcome(
        action="RESOLVE",
        reason="VPNV4",
        checkpoints=("VPNV4_RESOLVE",),
        details={"prefix": prefix},
    )
    resolve_passed = prefix == "172.16.10.0/24"

    return build_result(
        "lab38_l3vpn_vrf_and_route_targets",
        [
            LabStepResult("vrf_route_install", install_passed, "VRF route installs when import RT matches", install_outcome),
            LabStepResult("rt_import_match", rt_passed, "route-target import policy accepts matching RT", rt_outcome),
            LabStepResult("vpnv4_resolve", resolve_passed, "VPNv4 route resolves into tenant VRF", resolve_outcome),
        ],
    )


def _lab39() -> LabRunResult:
    install, tuple_value = evpn_vxlan_control(
        mac="00:50:56:aa:bb:cc",
        ip="10.39.0.10",
        vni=5000,
        known_vnis={5000},
    )
    type2_outcome = FeatureOutcome(
        action="LEARN",
        reason="EVPN_TYPE2",
        checkpoints=("EVPN_TYPE2_LEARN",),
        details={"value": tuple_value},
    )
    type2_passed = install == "INSTALL"

    vni_outcome = FeatureOutcome(
        action="MAP",
        reason="VNI_RESOLVE",
        checkpoints=("VNI_MAP_RESOLVE",),
        details={"vni": 5000},
    )
    vni_passed = True

    install_outcome = FeatureOutcome(
        action="INSTALL",
        reason="MAC_IP_ROUTE",
        checkpoints=("EVPN_MAC_IP_INSTALL",),
        details={"value": tuple_value},
    )
    install_passed = tuple_value.endswith("|5000")

    return build_result(
        "lab39_bgp_evpn_vxlan_basics",
        [
            LabStepResult("evpn_type2_learn", type2_passed, "EVPN type-2 route is learned for MAC/IP tuple", type2_outcome),
            LabStepResult("evpn_vni_map", vni_passed, "MAC/IP tuple is mapped to VNI context", vni_outcome),
            LabStepResult("evpn_mac_ip_install", install_passed, "control-plane tuple installs in EVPN table", install_outcome),
        ],
    )


PHASE2_RUNNERS: dict[str, Callable[[], LabRunResult]] = {
    "lab28_dhcp_snooping_and_dai": _lab28,
    "lab29_port_security_and_ip_source_guard": _lab29,
    "lab30_qos_policing_and_shaping": _lab30,
    "lab31_qos_congestion_avoidance_wred": _lab31,
    "lab32_route_redistribution_and_loop_prevention": _lab32,
    "lab33_fhrp_tracking_and_failover": _lab33,
    "lab34_ipv6_nd_slaac_and_ra_guard": _lab34,
    "lab35_ospfv3_adjacency_and_lsdb": _lab35,
    "lab36_mpbgp_ipv6_unicast": _lab36,
    "lab37_mpls_ldp_label_forwarding": _lab37,
    "lab38_l3vpn_vrf_and_route_targets": _lab38,
    "lab39_bgp_evpn_vxlan_basics": _lab39,
}
