from __future__ import annotations

import pytest

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


@pytest.mark.tdl("tdl_route_01_prefix_list_match")
def test_prefix_list_match_ge_le_bounds() -> None:
    assert prefix_list_match(
        prefix="10.1.1.0/24",
        rules=[("PERMIT", "10.0.0.0/8", 24, 24)],
    ) == ("PERMIT", "RULE_MATCH")
    assert prefix_list_match(
        prefix="10.1.1.0/25",
        rules=[("PERMIT", "10.0.0.0/8", 24, 24)],
    ) == ("DENY", "NO_MATCH")


@pytest.mark.tdl("tdl_route_02_route_map_sequence_eval")
def test_route_map_eval_first_match_and_implicit_deny() -> None:
    assert route_map_eval(
        route={"prefix": "10.1.1.0/24"},
        sequences=[(10, "DENY", True), (20, "PERMIT", True)],
    ) == ("DENY", 10)
    assert route_map_eval(
        route={"prefix": "10.1.1.0/24"},
        sequences=[(10, "PERMIT", False)],
    ) == ("DENY", "IMPLICIT_DENY")


@pytest.mark.tdl("tdl_route_03_bgp_community_policy")
def test_community_policy_apply_add_and_replace() -> None:
    added = community_policy_apply(
        current={"65000:1"},
        operation="ADD",
        values={"65000:1", "65000:100"},
    )
    assert added == {"65000:1", "65000:100"}
    assert community_policy_apply(
        current=added,
        operation="REPLACE",
        values={"65000:200"},
    ) == {"65000:200"}


@pytest.mark.tdl("tdl_route_04_local_pref_and_med_policy")
def test_attribute_policy_transform_override_and_preserve() -> None:
    assert attribute_policy_transform(
        local_pref=100,
        med=20,
        policy={"local_pref": 200, "med": 50},
    ) == (200, 50)
    assert attribute_policy_transform(local_pref=100, med=20, policy={}) == (100, 20)


