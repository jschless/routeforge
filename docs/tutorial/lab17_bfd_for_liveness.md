# Lab 17: BFD for Liveness

## Learning objectives

- Implement `BfdSession.tick` in `src/routeforge/runtime/bfd.py`.
- Deliver `bfd_control_rx`: BFD control packet raises session to UP.
- Deliver `bfd_timeout`: missing control packets trigger deterministic timeout.
- Validate internal behavior through checkpoints: BFD_CONTROL_RX, BFD_STATE_CHANGE, BFD_TIMEOUT.

## Prerequisite recap

- Required prior labs: lab16_udp_tcp_fundamentals.
- Confirm target mapping before coding with `routeforge show lab17_bfd_for_liveness`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

BFD session state and timeout behavior feeding control reactions. Student-mode coding target for this stage is `src/routeforge/runtime/bfd.py` (`BfdSession.tick`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/bfd.py`
- Symbols: `BfdSession.tick`
- Why this target: Detect BFD timeout behavior deterministically.
- Stage check: `routeforge check lab17`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab17_bfd_for_liveness`
3. Edit only the listed symbols in `src/routeforge/runtime/bfd.py`.
4. Run `routeforge check lab17` until it exits with status `0`.
5. Run `routeforge run lab17_bfd_for_liveness --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab17_bfd_for_liveness
routeforge check lab17

STATE=/tmp/routeforge-progress.json
routeforge run lab17_bfd_for_liveness --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab17` passes when your implementation is complete for this stage.
- `bfd_control_rx` should print `[PASS]` (BFD control packet raises session to UP).
- `bfd_timeout` should print `[PASS]` (missing control packets trigger deterministic timeout).
- Run output includes checkpoints: BFD_CONTROL_RX, BFD_STATE_CHANGE, BFD_TIMEOUT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab17_bfd_for_liveness --state-file "$STATE" --trace-out /tmp/lab17_bfd_for_liveness.jsonl
routeforge debug replay --trace /tmp/lab17_bfd_for_liveness.jsonl
routeforge debug explain --trace /tmp/lab17_bfd_for_liveness.jsonl --step bfd_control_rx
```

Checkpoint guide:

- `BFD_CONTROL_RX`: BFD session state and timeout behavior feeding control reactions.
- `BFD_STATE_CHANGE`: BFD session state and timeout behavior feeding control reactions.
- `BFD_TIMEOUT`: BFD session state and timeout behavior feeding control reactions.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/bfd.py` and rerun `routeforge check lab17` to confirm tests catch regressions.
- If `routeforge run lab17_bfd_for_liveness --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 5880 (BFD base specification).

## Concept Deepening Notes

BFD is primarily about timer-driven liveness confidence. Correctness requires predictable transitions under control reception and timeout paths, with no hidden state jumps. Deterministic timeout handling is essential because routing failover policy later assumes BFD state is trustworthy and not oscillating.

## Checkpoint Guide (Expanded)

- `BFD_CONTROL_RX`: Confirm this marker appears when your implementation follows the intended decision path.
- `BFD_STATE_CHANGE`: Confirm this marker appears when your implementation follows the intended decision path.
- `BFD_TIMEOUT`: Confirm this marker appears when your implementation follows the intended decision path.
