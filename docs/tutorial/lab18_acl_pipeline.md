# Lab 18: ACL Pipeline

## Learning objectives

- Evaluate ACLs with deterministic first-match ordering.
- Produce explicit permit and deny outcomes.
- Verify ACL evaluation checkpoints.

## Prerequisite recap

- Complete `lab17_bfd_for_liveness`.
- Understand ordered policy evaluation semantics.

## Concept walkthrough

`lab18` introduces policy filtering. ACL rules are evaluated top-down, first match wins, and unmatched traffic is denied.

## Implementation TODO map

- `src/routeforge/runtime/policy_acl.py`: ACL rule and evaluator.
- `src/routeforge/labs/exercises.py`: permit and deny scenarios.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab18_acl_pipeline --completed lab01_frame_and_headers,lab02_mac_learning_switch,lab03_vlan_and_trunks,lab04_stp,lab05_stp_convergence_and_protection,lab06_arp_and_adjacency,lab07_ipv4_subnet_and_rib,lab08_fib_forwarding_pipeline,lab09_icmp_and_control_responses,lab10_ipv4_control_plane_diagnostics,lab11_ospf_adjacency_fsm,lab12_ospf_network_types_and_dr_bdr,lab13_ospf_lsa_flooding_and_lsdb,lab14_ospf_spf_and_route_install,lab15_ospf_multi_area_abr,lab16_udp_tcp_fundamentals,lab17_bfd_for_liveness
```

Expected:

- `acl_permit` step `PASS`.
- `acl_deny` step `PASS`.
- Checkpoints include `ACL_EVALUATE`, `ACL_PERMIT`, `ACL_DENY`.

## Debug trace checkpoints and interpretation guidance

- `ACL_EVALUATE`: policy evaluation occurred.
- `ACL_PERMIT`: packet matched permit rule.
- `ACL_DENY`: packet matched deny path or implicit deny.

## Failure drills and troubleshooting flow

- Reorder ACL entries and confirm changed outcomes.
- Remove explicit deny and verify implicit deny still applies.

## Standards and references

- Common ACL first-match policy model.
