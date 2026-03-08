# Lab 21: BGP Session FSM and Transport

## Learning objectives

- Implement `bgp_session_transition` in `src/routeforge/runtime/bgp.py`.
- Deliver `bgp_open_and_establish`: BGP OPEN and KEEPALIVE events transition the session to ESTABLISHED.
- Deliver `bgp_hold_timer_reset`: hold timer expiry returns the BGP session to IDLE.
- Validate internal behavior through checkpoints: BGP_OPEN_RX, BGP_SESSION_CHANGE.

## Prerequisite recap

- Required prior labs: lab20_qos_marking_and_queueing.
- Confirm target mapping before coding with `routeforge show lab21_bgp_session_fsm_and_transport`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### What problem does the BGP session FSM solve?

BGP is a *session-oriented* protocol — two routers must complete a TCP connection, exchange OPEN messages, and confirm parameters before they can exchange routing information.  The FSM tracks where each session is in that process and ensures that unexpected events (TCP failures, malformed OPENs) send the session back to a safe state.

### Topology

```
AS 65001             AS 65002
  R1 ─────────── TCP/BGP ─────────────  R2
  (10.1.1.1)     (port 179)       (10.1.1.2)
```

One eBGP session between R1 and R2.  The FSM on each router tracks the state of its side of the session.

### BGP session FSM (this lab's scope)

```
   IDLE ──START──► CONNECT ──TCP_OPEN──► OPEN_SENT ──OPEN_RECEIVED──► OPEN_CONFIRM ──KEEPALIVE──► ESTABLISHED
    ▲                  │                     │                               │                         │
    │               TCP_FAIL               ERROR                          ERROR                    NOTIFICATION
    │                  │                     │                               │                         │
    └──────────────────┴─────────────────────┴───────────────────────────────┴─────────────────────────┘
                  (any error or unexpected event → IDLE)
```

Normal session establishment sequence:
```
IDLE → (START) → CONNECT → (TCP_OPEN) → OPEN_SENT → (OPEN_RECEIVED) → OPEN_CONFIRM → (KEEPALIVE) → ESTABLISHED
```

### Common mistakes

- Forgetting that `ESTABLISHED + NOTIFICATION → IDLE` (session teardown).
- Returning `IDLE` for unknown states instead of `IDLE` (both correct, but make sure unknown states don't raise exceptions).
- Not handling `KEEPALIVE` in `ESTABLISHED` → `ESTABLISHED` (stay alive).

Student-mode coding target for this stage is `src/routeforge/runtime/bgp.py` (`bgp_session_transition`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/bgp.py`
- Symbols: `bgp_session_transition`
- Why this target: Drive BGP session FSM transitions.
- Stage check: `routeforge check lab21`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab21_bgp_session_fsm_and_transport`
3. Edit only the listed symbols in `src/routeforge/runtime/bgp.py`.
4. Run `routeforge check lab21` until it exits with status `0`.
5. Run `routeforge run lab21_bgp_session_fsm_and_transport --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab21_bgp_session_fsm_and_transport
routeforge check lab21

STATE=/tmp/routeforge-progress.json
routeforge run lab21_bgp_session_fsm_and_transport --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab21` passes when your implementation is complete for this stage.
- `bgp_open_and_establish` should print `[PASS]` (BGP OPEN and KEEPALIVE events transition the session to ESTABLISHED).
- `bgp_hold_timer_reset` should print `[PASS]` (hold timer expiry returns the BGP session to IDLE).
- Run output includes checkpoints: BGP_OPEN_RX, BGP_SESSION_CHANGE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab21_bgp_session_fsm_and_transport --state-file "$STATE" --trace-out /tmp/lab21_bgp_session_fsm_and_transport.jsonl
routeforge debug replay --trace /tmp/lab21_bgp_session_fsm_and_transport.jsonl
routeforge debug explain --trace /tmp/lab21_bgp_session_fsm_and_transport.jsonl --step bgp_open_and_establish
```

Checkpoint guide:

- `BGP_OPEN_RX`: A BGP OPEN message was received and the FSM was evaluated with the
  `OPEN_RECEIVED` event.  If missing, the scenario didn't reach the open-exchange step —
  check that the TCP_OPEN event first succeeds (CONNECT → OPEN_SENT).
- `BGP_SESSION_CHANGE`: The session state changed (e.g., IDLE → CONNECT, OPEN_SENT →
  OPEN_CONFIRM, or ESTABLISHED → IDLE).  If missing for a transition that should happen,
  your FSM returned the same state as the input instead of the expected next state.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/bgp.py` and rerun `routeforge check lab21` to confirm tests catch regressions.
- If `routeforge run lab21_bgp_session_fsm_and_transport --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 4271 (BGP-4).

