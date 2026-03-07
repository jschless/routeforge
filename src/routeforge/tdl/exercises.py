"""Executable TDL challenge scenarios."""

from __future__ import annotations

from typing import Callable

from routeforge.runtime.tdl import (
    attribute_policy_transform,
    bfd_flap_dampening,
    channel_conflict_score,
    client_join_fsm,
    closed_loop_remediation,
    community_policy_apply,
    control_plane_stability_triage,
    config_drift_diff,
    gr_stale_path_action,
    hsrp_priority_recompute,
    igmp_snooping_membership,
    isis_lsp_pacing,
    l3vpn_trace_forward,
    ldp_label_allocate,
    multicast_tree_forward,
    mpls_forward_action,
    netconf_edit_merge_replace,
    policy_pipeline_decision,
    pim_dr_election,
    prefix_list_match,
    restconf_patch_idempotence,
    roaming_decision,
    route_map_eval,
    rp_mapping,
    rpf_check,
    validate_yang_path,
    vpnv4_install_decision,
    vrf_rt_import_export,
    wireless_incident_triage,
    wmm_queue_map,
)
from routeforge.tdl.contracts import TdlOutcome, TdlRunResult, TdlStepResult, build_tdl_result


def _auto_01() -> TdlRunResult:
    valid = validate_yang_path("/interfaces/interface/enabled")
    invalid = not validate_yang_path("interfaces//enabled")
    return build_tdl_result(
        "tdl_auto_01_yang_path_validation",
        [
            TdlStepResult(
                name="yang_path_valid",
                passed=valid,
                detail="well-formed path validates",
                outcome=TdlOutcome(
                    action="VALIDATE",
                    reason="PATH_VALID",
                    checkpoints=("TDL_AUTO_PATH_OK",),
                    details={},
                ),
            ),
            TdlStepResult(
                name="yang_path_invalid",
                passed=invalid,
                detail="malformed path is rejected",
                outcome=TdlOutcome(
                    action="VALIDATE",
                    reason="PATH_REJECT",
                    checkpoints=("TDL_AUTO_PATH_REJECT",),
                    details={},
                ),
            ),
        ],
    )


def _auto_02() -> TdlRunResult:
    merged = netconf_edit_merge_replace(
        running={"hostname": "R1", "asn": 65001},
        candidate={"asn": 65010},
        operation="merge",
    )
    replaced = netconf_edit_merge_replace(
        running={"hostname": "R1", "asn": 65001},
        candidate={"hostname": "R2"},
        operation="replace",
    )
    return build_tdl_result(
        "tdl_auto_02_netconf_edit_merge_replace",
        [
            TdlStepResult(
                name="netconf_merge",
                passed=merged == {"hostname": "R1", "asn": 65010},
                detail="merge updates keys while retaining unspecified config",
                outcome=TdlOutcome(
                    action="APPLY",
                    reason="NETCONF_MERGE",
                    checkpoints=("TDL_AUTO_NETCONF_MERGE",),
                    details={"result": merged},
                ),
            ),
            TdlStepResult(
                name="netconf_replace",
                passed=replaced == {"hostname": "R2"},
                detail="replace overwrites running config with candidate",
                outcome=TdlOutcome(
                    action="APPLY",
                    reason="NETCONF_REPLACE",
                    checkpoints=("TDL_AUTO_NETCONF_REPLACE",),
                    details={"result": replaced},
                ),
            ),
        ],
    )


def _auto_03() -> TdlRunResult:
    first, changed_first = restconf_patch_idempotence(
        current={"mtu": 1500},
        patch={"mtu": 9000},
    )
    second, changed_second = restconf_patch_idempotence(
        current=first,
        patch={"mtu": 9000},
    )
    return build_tdl_result(
        "tdl_auto_03_restconf_patch_idempotence",
        [
            TdlStepResult(
                name="restconf_patch_changes",
                passed=changed_first is True and first["mtu"] == 9000,
                detail="patch changes value on first apply",
                outcome=TdlOutcome(
                    action="PATCH",
                    reason="PATCH_APPLIED",
                    checkpoints=("TDL_AUTO_PATCH_APPLY",),
                    details={"changed": changed_first},
                ),
            ),
            TdlStepResult(
                name="restconf_patch_idempotent",
                passed=changed_second is False and second["mtu"] == 9000,
                detail="repeat patch is idempotent no-op",
                outcome=TdlOutcome(
                    action="PATCH",
                    reason="PATCH_IDEMPOTENT",
                    checkpoints=("TDL_AUTO_PATCH_IDEMPOTENT",),
                    details={"changed": changed_second},
                ),
            ),
        ],
    )


