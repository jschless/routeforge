# Lab 15: OSPF Multi-Area ABR

## Learning objectives

- Originate deterministic ABR summary routes.
- Install summary routes as inter-area reachability.
- Verify summary and inter-area checkpoints.

## Prerequisite recap

- Complete `lab14_ospf_spf_and_route_install`.
- Understand backbone/non-backbone area boundaries.

## Concept walkthrough

`lab15` adds ABR behavior. Non-backbone area routes are summarized deterministically and installed as inter-area routes for broader reachability.

## Implementation TODO map

- `src/routeforge/runtime/ospf.py`: summary origin helper.
- `src/routeforge/labs/exercises.py`: ABR summary/install scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab15_ospf_multi_area_abr --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install
```

Expected:

- `ospf_summary_originate` step `PASS`.
- `ospf_interarea_install` step `PASS`.
- Checkpoints include `OSPF_SUMMARY_ORIGINATE`, `OSPF_INTERAREA_ROUTE_INSTALL`.

## Debug trace checkpoints and interpretation guidance

- `OSPF_SUMMARY_ORIGINATE`: ABR summary creation event.
- `OSPF_INTERAREA_ROUTE_INSTALL`: summary programmed as inter-area route.

## Failure drills and troubleshooting flow

- Change source area routes and verify summary set changes deterministically.
- Suppress summaries and confirm inter-area lookup fails.

## Standards and references

- RFC 2328 ABR inter-area summary behavior.
