from __future__ import annotations

import pytest

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


@pytest.mark.tdl("tdl_auto_01_yang_path_validation")
def test_validate_yang_path_accepts_and_rejects_expected_shapes() -> None:
    assert validate_yang_path("/interfaces/interface/state")
    assert not validate_yang_path("interfaces/interface/state")
    assert not validate_yang_path("/interfaces//state")
    assert not validate_yang_path("/interfaces/9bad")


@pytest.mark.tdl("tdl_auto_02_netconf_edit_merge_replace")
def test_netconf_edit_merge_replace_rejects_unknown_operation() -> None:
    with pytest.raises(ValueError, match="merge or replace"):
        netconf_edit_merge_replace(running={}, candidate={}, operation="delete")


@pytest.mark.tdl("tdl_auto_03_restconf_patch_idempotence")
def test_restconf_patch_idempotence_does_not_mutate_source() -> None:
    current = {"hostname": "R1", "mtu": 1500}
    updated, changed = restconf_patch_idempotence(current=current, patch={"mtu": 9000})
    assert changed is True
    assert current == {"hostname": "R1", "mtu": 1500}
    assert updated == {"hostname": "R1", "mtu": 9000}


@pytest.mark.tdl("tdl_auto_04_config_diff_and_drift_detection")
def test_config_drift_diff_tracks_missing_and_extra_keys() -> None:
    diff = config_drift_diff(intended={"a": 1, "b": 2}, observed={"a": 1, "c": 3})
    assert diff == {"b": (2, None), "c": (None, 3)}


@pytest.mark.tdl("tdl_auto_boss_closed_loop_remediation")
def test_closed_loop_remediation_threshold_boundary_behavior() -> None:
    actions = closed_loop_remediation(
        telemetry={"cpu": 80, "loss": 1, "sessions": 40},
        thresholds={"cpu": 80, "loss": 4, "sessions": 80},
    )
    assert actions == {"cpu": "HOLD", "loss": "SCALE_IN", "sessions": "HOLD"}


@pytest.mark.tdl("tdl_mcast_01_rpf_check")
def test_rpf_check_requires_exact_ingress_interface_match() -> None:
    assert rpf_check(incoming_interface="Gi0/1", expected_rpf_interface="Gi0/1")
    assert not rpf_check(incoming_interface="Gi0/2", expected_rpf_interface="Gi0/1")


@pytest.mark.tdl("tdl_mcast_02_pim_dr_election")
def test_pim_dr_election_rejects_empty_candidates() -> None:
    with pytest.raises(ValueError, match="at least one candidate"):
        pim_dr_election([])


@pytest.mark.tdl("tdl_mcast_03_igmp_snooping_membership_aging")
def test_igmp_snooping_membership_rejects_unknown_action() -> None:
    with pytest.raises(ValueError, match="JOIN or LEAVE"):
        igmp_snooping_membership(table={}, group="239.1.1.1", interface="Gi0/1", action="REFRESH")


@pytest.mark.tdl("tdl_mcast_04_rp_mapping_decision")
def test_rp_mapping_range_bounds_are_inclusive() -> None:
    ranges = [("239.1.1.0", "239.1.1.255", "RP1")]
    assert rp_mapping(group_ip="239.1.1.0", rp_ranges=ranges) == "RP1"
    assert rp_mapping(group_ip="239.1.1.255", rp_ranges=ranges) == "RP1"


@pytest.mark.tdl("tdl_mcast_boss_end_to_end_tree_debug")
def test_multicast_tree_forward_drops_when_no_egress_listeners() -> None:
    assert multicast_tree_forward(
        joined_interfaces={"Gi0/1"},
        ingress_interface="Gi0/1",
        rpf_passed=True,
    ) == ("DROP_NO_LISTENERS", ())


@pytest.mark.tdl("tdl_wlan_01_client_join_state_machine")
def test_client_join_fsm_unknown_event_holds_state() -> None:
    assert client_join_fsm(current_state="ASSOCIATED", event="UNKNOWN") == "ASSOCIATED"


@pytest.mark.tdl("tdl_wlan_02_ap_channel_conflict_scoring")
def test_channel_conflict_score_partial_overlap() -> None:
    assert channel_conflict_score(channel_a=1, channel_b=3) == 60


@pytest.mark.tdl("tdl_wlan_03_roaming_decision")
def test_roaming_decision_holds_on_tied_signal() -> None:
    assert roaming_decision(
        current_ap="AP1",
        current_rssi=-60,
        candidates={"AP2": -60, "AP3": -61},
        hysteresis_db=1,
    ) == "AP1"


@pytest.mark.tdl("tdl_wlan_04_wmm_queue_mapping")
def test_wmm_queue_map_boundary_values() -> None:
    assert wmm_queue_map(dscp=34) == "VIDEO"
    assert wmm_queue_map(dscp=10) == "BEST_EFFORT"
    assert wmm_queue_map(dscp=9) == "BACKGROUND"


@pytest.mark.tdl("tdl_wlan_boss_site_incident_triage")
def test_wireless_incident_triage_preserves_reason_precedence() -> None:
    # Auth failure takes precedence over other RF and DHCP conditions.
    assert (
        wireless_incident_triage(
            auth_ok=False,
            dhcp_ok=False,
            rssi_dbm=-90,
            channel_utilization=95,
        )
        == "AUTH_FAILURE"
    )
