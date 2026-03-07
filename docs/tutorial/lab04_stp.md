# Lab 04: Spanning Tree

## Learning objectives

- Implement `compute_stp` in `src/routeforge/runtime/stp.py`.
- Deliver `stp_root_election`: lowest bridge ID is selected as deterministic root.
- Deliver `stp_port_roles`: root/designated/alternate roles are assigned deterministically.
- Validate internal behavior through checkpoints: STP_ROOT_CHANGE, STP_PORT_ROLE_CHANGE.

## Prerequisite recap

- Required prior labs: lab03_vlan_and_trunks.
- Confirm target mapping before coding with `routeforge show lab04_stp`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

STP deterministic root and port role/state behavior. Student-mode coding target for this stage is `src/routeforge/runtime/stp.py` (`compute_stp`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/stp.py`
- Symbols: `compute_stp`
- Why this target: Compute deterministic STP root and port roles.
- Stage check: `routeforge check lab04`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab04_stp`
3. Edit only the listed symbols in `src/routeforge/runtime/stp.py`.
4. Run `routeforge check lab04` until it exits with status `0`.
5. Run `routeforge run lab04_stp --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab04_stp
routeforge check lab04

STATE=/tmp/routeforge-progress.json
routeforge run lab04_stp --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab04` passes when your implementation is complete for this stage.
- `stp_root_election` should print `[PASS]` (lowest bridge ID is selected as deterministic root).
- `stp_port_roles` should print `[PASS]` (root/designated/alternate roles are assigned deterministically).
- Run output includes checkpoints: STP_ROOT_CHANGE, STP_PORT_ROLE_CHANGE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab04_stp --state-file "$STATE" --trace-out /tmp/lab04_stp.jsonl
routeforge debug replay --trace /tmp/lab04_stp.jsonl
routeforge debug explain --trace /tmp/lab04_stp.jsonl --step stp_root_election
```

Checkpoint guide:

- `STP_ROOT_CHANGE`: STP deterministic root and port role/state behavior.
- `STP_PORT_ROLE_CHANGE`: STP deterministic root and port role/state behavior.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/stp.py` and rerun `routeforge check lab04` to confirm tests catch regressions.
- If `routeforge run lab04_stp --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IEEE 802.1D (bridging and STP fundamentals).
- IEEE 802.1Q (VLAN tagging and trunk behavior).