def _auto_04() -> TdlRunResult:
    diff = config_drift_diff(
        intended={"hostname": "R1", "asn": 65010, "mtu": 9000},
        observed={"hostname": "R1", "asn": 65020},
    )
    return build_tdl_result(
        "tdl_auto_04_config_diff_and_drift_detection",
        [
            TdlStepResult(
                name="drift_detect_mismatch",
                passed=diff.get("asn") == (65010, 65020),
                detail="mismatched keys are surfaced with intended/observed tuple",
                outcome=TdlOutcome(
                    action="DIFF",
                    reason="DRIFT_FOUND",
                    checkpoints=("TDL_AUTO_DRIFT_FOUND",),
                    details={"diff": diff},
                ),
            ),
            TdlStepResult(
                name="drift_detect_missing",
                passed=diff.get("mtu") == (9000, None),
                detail="missing observed keys are included in drift output",
                outcome=TdlOutcome(
                    action="DIFF",
                    reason="DRIFT_MISSING_KEY",
                    checkpoints=("TDL_AUTO_DRIFT_MISSING",),
                    details={"diff": diff},
                ),
            ),
        ],
    )


def _auto_boss() -> TdlRunResult:
    actions = closed_loop_remediation(
        telemetry={"cpu": 92, "sessions": 40, "loss": 1},
        thresholds={"cpu": 80, "sessions": 60, "loss": 5},
    )
    return build_tdl_result(
        "tdl_auto_boss_closed_loop_remediation",
        [
            TdlStepResult(
                name="closed_loop_scale_out",
                passed=actions["cpu"] == "SCALE_OUT",
                detail="high-utilization metric triggers scale-out action",
                outcome=TdlOutcome(
                    action="REMEDIATE",
                    reason="SCALE_OUT",
                    checkpoints=("TDL_BOSS_AUTO_SCALE_OUT",),
                    details={"actions": actions},
                ),
            ),
            TdlStepResult(
                name="closed_loop_mixed_actions",
                passed=actions["sessions"] == "HOLD" and actions["loss"] == "SCALE_IN",
                detail="metrics map deterministically into hold/scale-in actions",
                outcome=TdlOutcome(
                    action="REMEDIATE",
                    reason="MIXED_ACTIONS",
                    checkpoints=("TDL_BOSS_AUTO_POLICY_APPLY",),
                    details={"actions": actions},
                ),
            ),
        ],
    )


def _mcast_01() -> TdlRunResult:
    good = rpf_check(incoming_interface="Gi0/1", expected_rpf_interface="Gi0/1")
    bad = not rpf_check(incoming_interface="Gi0/2", expected_rpf_interface="Gi0/1")
    return build_tdl_result(
        "tdl_mcast_01_rpf_check",
        [
            TdlStepResult(
                name="rpf_pass",
                passed=good,
                detail="packet passes when ingress equals expected RPF interface",
                outcome=TdlOutcome(
                    action="CHECK",
                    reason="RPF_PASS",
                    checkpoints=("TDL_MCAST_RPF_PASS",),
                    details={},
                ),
            ),
            TdlStepResult(
                name="rpf_fail",
                passed=bad,
                detail="packet fails when ingress differs from expected RPF interface",
                outcome=TdlOutcome(
                    action="CHECK",
                    reason="RPF_FAIL",
                    checkpoints=("TDL_MCAST_RPF_FAIL",),
                    details={},
                ),
            ),
        ],
    )


def _mcast_02() -> TdlRunResult:
    dr = pim_dr_election(
        [
            ("1.1.1.1", 100, "10.0.0.1"),
            ("2.2.2.2", 100, "10.0.0.2"),
            ("3.3.3.3", 90, "10.0.0.3"),
        ]
    )
    return build_tdl_result(
        "tdl_mcast_02_pim_dr_election",
        [
            TdlStepResult(
                name="pim_dr_priority",
                passed=dr in {"1.1.1.1", "2.2.2.2"},
                detail="DR election honors highest priority candidates",
                outcome=TdlOutcome(
                    action="ELECT",
                    reason="PIM_DR_PRIORITY",
                    checkpoints=("TDL_MCAST_DR_PRIORITY",),
                    details={"dr": dr},
                ),
            ),
            TdlStepResult(
                name="pim_dr_tiebreak",
                passed=dr == "2.2.2.2",
                detail="tie-break uses highest interface IP deterministically",
                outcome=TdlOutcome(
                    action="ELECT",
                    reason="PIM_DR_TIEBREAK",
                    checkpoints=("TDL_MCAST_DR_TIEBREAK",),
                    details={"dr": dr},
                ),
            ),
        ],
    )


def _mcast_03() -> TdlRunResult:
    table = igmp_snooping_membership(table={}, group="239.1.1.1", interface="Gi0/2", action="JOIN")
    after_leave = igmp_snooping_membership(table=table, group="239.1.1.1", interface="Gi0/2", action="LEAVE")
    return build_tdl_result(
        "tdl_mcast_03_igmp_snooping_membership_aging",
        [
            TdlStepResult(
                name="igmp_join",
                passed=table == {"239.1.1.1": {"Gi0/2"}},
                detail="JOIN event installs group membership",
                outcome=TdlOutcome(
                    action="UPDATE",
                    reason="IGMP_JOIN",
                    checkpoints=("TDL_MCAST_IGMP_JOIN",),
                    details={"table": table},
                ),
            ),
            TdlStepResult(
                name="igmp_leave_cleanup",
                passed=after_leave == {},
                detail="LEAVE event removes membership and empty group",
                outcome=TdlOutcome(
                    action="UPDATE",
                    reason="IGMP_LEAVE",
                    checkpoints=("TDL_MCAST_IGMP_LEAVE",),
                    details={"table": after_leave},
                ),
            ),
        ],
    )


