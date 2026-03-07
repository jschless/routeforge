# Lab 16: UDP/TCP Fundamentals

## Learning objectives

- Classify flows with deterministic 5-tuple identity.
- Advance TCP FSM through deterministic state transitions.
- Validate UDP datagrams with deterministic header checks.

## Prerequisite recap

- Complete `lab15_ospf_multi_area_abr`.
- Understand transport protocol differences between TCP and UDP.

## Concept walkthrough

`lab16` introduces transport behavior needed for protocol and service logic. Flow identity, TCP state transitions, and UDP validation are modeled in a deterministic way.

## Implementation TODO map

- `src/routeforge/runtime/transport.py`: flow classification, TCP FSM, UDP validation.
- `src/routeforge/labs/exercises.py`: transport scenarios and assertions.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab16_udp_tcp_fundamentals --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr
```

Expected:

- `flow_classify` step `PASS`.
- `tcp_state_change` step `PASS`.
- `udp_validate` step `PASS`.
- Checkpoints include `FLOW_CLASSIFY`, `TCP_STATE_CHANGE`, `UDP_VALIDATE`.

## Debug trace checkpoints and interpretation guidance

- `FLOW_CLASSIFY`: flow key established.
- `TCP_STATE_CHANGE`: TCP FSM state transition recorded.
- `UDP_VALIDATE`: UDP packet validity decision recorded.

## Failure drills and troubleshooting flow

- Use invalid UDP length and confirm deterministic validation failure.
- Skip TCP handshake event and verify state does not reach `ESTABLISHED`.

## Standards and references

- RFC 793 (TCP) and RFC 768 (UDP) concepts.
