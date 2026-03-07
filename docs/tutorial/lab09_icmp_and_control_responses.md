# Lab 09: ICMP and Control Responses

## Learning objectives

- Implement `icmp_control` in `src/routeforge/runtime/l3.py`.
- Deliver `icmp_echo_reply`: ICMP echo request returns deterministic echo reply.
- Deliver `icmp_unreachable`: missing route produces ICMP unreachable.
- Deliver `icmp_time_exceeded`: TTL expiry produces ICMP time exceeded.
- Validate internal behavior through checkpoints: ICMP_ECHO_REPLY, ICMP_UNREACHABLE, ICMP_TIME_EXCEEDED.

## Prerequisite recap

- Required prior labs: lab08_fib_forwarding_pipeline.
- Confirm target mapping before coding with `routeforge show lab09_icmp_and_control_responses`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

ICMP echo, unreachable, and time-exceeded behavior. Student-mode coding target for this stage is `src/routeforge/runtime/l3.py` (`icmp_control`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/l3.py`
- Symbols: `icmp_control`
- Why this target: Generate ICMP control-plane responses for echo, no-route, and TTL expiry.
- Stage check: `routeforge check lab09`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab09_icmp_and_control_responses`
3. Edit only the listed symbols in `src/routeforge/runtime/l3.py`.
4. Run `routeforge check lab09` until it exits with status `0`.
5. Run `routeforge run lab09_icmp_and_control_responses --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab09_icmp_and_control_responses
routeforge check lab09

STATE=/tmp/routeforge-progress.json
routeforge run lab09_icmp_and_control_responses --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab09` passes when your implementation is complete for this stage.
- `icmp_echo_reply` should print `[PASS]` (ICMP echo request returns deterministic echo reply).
- `icmp_unreachable` should print `[PASS]` (missing route produces ICMP unreachable).
- `icmp_time_exceeded` should print `[PASS]` (TTL expiry produces ICMP time exceeded).
- Run output includes checkpoints: ICMP_ECHO_REPLY, ICMP_UNREACHABLE, ICMP_TIME_EXCEEDED.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab09_icmp_and_control_responses --state-file "$STATE" --trace-out /tmp/lab09_icmp_and_control_responses.jsonl
routeforge debug replay --trace /tmp/lab09_icmp_and_control_responses.jsonl
routeforge debug explain --trace /tmp/lab09_icmp_and_control_responses.jsonl --step icmp_echo_reply
```

Checkpoint guide:

- `ICMP_ECHO_REPLY`: ICMP echo, unreachable, and time-exceeded behavior.
- `ICMP_UNREACHABLE`: ICMP echo, unreachable, and time-exceeded behavior.
- `ICMP_TIME_EXCEEDED`: ICMP echo, unreachable, and time-exceeded behavior.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/l3.py` and rerun `routeforge check lab09` to confirm tests catch regressions.
- If `routeforge run lab09_icmp_and_control_responses --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 791 (IPv4).
- RFC 792 (ICMP).
- RFC 826 (ARP).