def _mcast_04() -> TdlRunResult:
    mapped = rp_mapping(
        group_ip="239.1.1.10",
        rp_ranges=[("239.1.1.0", "239.1.1.255", "RP1"), ("239.2.0.0", "239.2.255.255", "RP2")],
    )
    missing = rp_mapping(
        group_ip="238.1.1.1",
        rp_ranges=[("239.1.1.0", "239.1.1.255", "RP1")],
    )
    return build_tdl_result(
        "tdl_mcast_04_rp_mapping_decision",
        [
            TdlStepResult(
                name="rp_map_match",
                passed=mapped == "RP1",
                detail="group maps into matching RP range",
                outcome=TdlOutcome(
                    action="MAP",
                    reason="RP_MATCH",
                    checkpoints=("TDL_MCAST_RP_MATCH",),
                    details={"rp": mapped},
                ),
            ),
            TdlStepResult(
                name="rp_map_miss",
                passed=missing is None,
                detail="non-matching groups return no RP",
                outcome=TdlOutcome(
                    action="MAP",
                    reason="RP_MISS",
                    checkpoints=("TDL_MCAST_RP_MISS",),
                    details={"rp": missing},
                ),
            ),
        ],
    )


def _mcast_boss() -> TdlRunResult:
    forward = multicast_tree_forward(
        joined_interfaces={"Gi0/2", "Gi0/3"},
        ingress_interface="Gi0/1",
        rpf_passed=True,
    )
    drop = multicast_tree_forward(
        joined_interfaces={"Gi0/2"},
        ingress_interface="Gi0/1",
        rpf_passed=False,
    )
    return build_tdl_result(
        "tdl_mcast_boss_end_to_end_tree_debug",
        [
            TdlStepResult(
                name="tree_forward",
                passed=forward == ("FORWARD", ("Gi0/2", "Gi0/3")),
                detail="valid RPF and listeners build deterministic forwarding set",
                outcome=TdlOutcome(
                    action="FORWARD",
                    reason="TREE_FORWARD",
                    checkpoints=("TDL_BOSS_MCAST_FORWARD",),
                    details={"result": forward},
                ),
            ),
            TdlStepResult(
                name="tree_drop_rpf",
                passed=drop == ("DROP_RPF_FAIL", ()),
                detail="RPF failure blocks multicast forwarding",
                outcome=TdlOutcome(
                    action="DROP",
                    reason="TREE_RPF_FAIL",
                    checkpoints=("TDL_BOSS_MCAST_DROP",),
                    details={"result": drop},
                ),
            ),
        ],
    )


def _wlan_01() -> TdlRunResult:
    state = client_join_fsm(current_state="IDLE", event="AUTH_OK")
    state = client_join_fsm(current_state=state, event="ASSOC_OK")
    ready = client_join_fsm(current_state=state, event="DHCP_OK")
    reset = client_join_fsm(current_state=ready, event="TIMEOUT")
    return build_tdl_result(
        "tdl_wlan_01_client_join_state_machine",
        [
            TdlStepResult(
                name="join_to_ready",
                passed=ready == "IP_READY",
                detail="auth+assoc+dhcp sequence reaches IP_READY",
                outcome=TdlOutcome(
                    action="TRANSITION",
                    reason="JOIN_SUCCESS",
                    checkpoints=("TDL_WLAN_JOIN_READY",),
                    details={"state": ready},
                ),
            ),
            TdlStepResult(
                name="join_timeout_reset",
                passed=reset == "IDLE",
                detail="timeout event resets client join state",
                outcome=TdlOutcome(
                    action="TRANSITION",
                    reason="JOIN_TIMEOUT",
                    checkpoints=("TDL_WLAN_JOIN_TIMEOUT",),
                    details={"state": reset},
                ),
            ),
        ],
    )


def _wlan_02() -> TdlRunResult:
    full = channel_conflict_score(channel_a=6, channel_b=6)
    none = channel_conflict_score(channel_a=1, channel_b=11)
    return build_tdl_result(
        "tdl_wlan_02_ap_channel_conflict_scoring",
        [
            TdlStepResult(
                name="channel_full_conflict",
                passed=full == 100,
                detail="same channel produces maximum conflict score",
                outcome=TdlOutcome(
                    action="SCORE",
                    reason="CHANNEL_CONFLICT_MAX",
                    checkpoints=("TDL_WLAN_CHAN_CONFLICT_MAX",),
                    details={"score": full},
                ),
            ),
            TdlStepResult(
                name="channel_no_conflict",
                passed=none == 0,
                detail="sufficiently separated channels produce no conflict",
                outcome=TdlOutcome(
                    action="SCORE",
                    reason="CHANNEL_CONFLICT_NONE",
                    checkpoints=("TDL_WLAN_CHAN_CONFLICT_NONE",),
                    details={"score": none},
                ),
            ),
        ],
    )


