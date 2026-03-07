# Lab 12: OSPF Network Types and DR/BDR

## Learning objectives

- Elect DR/BDR deterministically from candidate priority/router-ID.
- Handle DR failover with deterministic promotion rules.
- Verify election/failover checkpoints.

## Prerequisite recap

- Complete `lab11_ospf_adjacency_fsm`.
- Understand OSPF broadcast-network election roles.

## Concept walkthrough

`lab12` models deterministic DR/BDR elections and failover. The best candidate becomes DR, second-best becomes BDR, and BDR is promoted when DR fails.

## Implementation TODO map

- `src/routeforge/runtime/ospf.py`: DR/BDR election and failover helpers.
- `src/routeforge/labs/exercises.py`: election and failover scenarios.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab12_ospf_network_types_and_dr_bdr --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm
```

Expected:

- `ospf_dr_bdr_election` step `PASS`.
- `ospf_dr_failover` step `PASS`.
- Checkpoints include `OSPF_DR_ELECT`, `OSPF_BDR_ELECT`, `OSPF_DR_FAILOVER`.

## Debug trace checkpoints and interpretation guidance

- `OSPF_DR_ELECT`: DR winner chosen.
- `OSPF_BDR_ELECT`: BDR winner chosen.
- `OSPF_DR_FAILOVER`: failover election result.

## Failure drills and troubleshooting flow

- Equalize priorities and confirm router-ID tie-break behavior.
- Remove two candidates and verify single-router election behavior.

## Standards and references

- RFC 2328 DR/BDR election concepts.
