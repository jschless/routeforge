"""Manifest for TDL side-quest challenges."""

from __future__ import annotations

from typing import Literal, TypedDict


class TdlEntry(TypedDict):
    id: str
    title: str
    domain: Literal["AUTOMATION", "MULTICAST", "WIRELESS"]
    kind: Literal["mission", "boss"]
    prereqs: list[str]
    xp: int
    path: str
    symbols: list[str]
    summary: str


TDL_CHALLENGES: list[TdlEntry] = [
    {
        "id": "tdl_auto_01_yang_path_validation",
        "title": "YANG Path Validation",
        "domain": "AUTOMATION",
        "kind": "mission",
        "prereqs": [],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["validate_yang_path"],
        "summary": "Validate deterministic YANG-style path syntax.",
    },
    {
        "id": "tdl_auto_02_netconf_edit_merge_replace",
        "title": "NETCONF Edit Merge/Replace",
        "domain": "AUTOMATION",
        "kind": "mission",
        "prereqs": ["tdl_auto_01_yang_path_validation"],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["netconf_edit_merge_replace"],
        "summary": "Apply NETCONF merge/replace behavior deterministically.",
    },
    {
        "id": "tdl_auto_03_restconf_patch_idempotence",
        "title": "RESTCONF PATCH Idempotence",
        "domain": "AUTOMATION",
        "kind": "mission",
        "prereqs": ["tdl_auto_02_netconf_edit_merge_replace"],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["restconf_patch_idempotence"],
        "summary": "Apply RESTCONF patch semantics and detect no-op updates.",
    },
    {
        "id": "tdl_auto_04_config_diff_and_drift_detection",
        "title": "Config Drift Detection",
        "domain": "AUTOMATION",
        "kind": "mission",
        "prereqs": ["tdl_auto_03_restconf_patch_idempotence"],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["config_drift_diff"],
        "summary": "Detect intended-vs-observed key drift for closed-loop workflows.",
    },
    {
        "id": "tdl_auto_boss_closed_loop_remediation",
        "title": "Boss: Closed-Loop Remediation",
        "domain": "AUTOMATION",
        "kind": "boss",
        "prereqs": [
            "tdl_auto_01_yang_path_validation",
            "tdl_auto_02_netconf_edit_merge_replace",
            "tdl_auto_03_restconf_patch_idempotence",
            "tdl_auto_04_config_diff_and_drift_detection",
        ],
        "xp": 300,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["closed_loop_remediation"],
        "summary": "Derive remediation actions from telemetry and thresholds.",
    },
    {
        "id": "tdl_mcast_01_rpf_check",
        "title": "RPF Check",
        "domain": "MULTICAST",
        "kind": "mission",
        "prereqs": [],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["rpf_check"],
        "summary": "Validate incoming multicast interface against RPF expectation.",
    },
    {
        "id": "tdl_mcast_02_pim_dr_election",
        "title": "PIM DR Election",
        "domain": "MULTICAST",
        "kind": "mission",
        "prereqs": ["tdl_mcast_01_rpf_check"],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["pim_dr_election"],
        "summary": "Elect PIM DR using deterministic tie-break logic.",
    },
    {
        "id": "tdl_mcast_03_igmp_snooping_membership_aging",
        "title": "IGMP Snooping Membership",
        "domain": "MULTICAST",
        "kind": "mission",
        "prereqs": ["tdl_mcast_02_pim_dr_election"],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["igmp_snooping_membership"],
        "summary": "Apply JOIN/LEAVE events to multicast group membership tables.",
    },
    {
        "id": "tdl_mcast_04_rp_mapping_decision",
        "title": "RP Mapping Decision",
        "domain": "MULTICAST",
        "kind": "mission",
        "prereqs": ["tdl_mcast_03_igmp_snooping_membership_aging"],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["rp_mapping"],
        "summary": "Map multicast group ranges to rendezvous-point selection.",
    },
    {
        "id": "tdl_mcast_boss_end_to_end_tree_debug",
        "title": "Boss: End-to-End Tree Debug",
        "domain": "MULTICAST",
        "kind": "boss",
        "prereqs": [
            "tdl_mcast_01_rpf_check",
            "tdl_mcast_02_pim_dr_election",
            "tdl_mcast_03_igmp_snooping_membership_aging",
            "tdl_mcast_04_rp_mapping_decision",
        ],
        "xp": 300,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["multicast_tree_forward"],
        "summary": "Derive multicast forwarding/drop action across RPF and listeners.",
    },
    {
        "id": "tdl_wlan_01_client_join_state_machine",
        "title": "Client Join State Machine",
        "domain": "WIRELESS",
        "kind": "mission",
        "prereqs": [],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["client_join_fsm"],
        "summary": "Advance wireless client join states with deterministic events.",
    },
    {
        "id": "tdl_wlan_02_ap_channel_conflict_scoring",
        "title": "AP Channel Conflict Scoring",
        "domain": "WIRELESS",
        "kind": "mission",
        "prereqs": ["tdl_wlan_01_client_join_state_machine"],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["channel_conflict_score"],
        "summary": "Score co-channel conflict severity for AP channel decisions.",
    },
    {
        "id": "tdl_wlan_03_roaming_decision",
        "title": "Roaming Decision",
        "domain": "WIRELESS",
        "kind": "mission",
        "prereqs": ["tdl_wlan_02_ap_channel_conflict_scoring"],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["roaming_decision"],
        "summary": "Select roaming target AP using RSSI and hysteresis.",
    },
    {
        "id": "tdl_wlan_04_wmm_queue_mapping",
        "title": "WMM Queue Mapping",
        "domain": "WIRELESS",
        "kind": "mission",
        "prereqs": ["tdl_wlan_03_roaming_decision"],
        "xp": 100,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["wmm_queue_map"],
        "summary": "Map DSCP classes into deterministic WMM queues.",
    },
    {
        "id": "tdl_wlan_boss_site_incident_triage",
        "title": "Boss: Site Incident Triage",
        "domain": "WIRELESS",
        "kind": "boss",
        "prereqs": [
            "tdl_wlan_01_client_join_state_machine",
            "tdl_wlan_02_ap_channel_conflict_scoring",
            "tdl_wlan_03_roaming_decision",
            "tdl_wlan_04_wmm_queue_mapping",
        ],
        "xp": 300,
        "path": "src/routeforge/runtime/tdl.py",
        "symbols": ["wireless_incident_triage"],
        "summary": "Classify dominant wireless incident root cause deterministically.",
    },
]


def get_tdl_challenge(challenge_id: str) -> TdlEntry | None:
    for entry in TDL_CHALLENGES:
        if entry["id"] == challenge_id:
            return entry
    return None


def tdl_missing_prereqs(challenge_id: str, completed: set[str]) -> list[str]:
    challenge = get_tdl_challenge(challenge_id)
    if challenge is None:
        raise KeyError(f"unknown tdl challenge: {challenge_id}")
    return [prereq for prereq in challenge["prereqs"] if prereq not in completed]
