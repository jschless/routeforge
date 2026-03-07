# Lab 17: BFD for Liveness

## Learning objectives

- Process BFD control packets into session state transitions.
- Detect liveness failure via deterministic timeout threshold.
- Verify BFD checkpoints for receive, state change, and timeout.

## Prerequisite recap

- Complete `lab16_udp_tcp_fundamentals`.
- Understand heartbeat-based failure detection concepts.

## Concept walkthrough

`lab17` adds fast liveness signaling. Control packets drive the session to `UP`; missed intervals drive deterministic timeout back to `DOWN`.

## Implementation TODO map

- `src/routeforge/runtime/bfd.py`: session receive/tick logic.
- `src/routeforge/labs/exercises.py`: control-receive and timeout scenarios.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab17_bfd_for_liveness --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr,lab16_udp_tcp_fundamentals
```

Expected:

- `bfd_control_rx` step `PASS`.
- `bfd_timeout` step `PASS`.
- Checkpoints include `BFD_CONTROL_RX`, `BFD_STATE_CHANGE`, `BFD_TIMEOUT`.

## Debug trace checkpoints and interpretation guidance

- `BFD_CONTROL_RX`: control packet received.
- `BFD_STATE_CHANGE`: session state updated.
- `BFD_TIMEOUT`: detect-mult timeout reached.

## Failure drills and troubleshooting flow

- Lower detect multiplier and observe faster timeout behavior.
- Keep receiving control packets and verify session stays `UP`.

## Standards and references

- RFC 5880 BFD session behavior concepts.
