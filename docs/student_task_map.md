# Student Task Map

This page is the source of truth for what a student should implement at each stage on the `student` branch.

You can query one entry from CLI:

```bash
routeforge show <lab_id>
```

It prints `student.stage`, `student.target`, `student.symbols`, and `student.summary`.

| Stage | Lab | File | Symbols |
| --- | --- | --- | --- |
| 1 | `lab01_frame_and_headers` | `src/routeforge/model/packet.py` | `is_valid_mac`, `IPv4Header.validate`, `EthernetFrame.validate` |
| 2 | `lab02_mac_learning_switch` | `src/routeforge/runtime/dataplane_sim.py` | `DataplaneSim._determine_forwarding_plan` |
| 3 | `lab03_vlan_and_trunks` | `src/routeforge/runtime/dataplane_sim.py` | `DataplaneSim._determine_egress_vlan_plan` |
| 4 | `lab04_stp` | `src/routeforge/runtime/stp.py` | `compute_stp` |
| 5 | `lab05_stp_convergence_and_protection` | `src/routeforge/runtime/stp.py` | `role_changes`, `bpdu_guard_decision` |
| 6 | `lab06_arp_and_adjacency` | `src/routeforge/runtime/adjacency.py` | `ArpAdjacencyTable.queue_packet`, `ArpAdjacencyTable.resolve` |
| 7 | `lab07_ipv4_subnet_and_rib` | `src/routeforge/runtime/l3.py` | `RibTable.lookup` |
| 8 | `lab08_fib_forwarding_pipeline` | `src/routeforge/runtime/l3.py` | `forward_packet` |
| 9 | `lab09_icmp_and_control_responses` | `src/routeforge/runtime/l3.py` | `icmp_control` |
| 10 | `lab10_ipv4_control_plane_diagnostics` | `src/routeforge/runtime/l3.py` | `explain_drop` |
| 11 | `lab11_ospf_adjacency_fsm` | `src/routeforge/runtime/ospf.py` | `neighbor_hello_transition` |
| 12 | `lab12_ospf_network_types_and_dr_bdr` | `src/routeforge/runtime/ospf.py` | `_election_order`, `failover_dr_bdr` |
| 13 | `lab13_ospf_lsa_flooding_and_lsdb` | `src/routeforge/runtime/ospf.py` | `Lsdb.age_tick` |
| 14 | `lab14_ospf_spf_and_route_install` | `src/routeforge/runtime/ospf.py` | `run_spf` |
| 15 | `lab15_ospf_multi_area_abr` | `src/routeforge/runtime/ospf.py` | `originate_summaries` |
| 16 | `lab16_udp_tcp_fundamentals` | `src/routeforge/runtime/transport.py` | `classify_flow`, `validate_udp` |
| 17 | `lab17_bfd_for_liveness` | `src/routeforge/runtime/bfd.py` | `BfdSession.tick` |
| 18 | `lab18_acl_pipeline` | `src/routeforge/runtime/policy_acl.py` | `evaluate_acl` |
| 19 | `lab19_nat44_stateful_translation` | `src/routeforge/runtime/nat44.py` | `Nat44Table.inbound_translate` |
| 20 | `lab20_qos_marking_and_queueing` | `src/routeforge/runtime/qos.py` | `QosEngine.dequeue` |
| 21 | `lab21_bgp_session_fsm_and_transport` | `src/routeforge/runtime/bgp.py` | `bgp_session_transition` |
| 22 | `lab22_bgp_attributes_and_bestpath` | `src/routeforge/runtime/bgp.py` | `select_best_path` |
| 23 | `lab23_bgp_policy_and_filters` | `src/routeforge/runtime/bgp.py` | `apply_export_policy` |
| 24 | `lab24_bgp_scaling_patterns` | `src/routeforge/runtime/bgp.py` | `route_reflect` |
| 25 | `lab25_tunnels_and_ipsec` | `src/routeforge/runtime/tunnel_ipsec.py` | `evaluate_ipsec_policy` |
| 26 | `lab26_observability_and_ops` | `src/routeforge/runtime/observability.py` | `readiness_check`, `emit_telemetry` |
| 27 | `lab27_capstone_incident_drill` | `src/routeforge/runtime/capstone.py` | `apply_step` |
| 28 | `lab28_dhcp_snooping_and_dai` | `src/routeforge/runtime/security.py` | `learn_binding_if_trusted`, `dhcp_snooping_dai` |
| 29 | `lab29_port_security_and_ip_source_guard` | `src/routeforge/runtime/security.py` | `update_secure_mac_table`, `port_security_ip_source_guard` |
| 30 | `lab30_qos_policing_and_shaping` | `src/routeforge/runtime/qos_advanced.py` | `apply_policer`, `qos_police_shape` |
| 31 | `lab31_qos_congestion_avoidance_wred` | `src/routeforge/runtime/qos_advanced.py` | `wred_decision_profile`, `qos_wred_decision` |
| 32 | `lab32_route_redistribution_and_loop_prevention` | `src/routeforge/runtime/routing_policy.py` | `build_redistribution_tag`, `redistribute_with_loop_guard` |
| 33 | `lab33_fhrp_tracking_and_failover` | `src/routeforge/runtime/routing_policy.py` | `tracked_object_result`, `fhrp_track_failover` |
| 34 | `lab34_ipv6_nd_slaac_and_ra_guard` | `src/routeforge/runtime/ipv6.py` | `derive_slaac_host_id`, `ipv6_nd_slaac_ra_guard` |
| 35 | `lab35_ospfv3_adjacency_and_lsdb` | `src/routeforge/runtime/ipv6.py` | `ospfv3_neighbor_result`, `ospfv3_adjacency_lsdb` |
| 36 | `lab36_mpbgp_ipv6_unicast` | `src/routeforge/runtime/ipv6.py` | `rank_mpbgp_path`, `mpbgp_ipv6_unicast` |
| 37 | `lab37_mpls_ldp_label_forwarding` | `src/routeforge/runtime/mpls.py` | `lfib_mapping`, `mpls_ldp_lfib` |
| 38 | `lab38_l3vpn_vrf_and_route_targets` | `src/routeforge/runtime/mpls.py` | `vrf_import_action`, `l3vpn_vrf_route_targets` |
| 39 | `lab39_bgp_evpn_vxlan_basics` | `src/routeforge/runtime/mpls.py` | `evpn_type2_entry`, `evpn_vxlan_control` |

Machine-readable source:

- [`labs/student_targets.yaml`](../labs/student_targets.yaml)
