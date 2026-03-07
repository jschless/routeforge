# Lab 14: OSPF SPF and Route Install

## Learning objectives

- Run deterministic SPF over a weighted topology.
- Derive deterministic next-hop for destination router.
- Install SPF outcome into RIB.

## Prerequisite recap

- Complete `lab13_ospf_lsa_flooding_and_lsdb`.
- Understand shortest-path and next-hop interpretation.

## Concept walkthrough

`lab14` applies SPF results to route programming. SPF chooses least-cost paths and the resulting reachability is installed into the RIB.

## Implementation TODO map

- `src/routeforge/runtime/ospf.py`: SPF run and next-hop helper.
- `src/routeforge/labs/exercises.py`: SPF + route install scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab14_ospf_spf_and_route_install --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb
```

Expected:

- `ospf_spf_run` step `PASS`.
- `ospf_route_install` step `PASS`.
- Checkpoints include `OSPF_SPF_RUN`, `RIB_ROUTE_INSTALL`.

## Debug trace checkpoints and interpretation guidance

- `OSPF_SPF_RUN`: shortest-path computation complete.
- `RIB_ROUTE_INSTALL`: resulting route programmed into routing table.

## Failure drills and troubleshooting flow

- Adjust link cost and confirm next-hop/cost changes deterministically.
- Remove destination node and confirm SPF reachability loss.

## Standards and references

- RFC 2328 SPF route computation concepts.
