# Lab 05: STP Convergence and Protection

## Learning objectives

- Recompute loop-free roles after a topology failure.
- Observe deterministic role changes after link loss.
- Enforce a guard policy for unexpected BPDUs on edge ports.

## Prerequisite recap

- Complete `lab04_stp`.
- Understand root, designated, and alternate STP roles.

## Concept walkthrough

`lab05` adds operational failure handling: when a link fails, STP must reconverge deterministically. It also introduces protection semantics, where edge ports shut down when they receive unexpected BPDUs.

## Implementation TODO map

- `src/routeforge/runtime/stp.py`: link removal, role diffing, and BPDU guard decision helper.
- `src/routeforge/labs/exercises.py`: convergence and guard verification steps.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab05_stp_convergence_and_protection --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp
```

Expected:

- `stp_topology_change` step `PASS`.
- `stp_guard_action` step `PASS`.
- Checkpoints include `STP_TOPOLOGY_CHANGE`, `STP_GUARD_ACTION`.

## Debug trace checkpoints and interpretation guidance

- `STP_TOPOLOGY_CHANGE`: role/root-path recomputation after link-state change.
- `STP_GUARD_ACTION`: guard policy enforcement event.

## Failure drills and troubleshooting flow

- Change failed link input and confirm different reconvergence role changes.
- Disable edge-port guard condition and confirm no `ERRDISABLE` action is emitted.

## Standards and references

- IEEE 802.1D topology change behavior.
- Common BPDU guard operational practice.