def _wlan_03() -> TdlRunResult:
    stay = roaming_decision(
        current_ap="AP1",
        current_rssi=-58,
        candidates={"AP2": -57},
        hysteresis_db=4,
    )
    roam = roaming_decision(
        current_ap="AP1",
        current_rssi=-65,
        candidates={"AP2": -57, "AP3": -60},
        hysteresis_db=4,
    )
    return build_tdl_result(
        "tdl_wlan_03_roaming_decision",
        [
            TdlStepResult(
                name="roam_hysteresis_hold",
                passed=stay == "AP1",
                detail="hysteresis prevents low-gain roam",
                outcome=TdlOutcome(
                    action="DECIDE",
                    reason="ROAM_HOLD",
                    checkpoints=("TDL_WLAN_ROAM_HOLD",),
                    details={"ap": stay},
                ),
            ),
            TdlStepResult(
                name="roam_select_best",
                passed=roam == "AP2",
                detail="best candidate above hysteresis is selected",
                outcome=TdlOutcome(
                    action="DECIDE",
                    reason="ROAM_SWITCH",
                    checkpoints=("TDL_WLAN_ROAM_SWITCH",),
                    details={"ap": roam},
                ),
            ),
        ],
    )


def _wlan_04() -> TdlRunResult:
    voice = wmm_queue_map(dscp=46)
    background = wmm_queue_map(dscp=0)
    return build_tdl_result(
        "tdl_wlan_04_wmm_queue_mapping",
        [
            TdlStepResult(
                name="wmm_voice_map",
                passed=voice == "VOICE",
                detail="EF traffic maps to voice queue",
                outcome=TdlOutcome(
                    action="MAP",
                    reason="WMM_VOICE",
                    checkpoints=("TDL_WLAN_WMM_VOICE",),
                    details={"queue": voice},
                ),
            ),
            TdlStepResult(
                name="wmm_background_map",
                passed=background == "BACKGROUND",
                detail="default traffic maps to background queue",
                outcome=TdlOutcome(
                    action="MAP",
                    reason="WMM_BACKGROUND",
                    checkpoints=("TDL_WLAN_WMM_BACKGROUND",),
                    details={"queue": background},
                ),
            ),
        ],
    )


def _wlan_boss() -> TdlRunResult:
    auth_fail = wireless_incident_triage(
        auth_ok=False,
        dhcp_ok=False,
        rssi_dbm=-60,
        channel_utilization=40,
    )
    rf_congested = wireless_incident_triage(
        auth_ok=True,
        dhcp_ok=True,
        rssi_dbm=-62,
        channel_utilization=92,
    )
    return build_tdl_result(
        "tdl_wlan_boss_site_incident_triage",
        [
            TdlStepResult(
                name="wlan_triage_auth",
                passed=auth_fail == "AUTH_FAILURE",
                detail="authentication issues are prioritized in triage output",
                outcome=TdlOutcome(
                    action="TRIAGE",
                    reason="AUTH_FAILURE",
                    checkpoints=("TDL_BOSS_WLAN_AUTH",),
                    details={"classification": auth_fail},
                ),
            ),
            TdlStepResult(
                name="wlan_triage_rf",
                passed=rf_congested == "RF_CONGESTION",
                detail="high channel utilization classifies as RF congestion",
                outcome=TdlOutcome(
                    action="TRIAGE",
                    reason="RF_CONGESTION",
                    checkpoints=("TDL_BOSS_WLAN_RF",),
                    details={"classification": rf_congested},
                ),
            ),
        ],
    )


def _route_01() -> TdlRunResult:
    permit = prefix_list_match(
        prefix="10.1.1.0/24",
        rules=[("PERMIT", "10.0.0.0/8", 24, 24)],
    )
    deny = prefix_list_match(
        prefix="10.1.1.0/25",
        rules=[("PERMIT", "10.0.0.0/8", 24, 24)],
    )
    return build_tdl_result(
        "tdl_route_01_prefix_list_match",
        [
            TdlStepResult(
                name="prefix_list_permit_match",
                passed=permit == ("PERMIT", "RULE_MATCH"),
                detail="matching prefix with ge/le bounds is permitted",
                outcome=TdlOutcome(
                    action="MATCH",
                    reason="PREFIX_PERMIT",
                    checkpoints=("TDL_ROUTE_PREFIX_PERMIT",),
                    details={"result": permit},
                ),
            ),
            TdlStepResult(
                name="prefix_list_deny_no_match",
                passed=deny == ("DENY", "NO_MATCH"),
                detail="non-matching prefix length is denied",
                outcome=TdlOutcome(
                    action="MATCH",
                    reason="PREFIX_DENY",
                    checkpoints=("TDL_ROUTE_PREFIX_DENY",),
                    details={"result": deny},
                ),
            ),
        ],
    )


