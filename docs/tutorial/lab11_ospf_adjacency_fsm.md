# Lab 11: OSPF Adjacency FSM

## Learning objectives

- Process OSPF hello reception into neighbor FSM transitions.
- Observe deterministic state changes up to `FULL`.
- Verify adjacency checkpoints in traces.

## Prerequisite recap

- Complete `lab10_ipv4_control_plane_diagnostics`.
- Understand basic control-plane state machine concepts.

## Concept walkthrough

`lab11` starts OSPF behavior with neighbor states. Repeated hello processing drives deterministic transitions from `DOWN` to `FULL`.

## Implementation TODO map

- `src/routeforge/runtime/ospf.py`: neighbor hello transition logic.
- `src/routeforge/labs/exercises.py`: adjacency FSM scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab11_ospf_adjacency_fsm --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics
```

Expected:

- `ospf_hello_rx` step `PASS`.
- `ospf_neighbor_fsm_full` step `PASS`.
- Checkpoints include `OSPF_HELLO_RX`, `OSPF_NEIGHBOR_CHANGE`.

## Debug trace checkpoints and interpretation guidance

- `OSPF_HELLO_RX`: hello processing event.
- `OSPF_NEIGHBOR_CHANGE`: state transition event.

## Failure drills and troubleshooting flow

- Force dead timer expiry and confirm transition to `DOWN`.
- Skip hello input and verify state remains stable.

## Standards and references

- RFC 2328 neighbor state progression (conceptual).
