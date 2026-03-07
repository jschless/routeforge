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

### What problem does OSPF adjacency solve?

OSPF routers can only exchange routing information with *adjacent* neighbors — routers they've confirmed are reachable and speaking the same OSPF configuration.  The adjacency FSM (Finite State Machine) tracks whether a neighbor is reachable using *hello* packets sent on a regular interval.  If hellos stop arriving before the *dead timer* expires, the neighbor is declared down and its routes are removed.

### Topology

```
  Router R1 -------- Router R2
   (ospf area 0)   (ospf area 0)
      |                  |
   eth0              eth0
```

Two routers on a point-to-point link.  R1's view of R2 is a single neighbor entry tracked by the FSM.

### Simplified FSM (this lab)

This lab uses a two-state model (DOWN / FULL) that captures the essential behavior:

```
        hello_received=True
        dead_timer_expired=False
             ┌──────────┐
   ┌──────── │          │ ──────────────────────────────────────────┐
   │  DOWN → │   FULL   │ → DOWN (dead_timer_expired=True)          │
   │         └──────────┘                                           │
   │              ↑                                                  │
   └──────────────┘ (stays FULL on repeated hellos)                 │
                                                                     │
   ANY state → DOWN when dead_timer_expired=True ◄───────────────────┘
```

| current_state | hello_received | dead_timer_expired | next_state |
|---|---|---|---|
| any | — | True | DOWN |
| DOWN | True | False | FULL |
| FULL | True | False | FULL |
| any | False | False | unchanged |

### What correct behavior looks like

- `neighbor_hello_transition(current_state="DOWN", hello_received=True, dead_timer_expired=False)` → `"FULL"`
- `neighbor_hello_transition(current_state="FULL", hello_received=False, dead_timer_expired=True)` → `"DOWN"`
- `neighbor_hello_transition(current_state="FULL", hello_received=False, dead_timer_expired=False)` → `"FULL"`

Student-mode coding target for this stage is `src/routeforge/runtime/ospf.py` (`neighbor_hello_transition`).

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

- `OSPF_HELLO_RX`: A hello packet was processed and the neighbor state machine was evaluated.
  If missing, `neighbor_hello_transition` was not called — check the scenario setup.
- `OSPF_NEIGHBOR_CHANGE`: The neighbor state changed (e.g., DOWN → FULL or FULL → DOWN).
  If missing when a state change was expected, verify your FSM returns the correct next state
  instead of the unchanged current state.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/ospf.py` and rerun `routeforge check lab11` to confirm tests catch regressions.
- If `routeforge run lab11_ospf_adjacency_fsm --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 2328 (OSPFv2).