def _route_02() -> TdlRunResult:
    denied = route_map_eval(
        route={"prefix": "10.1.1.0/24"},
        sequences=[(10, "DENY", True), (20, "PERMIT", True)],
    )
    implicit = route_map_eval(
        route={"prefix": "10.1.1.0/24"},
        sequences=[(10, "PERMIT", False), (20, "DENY", False)],
    )
    return build_tdl_result(
        "tdl_route_02_route_map_sequence_eval",
        [
            TdlStepResult(
                name="route_map_first_match",
                passed=denied == ("DENY", 10),
                detail="first matching sequence decides route-map action",
                outcome=TdlOutcome(
                    action="EVAL",
                    reason="ROUTE_MAP_FIRST_MATCH",
                    checkpoints=("TDL_ROUTE_MAP_FIRST_MATCH",),
                    details={"result": denied},
                ),
            ),
            TdlStepResult(
                name="route_map_implicit_deny",
                passed=implicit == ("DENY", "IMPLICIT_DENY"),
                detail="no matching sequence falls through to implicit deny",
                outcome=TdlOutcome(
                    action="EVAL",
                    reason="ROUTE_MAP_IMPLICIT_DENY",
                    checkpoints=("TDL_ROUTE_MAP_IMPLICIT_DENY",),
                    details={"result": implicit},
                ),
            ),
        ],
    )


def _route_03() -> TdlRunResult:
    added = community_policy_apply(
        current={"65000:1"},
        operation="ADD",
        values={"65000:1", "65000:100"},
    )
    replaced = community_policy_apply(
        current=added,
        operation="REPLACE",
        values={"65000:200"},
    )
    return build_tdl_result(
        "tdl_route_03_bgp_community_policy",
        [
            TdlStepResult(
                name="community_add_idempotent",
                passed=added == {"65000:1", "65000:100"},
                detail="ADD operation avoids duplicate communities",
                outcome=TdlOutcome(
                    action="APPLY",
                    reason="COMMUNITY_ADD",
                    checkpoints=("TDL_ROUTE_COMMUNITY_ADD",),
                    details={"communities": sorted(added)},
                ),
            ),
            TdlStepResult(
                name="community_replace_exact",
                passed=replaced == {"65000:200"},
                detail="REPLACE operation overwrites prior community set",
                outcome=TdlOutcome(
                    action="APPLY",
                    reason="COMMUNITY_REPLACE",
                    checkpoints=("TDL_ROUTE_COMMUNITY_REPLACE",),
                    details={"communities": sorted(replaced)},
                ),
            ),
        ],
    )


def _route_04() -> TdlRunResult:
    transformed = attribute_policy_transform(
        local_pref=100,
        med=20,
        policy={"local_pref": 200, "med": 50},
    )
    preserved = attribute_policy_transform(
        local_pref=100,
        med=20,
        policy={},
    )
    return build_tdl_result(
        "tdl_route_04_local_pref_and_med_policy",
        [
            TdlStepResult(
                name="attribute_transform_override",
                passed=transformed == (200, 50),
                detail="policy overrides local-pref and MED deterministically",
                outcome=TdlOutcome(
                    action="TRANSFORM",
                    reason="ATTR_OVERRIDE",
                    checkpoints=("TDL_ROUTE_ATTR_OVERRIDE",),
                    details={"attrs": transformed},
                ),
            ),
            TdlStepResult(
                name="attribute_transform_preserve",
                passed=preserved == (100, 20),
                detail="missing policy keys preserve existing attributes",
                outcome=TdlOutcome(
                    action="TRANSFORM",
                    reason="ATTR_PRESERVE",
                    checkpoints=("TDL_ROUTE_ATTR_PRESERVE",),
                    details={"attrs": preserved},
                ),
            ),
        ],
    )


def _route_boss() -> TdlRunResult:
    dropped = policy_pipeline_decision(
        prefix="192.0.2.0/24",
        prefix_rules=[("PERMIT", "10.0.0.0/8", 24, 24)],
        route_map_sequences=[(10, "PERMIT", True)],
        communities=set(),
        community_operation="ADD",
        community_values={"65000:100"},
        local_pref=100,
        med=20,
        attr_policy={"local_pref": 200, "med": 50},
    )
    advertised = policy_pipeline_decision(
        prefix="10.1.1.0/24",
        prefix_rules=[("PERMIT", "10.0.0.0/8", 24, 24)],
        route_map_sequences=[(10, "PERMIT", True)],
        communities=set(),
        community_operation="ADD",
        community_values={"65000:100"},
        local_pref=100,
        med=20,
        attr_policy={"local_pref": 200, "med": 50},
    )
    advertised_payload = advertised[1] if isinstance(advertised[1], dict) else {}
    return build_tdl_result(
        "tdl_route_boss_policy_pipeline_debug",
        [
            TdlStepResult(
                name="policy_pipeline_prefix_drop",
                passed=dropped == ("DROP", "PREFIX_DENY"),
                detail="prefix-list deny terminates route policy pipeline",
                outcome=TdlOutcome(
                    action="DROP",
                    reason="PREFIX_DENY",
                    checkpoints=("TDL_BOSS_ROUTE_PREFIX_DENY",),
                    details={"result": dropped},
                ),
            ),
            TdlStepResult(
                name="policy_pipeline_advertise",
                passed=advertised[0] == "ADVERTISE"
                and advertised_payload.get("local_pref") == 200
                and advertised_payload.get("med") == 50
                and advertised_payload.get("communities") == ("65000:100",),
                detail="permitted route is transformed and advertised with expected attributes",
                outcome=TdlOutcome(
                    action="ADVERTISE",
                    reason="POLICY_APPLY",
                    checkpoints=("TDL_BOSS_ROUTE_ADVERTISE",),
                    details={"result": advertised},
                ),
            ),
        ],
    )


