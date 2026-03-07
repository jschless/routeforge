# RouteForge

RouteForge is a pedagogical Python networking workbook for building router intuition at CCNP depth.

It uses a dual-simulation design:

- `dataplane_sim` for packet/forwarding behavior
- `controlplane_sim` for routing protocol state machines

Both run on a shared deterministic scheduler and exchange typed bridge messages.

## Current status

Phase 0 architecture contracts are implemented.

Phase 1 + Phase 2 student loop is available for:

- `lab01_frame_and_headers`
- `lab02_mac_learning_switch`
- `lab03_vlan_and_trunks`
- `lab04_stp`
- `lab05_stp_convergence_and_protection`
- `lab06_arp_and_adjacency`
- `lab07_ipv4_subnet_and_rib`
- `lab08_fib_forwarding_pipeline`
- `lab09_icmp_and_control_responses`
- `lab10_ipv4_control_plane_diagnostics`
- `lab11_ospf_adjacency_fsm`
- `lab12_ospf_network_types_and_dr_bdr`
- `lab13_ospf_lsa_flooding_and_lsdb`
- `lab14_ospf_spf_and_route_install`
- `lab15_ospf_multi_area_abr`
- `lab16_udp_tcp_fundamentals`
- `lab17_bfd_for_liveness`
- `lab18_acl_pipeline`
- `lab19_nat44_stateful_translation`
- `lab20_qos_marking_and_queueing`
- `lab21_bgp_session_fsm_and_transport`
- `lab22_bgp_attributes_and_bestpath`
- `lab23_bgp_policy_and_filters`
- `lab24_bgp_scaling_patterns`
- `lab25_tunnels_and_ipsec`
- `lab26_observability_and_ops`
- `lab27_capstone_incident_drill`
- `lab28_dhcp_snooping_and_dai`
- `lab29_port_security_and_ip_source_guard`
- `lab30_qos_policing_and_shaping`
- `lab31_qos_congestion_avoidance_wred`
- `lab32_route_redistribution_and_loop_prevention`
- `lab33_fhrp_tracking_and_failover`
- `lab34_ipv6_nd_slaac_and_ra_guard`
- `lab35_ospfv3_adjacency_and_lsdb`
- `lab36_mpbgp_ipv6_unicast`
- `lab37_mpls_ldp_label_forwarding`
- `lab38_l3vpn_vrf_and_route_targets`
- `lab39_bgp_evpn_vxlan_basics`

Progress and readiness reporting are available via CLI:

- `routeforge progress show|mark|reset`
- `routeforge report [--json-out ...]`
- `routeforge report --rubric-file labs/assessment_rubric.yaml` for weighted scoring bands

Student experience is branch-based:

- `main`: reference implementation (all tests pass)
- `student`: same repo with selected TODO blanks in real source files
- staged checks: `routeforge check lab01`, `routeforge check lab02`, ... `routeforge check all`
- student task map: `routeforge show <lab_id>` or `docs/student_task_map.md`

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
git switch student
routeforge check lab01
routeforge check lab02
routeforge check all

# optional side-quest track
routeforge tdl list
routeforge tdl check tdl_auto_01_yang_path_validation
routeforge tdl run tdl_auto_01_yang_path_validation

# optional runtime/progress workflow
STATE=/tmp/routeforge-progress.json
routeforge run lab01_frame_and_headers --state-file "$STATE"
routeforge progress show --state-file "$STATE"
routeforge report --state-file "$STATE"
```

## Documentation

- `docs/routeforge_redesign.md`
- `docs/getting_started.md`
- `docs/tdl.md`
- `docs/student_task_map.md`
- `docs/function_contracts.md`
- `docs/bridge_contract.md`
- `labs/conformance_matrix.yaml`
- `labs/student_targets.yaml`
- `labs/assessment_rubric.yaml`
- `docs/index.md` (MkDocs textbook home)
- `docs/tutorial/lab01_frame_and_headers.md`
- `docs/tutorial/lab02_mac_learning_switch.md`
- `docs/tutorial/lab03_vlan_and_trunks.md`
- `docs/tutorial/lab04_stp.md`
- `docs/tutorial/lab05_stp_convergence_and_protection.md`
- `docs/tutorial/lab06_arp_and_adjacency.md`
- `docs/tutorial/lab07_ipv4_subnet_and_rib.md`
- `docs/tutorial/lab08_fib_forwarding_pipeline.md`
- `docs/tutorial/lab09_icmp_and_control_responses.md`
- `docs/tutorial/lab10_ipv4_control_plane_diagnostics.md`
- `docs/tutorial/lab11_ospf_adjacency_fsm.md`
- `docs/tutorial/lab12_ospf_network_types_and_dr_bdr.md`
- `docs/tutorial/lab13_ospf_lsa_flooding_and_lsdb.md`
- `docs/tutorial/lab14_ospf_spf_and_route_install.md`
- `docs/tutorial/lab15_ospf_multi_area_abr.md`
- `docs/tutorial/lab16_udp_tcp_fundamentals.md`
- `docs/tutorial/lab17_bfd_for_liveness.md`
- `docs/tutorial/lab18_acl_pipeline.md`
- `docs/tutorial/lab19_nat44_stateful_translation.md`
- `docs/tutorial/lab20_qos_marking_and_queueing.md`
- `docs/tutorial/lab21_bgp_session_fsm_and_transport.md`
- `docs/tutorial/lab22_bgp_attributes_and_bestpath.md`
- `docs/tutorial/lab23_bgp_policy_and_filters.md`
- `docs/tutorial/lab24_bgp_scaling_patterns.md`
- `docs/tutorial/lab25_tunnels_and_ipsec.md`
- `docs/tutorial/lab26_observability_and_ops.md`
- `docs/tutorial/lab27_capstone_incident_drill.md`
- `docs/tutorial/lab28_dhcp_snooping_and_dai.md`
- `docs/tutorial/lab29_port_security_and_ip_source_guard.md`
- `docs/tutorial/lab30_qos_policing_and_shaping.md`
- `docs/tutorial/lab31_qos_congestion_avoidance_wred.md`
- `docs/tutorial/lab32_route_redistribution_and_loop_prevention.md`
- `docs/tutorial/lab33_fhrp_tracking_and_failover.md`
- `docs/tutorial/lab34_ipv6_nd_slaac_and_ra_guard.md`
- `docs/tutorial/lab35_ospfv3_adjacency_and_lsdb.md`
- `docs/tutorial/lab36_mpbgp_ipv6_unicast.md`
- `docs/tutorial/lab37_mpls_ldp_label_forwarding.md`
- `docs/tutorial/lab38_l3vpn_vrf_and_route_targets.md`
- `docs/tutorial/lab39_bgp_evpn_vxlan_basics.md`

## GitHub Pages

- Workflow: `.github/workflows/pages.yml`
- Site config: `mkdocs.yml`
- Textbook home: `docs/index.md`
- GitHub setting required: `Settings -> Pages -> Source = GitHub Actions`
