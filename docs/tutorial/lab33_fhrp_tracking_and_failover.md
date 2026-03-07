# Lab 33: FHRP Tracking and Failover

## Learning objectives

- Implement `fhrp_track_failover` in `src/routeforge/runtime/phase2.py`.
- Deliver `fhrp_active_initial`: primary router is initially active.
- Deliver `fhrp_track_failover`: tracked failure triggers failover.
- Deliver `fhrp_preempt_recover`: primary preempts after recovery.
- Validate internal behavior through checkpoints: FHRP_ACTIVE_CHANGE, TRACK_DOWN, FHRP_PREEMPT.

## Prerequisite recap

- Required prior labs: `lab32_route_redistribution_and_loop_prevention`.
- Confirm target mapping before coding with `routeforge show lab33_fhrp_tracking_and_failover`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

First-hop redundancy behavior under tracked object failures. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`fhrp_track_failover`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbol: `fhrp_track_failover`
- Why this target: implement the core behavior required by the three lab steps.
- Stage check: `routeforge check lab33`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab33_fhrp_tracking_and_failover`
3. Edit only `fhrp_track_failover` in `src/routeforge/runtime/phase2.py`.
4. Run `routeforge check lab33` until it exits with status `0`.
5. Run `routeforge run lab33_fhrp_tracking_and_failover --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab33_fhrp_tracking_and_failover
routeforge check lab33

STATE=/tmp/routeforge-progress.json
routeforge run lab33_fhrp_tracking_and_failover --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab33` passes when your implementation is complete for this stage.
- `fhrp_active_initial` should print `[PASS]` (primary router is initially active).
- `fhrp_track_failover` should print `[PASS]` (tracked failure triggers failover).
- `fhrp_preempt_recover` should print `[PASS]` (primary preempts after recovery).
- Run output includes checkpoints: FHRP_ACTIVE_CHANGE, TRACK_DOWN, FHRP_PREEMPT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab33_fhrp_tracking_and_failover --state-file "$STATE" --trace-out /tmp/lab33_fhrp_tracking_and_failover.jsonl
routeforge debug replay --trace /tmp/lab33_fhrp_tracking_and_failover.jsonl
routeforge debug explain --trace /tmp/lab33_fhrp_tracking_and_failover.jsonl --step fhrp_active_initial
```

Checkpoint guide:

- `FHRP_ACTIVE_CHANGE`: first expected pipeline milestone.
- `TRACK_DOWN`: second expected pipeline milestone.
- `FHRP_PREEMPT`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `fhrp_track_failover` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab33` to confirm tests catch regressions.
- If `routeforge run lab33_fhrp_tracking_and_failover --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- FHRP tracking and preemption semantics.
