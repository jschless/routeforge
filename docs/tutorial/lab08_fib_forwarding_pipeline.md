# Lab 08: FIB Forwarding Pipeline

## Learning objectives

- Implement `forward_packet` in `src/routeforge/runtime/l3.py`.
- Deliver `fib_forward_and_ttl`: FIB hit forwards packet and decrements TTL.
- Deliver `fib_drop_no_route`: FIB miss drops packet with deterministic reason.
- Validate internal behavior through checkpoints: TTL_DECREMENT, FIB_FORWARD, FIB_DROP.

## Prerequisite recap

- Required prior labs: lab07_ipv4_subnet_and_rib.
- Confirm target mapping before coding with `routeforge show lab08_fib_forwarding_pipeline`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

FIB forwarding pipeline with TTL decrement and drop reasons. Student-mode coding target for this stage is `src/routeforge/runtime/l3.py` (`forward_packet`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/l3.py`
- Symbols: `forward_packet`
- Why this target: Build forwarding/drop decisions with TTL handling.
- Stage check: `routeforge check lab08`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab08_fib_forwarding_pipeline`
3. Edit only the listed symbols in `src/routeforge/runtime/l3.py`.
4. Run `routeforge check lab08` until it exits with status `0`.
5. Run `routeforge run lab08_fib_forwarding_pipeline --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab08_fib_forwarding_pipeline
routeforge check lab08

STATE=/tmp/routeforge-progress.json
routeforge run lab08_fib_forwarding_pipeline --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab08` passes when your implementation is complete for this stage.
- `fib_forward_and_ttl` should print `[PASS]` (FIB hit forwards packet and decrements TTL).
- `fib_drop_no_route` should print `[PASS]` (FIB miss drops packet with deterministic reason).
- Run output includes checkpoints: TTL_DECREMENT, FIB_FORWARD, FIB_DROP.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab08_fib_forwarding_pipeline --state-file "$STATE" --trace-out /tmp/lab08_fib_forwarding_pipeline.jsonl
routeforge debug replay --trace /tmp/lab08_fib_forwarding_pipeline.jsonl
routeforge debug explain --trace /tmp/lab08_fib_forwarding_pipeline.jsonl --step fib_forward_and_ttl
```

Checkpoint guide:

- `TTL_DECREMENT`: FIB forwarding pipeline with TTL decrement and drop reasons.
- `FIB_FORWARD`: FIB forwarding pipeline with TTL decrement and drop reasons.
- `FIB_DROP`: FIB forwarding pipeline with TTL decrement and drop reasons.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/l3.py` and rerun `routeforge check lab08` to confirm tests catch regressions.
- If `routeforge run lab08_fib_forwarding_pipeline --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 791 (IPv4).
- RFC 792 (ICMP).
- RFC 826 (ARP).

## Concept Deepening Notes

FIB behavior should separate selection from disposition. First determine whether a route exists and what next hop/interface it implies; then apply TTL and drop policy. Keeping this split clear makes ICMP and diagnostics labs easier because each control response can map to a specific forwarding-stage decision.

## Checkpoint Guide (Expanded)

- `TTL_DECREMENT`: Confirm this marker appears when your implementation follows the intended decision path.
- `FIB_FORWARD`: Confirm this marker appears when your implementation follows the intended decision path.
- `FIB_DROP`: Confirm this marker appears when your implementation follows the intended decision path.
