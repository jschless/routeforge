# TDL Side Quests

TDL means **Test Driven Learning**.

It is a gamified side-quest track that focuses on CCNP-adjacent topics not fully covered in the core lab chain.

You implement real functions in `src/routeforge/runtime/tdl.py` and use tests to validate behavior.

## Why TDL Exists

- Core labs focus on end-to-end protocol workflow.
- TDL missions isolate one concept at a time.
- Boss challenges combine multiple concepts with stricter edge cases.

## Student Workflow

```bash
# 1) see available side quests and lock state
routeforge tdl list

# 2) inspect one challenge contract
routeforge tdl show tdl_auto_01_yang_path_validation

# 3) code in the real file
$EDITOR src/routeforge/runtime/tdl.py

# 4) run only one challenge's tests
routeforge tdl check tdl_auto_01_yang_path_validation

# 5) run scenario and update TDL XP/progress
routeforge tdl run tdl_auto_01_yang_path_validation

# 6) inspect total TDL progress
routeforge tdl progress show
```

Notes:

- `routeforge tdl run ...` persists progress in `.routeforge_tdl_progress.json` by default.
- If prerequisites are not complete, the challenge is blocked.
- `routeforge tdl check all` runs the full TDL test suite.

## Challenge Map

| ID | Domain | Kind | XP | Target Symbol |
| --- | --- | --- | --- | --- |
| `tdl_auto_01_yang_path_validation` | Automation | mission | 100 | `validate_yang_path` |
| `tdl_auto_02_netconf_edit_merge_replace` | Automation | mission | 100 | `netconf_edit_merge_replace` |
| `tdl_auto_03_restconf_patch_idempotence` | Automation | mission | 100 | `restconf_patch_idempotence` |
| `tdl_auto_04_config_diff_and_drift_detection` | Automation | mission | 100 | `config_drift_diff` |
| `tdl_auto_boss_closed_loop_remediation` | Automation | boss | 300 | `closed_loop_remediation` |
| `tdl_mcast_01_rpf_check` | Multicast | mission | 100 | `rpf_check` |
| `tdl_mcast_02_pim_dr_election` | Multicast | mission | 100 | `pim_dr_election` |
| `tdl_mcast_03_igmp_snooping_membership_aging` | Multicast | mission | 100 | `igmp_snooping_membership` |
| `tdl_mcast_04_rp_mapping_decision` | Multicast | mission | 100 | `rp_mapping` |
| `tdl_mcast_boss_end_to_end_tree_debug` | Multicast | boss | 300 | `multicast_tree_forward` |
| `tdl_wlan_01_client_join_state_machine` | Wireless | mission | 100 | `client_join_fsm` |
| `tdl_wlan_02_ap_channel_conflict_scoring` | Wireless | mission | 100 | `channel_conflict_score` |
| `tdl_wlan_03_roaming_decision` | Wireless | mission | 100 | `roaming_decision` |
| `tdl_wlan_04_wmm_queue_mapping` | Wireless | mission | 100 | `wmm_queue_map` |
| `tdl_wlan_boss_site_incident_triage` | Wireless | boss | 300 | `wireless_incident_triage` |
| `tdl_route_01_prefix_list_match` | Routing | mission | 100 | `prefix_list_match` |
| `tdl_route_02_route_map_sequence_eval` | Routing | mission | 100 | `route_map_eval` |
| `tdl_route_03_bgp_community_policy` | Routing | mission | 100 | `community_policy_apply` |
| `tdl_route_04_local_pref_and_med_policy` | Routing | mission | 100 | `attribute_policy_transform` |
| `tdl_route_boss_policy_pipeline_debug` | Routing | boss | 300 | `policy_pipeline_decision` |
| `tdl_mpls_01_ldp_label_allocation` | MPLS | mission | 100 | `ldp_label_allocate` |
| `tdl_mpls_02_php_forwarding_decision` | MPLS | mission | 100 | `mpls_forward_action` |
| `tdl_mpls_03_l3vpn_rt_import_export` | MPLS | mission | 100 | `vrf_rt_import_export` |
| `tdl_mpls_04_vpnv4_next_hop_reachability` | MPLS | mission | 100 | `vpnv4_install_decision` |
| `tdl_mpls_boss_l3vpn_data_plane_trace` | MPLS | boss | 300 | `l3vpn_trace_forward` |
| `tdl_res_01_hsrp_priority_tracking` | Resiliency | mission | 100 | `hsrp_priority_recompute` |
| `tdl_res_02_bfd_flap_dampening` | Resiliency | mission | 100 | `bfd_flap_dampening` |
| `tdl_res_03_isis_lsp_pacing` | Resiliency | mission | 100 | `isis_lsp_pacing` |
| `tdl_res_04_graceful_restart_stale_timer` | Resiliency | mission | 100 | `gr_stale_path_action` |
| `tdl_res_boss_control_plane_stability_incident` | Resiliency | boss | 300 | `control_plane_stability_triage` |

## XP and Badges

- Missions: 100 XP each
- Bosses: 300 XP each
- Max XP: 4200

Badges:

- `automation_complete`
- `multicast_complete`
- `wireless_complete`
- `routing_complete`
- `mpls_complete`
- `resiliency_complete`
- `tdl_master`

## Common Failure Patterns

- Returning ad-hoc strings that differ from expected contract strings
- Skipping deterministic tie-break behavior
- Mutating input structures when the contract expects copy-on-write
- Ignoring prerequisite lock sequencing between missions
