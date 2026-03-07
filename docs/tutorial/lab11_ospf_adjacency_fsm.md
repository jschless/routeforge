# Lab 11: OSPF Adjacency FSM

## Learning objectives

- Implement `neighbor_hello_transition` in `src/routeforge/runtime/ospf.py`.
- Deliver `ospf_hello_rx`: hello packet advances neighbor from DOWN to INIT.
- Deliver `ospf_neighbor_fsm_full`: neighbor state machine converges deterministically to FULL.
- Validate internal behavior through checkpoints: OSPF_HELLO_RX, OSPF_NEIGHBOR_CHANGE.

## Prerequisite recap

- Required prior labs: lab10_ipv4_control_plane_diagnostics.
- Confirm target mapping before coding with `routeforge show lab11_ospf_adjacency_fsm`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

OSPF neighbor state machine and timer behavior. Student-mode coding target for this stage is `src/routeforge/runtime/ospf.py` (`neighbor_hello_transition`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/ospf.py`
- Symbols: `neighbor_hello_transition`
- Why this target: Advance OSPF neighbor state machine on hello/dead events.
- Stage check: `routeforge check lab11`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab11_ospf_adjacency_fsm`
3. Edit only the listed symbols in `src/routeforge/runtime/ospf.py`.
4. Run `routeforge check lab11` until it exits with status `0`.
5. Run `routeforge run lab11_ospf_adjacency_fsm --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab11_ospf_adjacency_fsm
routeforge check lab11

STATE=/tmp/routeforge-progress.json
routeforge run lab11_ospf_adjacency_fsm --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab11` passes when your implementation is complete for this stage.
- `ospf_hello_rx` should print `[PASS]` (hello packet advances neighbor from DOWN to INIT).
- `ospf_neighbor_fsm_full` should print `[PASS]` (neighbor state machine converges deterministically to FULL).
- Run output includes checkpoints: OSPF_HELLO_RX, OSPF_NEIGHBOR_CHANGE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab11_ospf_adjacency_fsm --state-file "$STATE" --trace-out /tmp/lab11_ospf_adjacency_fsm.jsonl
routeforge debug replay --trace /tmp/lab11_ospf_adjacency_fsm.jsonl
routeforge debug explain --trace /tmp/lab11_ospf_adjacency_fsm.jsonl --step ospf_hello_rx
```

Checkpoint guide:

- `OSPF_HELLO_RX`: OSPF neighbor state machine and timer behavior.
- `OSPF_NEIGHBOR_CHANGE`: OSPF neighbor state machine and timer behavior.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/ospf.py` and rerun `routeforge check lab11` to confirm tests catch regressions.
- If `routeforge run lab11_ospf_adjacency_fsm --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 2328 (OSPFv2).

