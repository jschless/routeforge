"""Executable TDL challenge scenarios."""

from __future__ import annotations

from typing import Callable

from routeforge.runtime.tdl import (
    channel_conflict_score,
    client_join_fsm,
    closed_loop_remediation,
    config_drift_diff,
    igmp_snooping_membership,
    multicast_tree_forward,
    netconf_edit_merge_replace,
    pim_dr_election,
    restconf_patch_idempotence,
    roaming_decision,
    rp_mapping,
    rpf_check,
    validate_yang_path,
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
}


def run_tdl_challenge(challenge_id: str) -> TdlRunResult:
    try:
        runner = TDL_RUNNERS[challenge_id]
    except KeyError as exc:
        raise KeyError(f"unknown tdl challenge: {challenge_id}") from exc
    return runner()
