# RouteForge

RouteForge is a pedagogical Python networking workbook for building router intuition at CCNP depth.

It uses a dual-simulation design:

- `dataplane_sim` for packet/forwarding behavior
- `controlplane_sim` for routing protocol state machines

Both run on a shared deterministic scheduler and exchange typed bridge messages.

## Current status

Phase 0 architecture contracts are implemented.

Phase 1 student loop is available for:

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

Progress and readiness reporting are available via CLI:

- `routeforge progress show|mark|reset`
- `routeforge report [--json-out ...]`
- `routeforge report --rubric-file labs/assessment_rubric.yaml` for weighted scoring bands

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
routeforge labs
routeforge run lab01_frame_and_headers
routeforge run lab02_mac_learning_switch --completed lab01_frame_and_headers
routeforge run lab03_vlan_and_trunks --completed lab01_frame_and_headers --completed lab02_mac_learning_switch
routeforge run lab04_stp --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks
routeforge run lab05_stp_convergence_and_protection --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp
routeforge run lab06_arp_and_adjacency --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection
routeforge run lab07_ipv4_subnet_and_rib --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection --completed lab06_arp_and_adjacency
routeforge run lab08_fib_forwarding_pipeline --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection --completed lab06_arp_and_adjacency --completed lab07_ipv4_subnet_and_rib
routeforge run lab09_icmp_and_control_responses --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection --completed lab06_arp_and_adjacency --completed lab07_ipv4_subnet_and_rib --completed lab08_fib_forwarding_pipeline
routeforge run lab10_ipv4_control_plane_diagnostics --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection --completed lab06_arp_and_adjacency --completed lab07_ipv4_subnet_and_rib --completed lab08_fib_forwarding_pipeline --completed lab09_icmp_and_control_responses
routeforge run lab11_ospf_adjacency_fsm --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics
routeforge run lab12_ospf_network_types_and_dr_bdr --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm
routeforge run lab13_ospf_lsa_flooding_and_lsdb --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr
routeforge run lab14_ospf_spf_and_route_install --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb
routeforge run lab15_ospf_multi_area_abr --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install
routeforge run lab16_udp_tcp_fundamentals --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr
routeforge run lab17_bfd_for_liveness --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr,lab16_udp_tcp_fundamentals
routeforge run lab18_acl_pipeline --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr,lab16_udp_tcp_fundamentals,lab17_bfd_for_liveness
routeforge run lab19_nat44_stateful_translation --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr,lab16_udp_tcp_fundamentals,lab17_bfd_for_liveness,lab18_acl_pipeline
routeforge run lab20_qos_marking_and_queueing --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr,lab16_udp_tcp_fundamentals,lab17_bfd_for_liveness,lab18_acl_pipeline,lab19_nat44_stateful_translation
routeforge run lab21_bgp_session_fsm_and_transport --completed <all-prior-labs> --state-file /tmp/routeforge-progress.json
routeforge progress show --state-file /tmp/routeforge-progress.json
routeforge run lab22_bgp_attributes_and_bestpath --state-file /tmp/routeforge-progress.json
routeforge report --state-file /tmp/routeforge-progress.json
routeforge report --state-file /tmp/routeforge-progress.json --json-out /tmp/routeforge-report.json
routeforge report --state-file /tmp/routeforge-progress.json --rubric-file labs/assessment_rubric.yaml
routeforge run lab01_frame_and_headers --trace-out /tmp/lab01-trace.jsonl
routeforge debug replay --trace /tmp/lab01-trace.jsonl
routeforge debug explain --trace /tmp/lab01-trace.jsonl --step invalid_frame_drops
```

## Documentation

- `docs/routeforge_redesign.md`
- `docs/bridge_contract.md`
- `labs/conformance_matrix.yaml`
- `labs/assessment_rubric.yaml`
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
