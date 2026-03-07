# Lab 04: Spanning Tree

## Learning objectives

- Elect a deterministic root bridge from bridge IDs.
- Assign root/designated/alternate roles deterministically.
- Observe loop-prevention checkpoints in trace output.

## Prerequisite recap

- Complete `lab03_vlan_and_trunks`.
- Understand switched L2 loops and flood-domain behavior.

## Concept walkthrough

`lab04` introduces STP core behavior. The switch with the lowest bridge ID becomes root. Non-root switches choose one root port toward the root, while remaining links elect designated vs alternate roles to block loops.

## Implementation TODO map

- `src/routeforge/runtime/stp.py`: root election and role computation.
- `src/routeforge/labs/exercises.py`: lab topology and expected role assertions.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab04_stp --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks
```

Expected:

- `stp_root_election` step `PASS`.
- `stp_port_roles` step `PASS`.
- Checkpoints include `STP_ROOT_CHANGE`, `STP_PORT_ROLE_CHANGE`.

## Debug trace checkpoints and interpretation guidance

- `STP_ROOT_CHANGE`: root bridge selection event.
- `STP_PORT_ROLE_CHANGE`: port roles converged for loop-free topology.

## Failure drills and troubleshooting flow

- Lower `S3` bridge priority and confirm root changes from `S1` to `S3`.
- Equalize path costs and inspect tie-break by bridge ID and port ID.

## Standards and references

- IEEE 802.1D spanning tree concepts.