def _mpls_01() -> TdlRunResult:
    bindings, first = ldp_label_allocate(fec="10.0.0.0/24", bindings={})
    reused_bindings, reused = ldp_label_allocate(fec="10.0.0.0/24", bindings=bindings)
    return build_tdl_result(
        "tdl_mpls_01_ldp_label_allocation",
        [
            TdlStepResult(
                name="ldp_allocate_new",
                passed=first == 16000 and bindings["10.0.0.0/24"] == 16000,
                detail="new FEC receives first deterministic label from pool",
                outcome=TdlOutcome(
                    action="ALLOCATE",
                    reason="LABEL_NEW",
                    checkpoints=("TDL_MPLS_LABEL_NEW",),
                    details={"bindings": bindings},
                ),
            ),
            TdlStepResult(
                name="ldp_allocate_reuse",
                passed=reused == 16000 and reused_bindings == bindings,
                detail="existing FEC retains stable label assignment",
                outcome=TdlOutcome(
                    action="ALLOCATE",
                    reason="LABEL_REUSE",
                    checkpoints=("TDL_MPLS_LABEL_REUSE",),
                    details={"bindings": reused_bindings},
                ),
            ),
        ],
    )


def _mpls_02() -> TdlRunResult:
    pop = mpls_forward_action(
        incoming_labeled=True,
        penultimate_hop=True,
        outgoing_label=3,
    )
    swap = mpls_forward_action(
        incoming_labeled=True,
        penultimate_hop=False,
        outgoing_label=24000,
    )
    return build_tdl_result(
        "tdl_mpls_02_php_forwarding_decision",
        [
            TdlStepResult(
                name="mpls_php_pop",
                passed=pop == ("POP", None),
                detail="penultimate hop with implicit-null performs POP",
                outcome=TdlOutcome(
                    action="FORWARD",
                    reason="PHP_POP",
                    checkpoints=("TDL_MPLS_PHP_POP",),
                    details={"result": pop},
                ),
            ),
            TdlStepResult(
                name="mpls_transit_swap",
                passed=swap == ("SWAP", 24000),
                detail="transit LSR performs SWAP with outgoing label",
                outcome=TdlOutcome(
                    action="FORWARD",
                    reason="TRANSIT_SWAP",
                    checkpoints=("TDL_MPLS_TRANSIT_SWAP",),
                    details={"result": swap},
                ),
            ),
        ],
    )


def _mpls_03() -> TdlRunResult:
    imported = vrf_rt_import_export(
        import_rts={"65000:100"},
        export_rts=set(),
        route_rt="65000:100",
        direction="IMPORT",
    )
    rejected = vrf_rt_import_export(
        import_rts={"65000:100"},
        export_rts=set(),
        route_rt="65000:200",
        direction="IMPORT",
    )
    return build_tdl_result(
        "tdl_mpls_03_l3vpn_rt_import_export",
        [
            TdlStepResult(
                name="rt_import_match",
                passed=imported == ("IMPORT", "65000:100"),
                detail="matching route-target is imported into VRF",
                outcome=TdlOutcome(
                    action="IMPORT",
                    reason="RT_MATCH",
                    checkpoints=("TDL_MPLS_RT_IMPORT",),
                    details={"result": imported},
                ),
            ),
            TdlStepResult(
                name="rt_import_reject",
                passed=rejected == ("REJECT", "65000:200"),
                detail="non-matching route-target is rejected",
                outcome=TdlOutcome(
                    action="REJECT",
                    reason="RT_MISS",
                    checkpoints=("TDL_MPLS_RT_REJECT",),
                    details={"result": rejected},
                ),
            ),
        ],
    )


def _mpls_04() -> TdlRunResult:
    installed = vpnv4_install_decision(next_hop_reachable=True, rt_action="IMPORT")
    suppressed = vpnv4_install_decision(next_hop_reachable=False, rt_action="IMPORT")
    return build_tdl_result(
        "tdl_mpls_04_vpnv4_next_hop_reachability",
        [
            TdlStepResult(
                name="vpnv4_install_reachable",
                passed=installed == ("INSTALL", "NH_REACHABLE"),
                detail="reachable next-hop with import action installs route",
                outcome=TdlOutcome(
                    action="INSTALL",
                    reason="NH_REACHABLE",
                    checkpoints=("TDL_MPLS_VPN_INSTALL",),
                    details={"result": installed},
                ),
            ),
            TdlStepResult(
                name="vpnv4_suppress_unreachable",
                passed=suppressed == ("SUPPRESS", "NH_UNREACHABLE"),
                detail="unreachable next-hop suppresses route install",
                outcome=TdlOutcome(
                    action="SUPPRESS",
                    reason="NH_UNREACHABLE",
                    checkpoints=("TDL_MPLS_VPN_SUPPRESS",),
                    details={"result": suppressed},
                ),
            ),
        ],
    )


