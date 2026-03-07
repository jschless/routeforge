# Lab 20: QoS Marking and Queueing

## Learning objectives

- Apply deterministic DSCP remarking by traffic class.
- Enqueue packets into deterministic queues.
- Dequeue packets with deterministic scheduler behavior.

## Prerequisite recap

- Complete `lab19_nat44_stateful_translation`.
- Understand traffic-class to queue mapping basics.

## Concept walkthrough

`lab20` adds service-level queue behavior. Traffic is remarked, queued, and dequeued in a deterministic order for reproducible outcomes.

## Implementation TODO map

- `src/routeforge/runtime/qos.py`: remark, enqueue, dequeue helpers.
- `src/routeforge/labs/exercises.py`: QoS marking and scheduler scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab20_qos_marking_and_queueing --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr,lab16_udp_tcp_fundamentals,lab17_bfd_for_liveness,lab18_acl_pipeline,lab19_nat44_stateful_translation
```

Expected:

- `qos_remark` step `PASS`.
- `qos_enqueue` step `PASS`.
- `qos_dequeue` step `PASS`.
- Checkpoints include `QOS_REMARK`, `QOS_ENQUEUE`, `QOS_DEQUEUE`.

## Debug trace checkpoints and interpretation guidance

- `QOS_REMARK`: packet class remarked to DSCP.
- `QOS_ENQUEUE`: packet admitted to queue.
- `QOS_DEQUEUE`: scheduler released packet.

## Failure drills and troubleshooting flow

- Mark as best-effort and confirm queue selection changes.
- Enqueue multiple packets and verify deterministic dequeue order.

## Standards and references

- DiffServ and basic queueing model concepts.
