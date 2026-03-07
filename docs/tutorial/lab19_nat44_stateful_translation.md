# Lab 19: NAT44 Stateful Translation

## Learning objectives

- Create deterministic NAT sessions on outbound flows.
- Translate inbound return traffic using existing session state.
- Expire idle sessions deterministically.

## Prerequisite recap

- Complete `lab18_acl_pipeline`.
- Understand inside/outside NAT flow direction.

## Concept walkthrough

`lab19` models stateful NAT44 behavior: outbound translation creates session state, inbound traffic reuses that state, and idle sessions expire after timeout.

## Implementation TODO map

- `src/routeforge/runtime/nat44.py`: session creation, lookup, expiration.
- `src/routeforge/labs/exercises.py`: outbound/inbound/timeout scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab19_nat44_stateful_translation --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr,lab16_udp_tcp_fundamentals,lab17_bfd_for_liveness,lab18_acl_pipeline
```

Expected:

- `nat_session_create` step `PASS`.
- `nat_inbound_translate` step `PASS`.
- `nat_session_expire` step `PASS`.
- Checkpoints include `NAT_SESSION_CREATE`, `NAT_TRANSLATE_OUTBOUND`, `NAT_TRANSLATE_INBOUND`, `NAT_SESSION_EXPIRE`.

## Debug trace checkpoints and interpretation guidance

- `NAT_SESSION_CREATE`: outbound session allocation event.
- `NAT_TRANSLATE_OUTBOUND`: outbound address/port translation.
- `NAT_TRANSLATE_INBOUND`: return-path lookup and reverse translation.
- `NAT_SESSION_EXPIRE`: timeout cleanup event.

## Failure drills and troubleshooting flow

- Reuse same inside flow and confirm no new outside port allocation.
- Shorten timeout and confirm earlier expiration behavior.

## Standards and references

- RFC 4787 NAT behavioral requirements (conceptual).
