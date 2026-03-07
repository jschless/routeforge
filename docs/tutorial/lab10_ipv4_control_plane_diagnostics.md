# Lab 10: IPv4 Control Plane Diagnostics

## Learning objectives

- Generate deterministic explain output for forwarding failures.
- Assert drop reasons in a repeatable diagnostic flow.
- Emit explicit diagnostics checkpoints for troubleshooting.

## Prerequisite recap

- Complete `lab09_icmp_and_control_responses`.
- Understand normalized drop reasons from forwarding pipeline behavior.

## Concept walkthrough

`lab10` focuses on observability rather than protocol breadth. Explanations and assertions turn packet outcomes into testable troubleshooting evidence.

## Implementation TODO map

- `src/routeforge/runtime/l3.py`: drop explanation helper.
- `src/routeforge/labs/exercises.py`: explain + assert lab diagnostics steps.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab10_ipv4_control_plane_diagnostics --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection --completed lab06_arp_and_adjacency --completed lab07_ipv4_subnet_and_rib --completed lab08_fib_forwarding_pipeline --completed lab09_icmp_and_control_responses
```

Expected:

- `diagnostic_explain` step `PASS`.
- `diagnostic_assert_reason` step `PASS`.
- Checkpoints include `EXPLAIN_CHECKPOINT`, `DROP_REASON_ASSERT`.

## Debug trace checkpoints and interpretation guidance

- `EXPLAIN_CHECKPOINT`: diagnostic explanation record emitted.
- `DROP_REASON_ASSERT`: expected and observed drop reason match.

## Failure drills and troubleshooting flow

- Change packet TTL to avoid drop and verify assertion fails as expected.
- Intentionally mismatch expected reason and confirm deterministic test failure.

## Standards and references

- Operational troubleshooting patterns aligned to CCNP-style reasoning.