def _mpls_boss() -> TdlRunResult:
    forwarded = l3vpn_trace_forward(
        next_hop_reachable=True,
        import_rts={"65000:100"},
        route_rt="65000:100",
        incoming_labeled=True,
        penultimate_hop=False,
        outgoing_label=24000,
    )
    dropped = l3vpn_trace_forward(
        next_hop_reachable=False,
        import_rts={"65000:100"},
        route_rt="65000:100",
        incoming_labeled=True,
        penultimate_hop=False,
        outgoing_label=24000,
    )
    return build_tdl_result(
        "tdl_mpls_boss_l3vpn_data_plane_trace",
        [
            TdlStepResult(
                name="l3vpn_trace_forward",
                passed=forwarded[0] == "FORWARD" and forwarded[1] == ("RT_IMPORT", "VPN_INSTALL", "MPLS_SWAP", "LABEL_24000"),
                detail="successful import/install path returns deterministic forwarding trace",
                outcome=TdlOutcome(
                    action="FORWARD",
                    reason="TRACE_FORWARD",
                    checkpoints=("TDL_BOSS_MPLS_FORWARD",),
                    details={"result": forwarded},
                ),
            ),
            TdlStepResult(
                name="l3vpn_trace_drop",
                passed=dropped == ("DROP", "NH_UNREACHABLE"),
                detail="next-hop failure drops route with first-failure reason",
                outcome=TdlOutcome(
                    action="DROP",
                    reason="TRACE_DROP",
                    checkpoints=("TDL_BOSS_MPLS_DROP",),
                    details={"result": dropped},
                ),
            ),
        ],
    )


def _res_01() -> TdlRunResult:
    down = hsrp_priority_recompute(base_priority=110, track_decrement=20, tracked_object_up=False)
    up = hsrp_priority_recompute(base_priority=110, track_decrement=20, tracked_object_up=True)
    return build_tdl_result(
        "tdl_res_01_hsrp_priority_tracking",
        [
            TdlStepResult(
                name="hsrp_priority_decrement",
                passed=down == 90,
                detail="tracked object down decrements HSRP priority",
                outcome=TdlOutcome(
                    action="RECOMPUTE",
                    reason="HSRP_DECREMENT",
                    checkpoints=("TDL_RES_HSRP_DECREMENT",),
                    details={"priority": down},
                ),
            ),
            TdlStepResult(
                name="hsrp_priority_stable",
                passed=up == 110,
                detail="tracked object up keeps base HSRP priority",
                outcome=TdlOutcome(
                    action="RECOMPUTE",
                    reason="HSRP_STABLE",
                    checkpoints=("TDL_RES_HSRP_STABLE",),
                    details={"priority": up},
                ),
            ),
        ],
    )


def _res_02() -> TdlRunResult:
    suppressed = bfd_flap_dampening(
        flap_count=5,
        suppress_threshold=3,
        hold_down_seconds=30,
        elapsed_seconds=10,
    )
    cleared = bfd_flap_dampening(
        flap_count=5,
        suppress_threshold=3,
        hold_down_seconds=30,
        elapsed_seconds=40,
    )
    return build_tdl_result(
        "tdl_res_02_bfd_flap_dampening",
        [
            TdlStepResult(
                name="bfd_suppress",
                passed=suppressed == ("SUPPRESS", 20),
                detail="high flap count enters suppress state until hold-down expires",
                outcome=TdlOutcome(
                    action="DAMPEN",
                    reason="BFD_SUPPRESS",
                    checkpoints=("TDL_RES_BFD_SUPPRESS",),
                    details={"result": suppressed},
                ),
            ),
            TdlStepResult(
                name="bfd_unsuppress",
                passed=cleared == ("UNSUPPRESS", 0),
                detail="elapsed hold-down exits suppress state",
                outcome=TdlOutcome(
                    action="DAMPEN",
                    reason="BFD_UNSUPPRESS",
                    checkpoints=("TDL_RES_BFD_UNSUPPRESS",),
                    details={"result": cleared},
                ),
            ),
        ],
    )


def _res_03() -> TdlRunResult:
    sent, remaining, tokens_left = isis_lsp_pacing(
        queued_lsps=("lsp1", "lsp2", "lsp3"),
        tokens=1,
        replenish=1,
        bucket_max=2,
    )
    sent_empty, remaining_empty, tokens_empty = isis_lsp_pacing(
        queued_lsps=("lsp1",),
        tokens=0,
        replenish=0,
        bucket_max=2,
    )
    return build_tdl_result(
        "tdl_res_03_isis_lsp_pacing",
        [
            TdlStepResult(
                name="isis_pacing_tokens_send",
                passed=sent == ("lsp1", "lsp2") and remaining == ("lsp3",) and tokens_left == 0,
                detail="available tokens send queued LSPs and deplete bucket",
                outcome=TdlOutcome(
                    action="PACE",
                    reason="TOKENS_AVAILABLE",
                    checkpoints=("TDL_RES_ISIS_SEND",),
                    details={"sent": sent, "remaining": remaining, "tokens": tokens_left},
                ),
            ),
            TdlStepResult(
                name="isis_pacing_tokens_empty",
                passed=sent_empty == () and remaining_empty == ("lsp1",) and tokens_empty == 0,
                detail="empty token bucket queues all LSPs",
                outcome=TdlOutcome(
                    action="PACE",
                    reason="TOKENS_EMPTY",
                    checkpoints=("TDL_RES_ISIS_QUEUE",),
                    details={"sent": sent_empty, "remaining": remaining_empty, "tokens": tokens_empty},
                ),
            ),
        ],
    )