@pytest.mark.tdl("tdl_route_boss_policy_pipeline_debug")
def test_policy_pipeline_decision_drop_and_advertise_paths() -> None:
    assert policy_pipeline_decision(
        prefix="192.0.2.0/24",
        prefix_rules=[("PERMIT", "10.0.0.0/8", 24, 24)],
        route_map_sequences=[(10, "PERMIT", True)],
        communities=set(),
        community_operation="ADD",
        community_values={"65000:100"},
        local_pref=100,
        med=20,
        attr_policy={"local_pref": 200, "med": 50},
    ) == ("DROP", "PREFIX_DENY")

    action, payload = policy_pipeline_decision(
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
    assert action == "ADVERTISE"
    assert payload == {"communities": ("65000:100",), "local_pref": 200, "med": 50}


@pytest.mark.tdl("tdl_mpls_01_ldp_label_allocation")
def test_ldp_label_allocate_new_and_reused_fec() -> None:
    bindings, first = ldp_label_allocate(fec="10.0.0.0/24", bindings={})
    assert first == 16000
    reused_bindings, reused = ldp_label_allocate(fec="10.0.0.0/24", bindings=bindings)
    assert reused == 16000
    assert reused_bindings == bindings


@pytest.mark.tdl("tdl_mpls_02_php_forwarding_decision")
def test_mpls_forward_action_pop_and_swap() -> None:
    assert mpls_forward_action(
        incoming_labeled=True,
        penultimate_hop=True,
        outgoing_label=3,
    ) == ("POP", None)
    assert mpls_forward_action(
        incoming_labeled=True,
        penultimate_hop=False,
        outgoing_label=24000,
    ) == ("SWAP", 24000)


@pytest.mark.tdl("tdl_mpls_03_l3vpn_rt_import_export")
def test_vrf_rt_import_export_import_and_reject() -> None:
    assert vrf_rt_import_export(
        import_rts={"65000:100"},
        export_rts=set(),
        route_rt="65000:100",
        direction="IMPORT",
    ) == ("IMPORT", "65000:100")
    assert vrf_rt_import_export(
        import_rts={"65000:100"},
        export_rts=set(),
        route_rt="65000:200",
        direction="IMPORT",
    ) == ("REJECT", "65000:200")


@pytest.mark.tdl("tdl_mpls_04_vpnv4_next_hop_reachability")
def test_vpnv4_install_decision_install_and_suppress() -> None:
    assert vpnv4_install_decision(next_hop_reachable=True, rt_action="IMPORT") == ("INSTALL", "NH_REACHABLE")
    assert vpnv4_install_decision(next_hop_reachable=False, rt_action="IMPORT") == ("SUPPRESS", "NH_UNREACHABLE")


@pytest.mark.tdl("tdl_mpls_boss_l3vpn_data_plane_trace")
def test_l3vpn_trace_forward_happy_and_failure_paths() -> None:
    assert l3vpn_trace_forward(
        next_hop_reachable=True,
        import_rts={"65000:100"},
        route_rt="65000:100",
        incoming_labeled=True,
        penultimate_hop=False,
        outgoing_label=24000,
    ) == ("FORWARD", ("RT_IMPORT", "VPN_INSTALL", "MPLS_SWAP", "LABEL_24000"))
    assert l3vpn_trace_forward(
        next_hop_reachable=False,
        import_rts={"65000:100"},
        route_rt="65000:100",
        incoming_labeled=True,
        penultimate_hop=False,
        outgoing_label=24000,
    ) == ("DROP", "NH_UNREACHABLE")


@pytest.mark.tdl("tdl_res_01_hsrp_priority_tracking")
def test_hsrp_priority_recompute_for_track_state() -> None:
    assert hsrp_priority_recompute(base_priority=110, track_decrement=20, tracked_object_up=False) == 90
    assert hsrp_priority_recompute(base_priority=110, track_decrement=20, tracked_object_up=True) == 110


@pytest.mark.tdl("tdl_res_02_bfd_flap_dampening")
def test_bfd_flap_dampening_suppress_and_unsuppress() -> None:
    assert bfd_flap_dampening(
        flap_count=5,
        suppress_threshold=3,
        hold_down_seconds=30,
        elapsed_seconds=10,
    ) == ("SUPPRESS", 20)
    assert bfd_flap_dampening(
        flap_count=5,
        suppress_threshold=3,
        hold_down_seconds=30,
        elapsed_seconds=30,
    ) == ("UNSUPPRESS", 0)


@pytest.mark.tdl("tdl_res_03_isis_lsp_pacing")
def test_isis_lsp_pacing_sends_only_when_tokens_available() -> None:
    assert isis_lsp_pacing(
        queued_lsps=("lsp1", "lsp2", "lsp3"),
        tokens=1,
        replenish=1,
        bucket_max=2,
    ) == (("lsp1", "lsp2"), ("lsp3",), 0)
    assert isis_lsp_pacing(
        queued_lsps=("lsp1",),
        tokens=0,
        replenish=0,
        bucket_max=2,
    ) == ((), ("lsp1",), 0)


@pytest.mark.tdl("tdl_res_04_graceful_restart_stale_timer")
def test_gr_stale_path_action_retain_and_flush() -> None:
    assert gr_stale_path_action(stale_seconds_remaining=15) == ("RETAIN_STALE", 15)
    assert gr_stale_path_action(stale_seconds_remaining=0) == ("FLUSH_STALE", 0)


@pytest.mark.tdl("tdl_res_boss_control_plane_stability_incident")
def test_control_plane_stability_triage_critical_and_healthy() -> None:
    assert control_plane_stability_triage(
        hsrp_priority=90,
        hsrp_min_priority=100,
        bfd_state="SUPPRESS",
        stale_state="FLUSH_STALE",
    ) == ("CRITICAL", "CONTROL_PLANE_UNSTABLE")
    assert control_plane_stability_triage(
        hsrp_priority=110,
        hsrp_min_priority=100,
        bfd_state="UNSUPPRESS",
        stale_state="RETAIN_STALE",
    ) == ("HEALTHY", "STABLE")