def _res_04() -> TdlRunResult:
    retain = gr_stale_path_action(stale_seconds_remaining=15)
    flush = gr_stale_path_action(stale_seconds_remaining=0)
    return build_tdl_result(
        "tdl_res_04_graceful_restart_stale_timer",
        [
            TdlStepResult(
                name="gr_retain_stale",
                passed=retain == ("RETAIN_STALE", 15),
                detail="routes remain stale while stale timer is active",
                outcome=TdlOutcome(
                    action="STALE",
                    reason="RETAIN_STALE",
                    checkpoints=("TDL_RES_GR_RETAIN",),
                    details={"result": retain},
                ),
            ),
            TdlStepResult(
                name="gr_flush_stale",
                passed=flush == ("FLUSH_STALE", 0),
                detail="routes flush after stale timer expiry",
                outcome=TdlOutcome(
                    action="STALE",
                    reason="FLUSH_STALE",
                    checkpoints=("TDL_RES_GR_FLUSH",),
                    details={"result": flush},
                ),
            ),
        ],
    )


def _res_boss() -> TdlRunResult:
    critical = control_plane_stability_triage(
        hsrp_priority=90,
        hsrp_min_priority=100,
        bfd_state="SUPPRESS",
        stale_state="FLUSH_STALE",
    )
    healthy = control_plane_stability_triage(
        hsrp_priority=110,
        hsrp_min_priority=100,
        bfd_state="UNSUPPRESS",
        stale_state="RETAIN_STALE",
    )
    return build_tdl_result(
        "tdl_res_boss_control_plane_stability_incident",
        [
            TdlStepResult(
                name="res_triage_critical",
                passed=critical == ("CRITICAL", "CONTROL_PLANE_UNSTABLE"),
                detail="suppressed BFD and stale flush trigger critical incident",
                outcome=TdlOutcome(
                    action="TRIAGE",
                    reason="CRITICAL",
                    checkpoints=("TDL_BOSS_RES_CRITICAL",),
                    details={"result": critical},
                ),
            ),
            TdlStepResult(
                name="res_triage_healthy",
                passed=healthy == ("HEALTHY", "STABLE"),
                detail="stable signals classify control plane as healthy",
                outcome=TdlOutcome(
                    action="TRIAGE",
                    reason="HEALTHY",
                    checkpoints=("TDL_BOSS_RES_HEALTHY",),
                    details={"result": healthy},
                ),
            ),
        ],
    )


TDL_RUNNERS: dict[str, Callable[[], TdlRunResult]] = {
    "tdl_auto_01_yang_path_validation": _auto_01,
    "tdl_auto_02_netconf_edit_merge_replace": _auto_02,
    "tdl_auto_03_restconf_patch_idempotence": _auto_03,
    "tdl_auto_04_config_diff_and_drift_detection": _auto_04,
    "tdl_auto_boss_closed_loop_remediation": _auto_boss,
    "tdl_mcast_01_rpf_check": _mcast_01,
    "tdl_mcast_02_pim_dr_election": _mcast_02,
    "tdl_mcast_03_igmp_snooping_membership_aging": _mcast_03,
    "tdl_mcast_04_rp_mapping_decision": _mcast_04,
    "tdl_mcast_boss_end_to_end_tree_debug": _mcast_boss,
    "tdl_wlan_01_client_join_state_machine": _wlan_01,
    "tdl_wlan_02_ap_channel_conflict_scoring": _wlan_02,
    "tdl_wlan_03_roaming_decision": _wlan_03,
    "tdl_wlan_04_wmm_queue_mapping": _wlan_04,
    "tdl_wlan_boss_site_incident_triage": _wlan_boss,
    "tdl_route_01_prefix_list_match": _route_01,
    "tdl_route_02_route_map_sequence_eval": _route_02,
    "tdl_route_03_bgp_community_policy": _route_03,
    "tdl_route_04_local_pref_and_med_policy": _route_04,
    "tdl_route_boss_policy_pipeline_debug": _route_boss,
    "tdl_mpls_01_ldp_label_allocation": _mpls_01,
    "tdl_mpls_02_php_forwarding_decision": _mpls_02,
    "tdl_mpls_03_l3vpn_rt_import_export": _mpls_03,
    "tdl_mpls_04_vpnv4_next_hop_reachability": _mpls_04,
    "tdl_mpls_boss_l3vpn_data_plane_trace": _mpls_boss,
    "tdl_res_01_hsrp_priority_tracking": _res_01,
    "tdl_res_02_bfd_flap_dampening": _res_02,
    "tdl_res_03_isis_lsp_pacing": _res_03,
    "tdl_res_04_graceful_restart_stale_timer": _res_04,
    "tdl_res_boss_control_plane_stability_incident": _res_boss,
}


def run_tdl_challenge(challenge_id: str) -> TdlRunResult:
    try:
        runner = TDL_RUNNERS[challenge_id]
    except KeyError as exc:
        raise KeyError(f"unknown tdl challenge: {challenge_id}") from exc
    return runner()
