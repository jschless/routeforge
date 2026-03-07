# Lab 31: QoS Congestion Avoidance (WRED)

## Learning objectives

- Implement `wred_decision_profile, qos_wred_decision` in `src/routeforge/runtime/phase2.py`.
- Deliver `qos_wred_profile`: WRED profile activates above minimum threshold.
- Deliver `qos_ecn_mark`: ECN-capable flow is marked before hard drop.
- Deliver `qos_wred_drop`: queue beyond max threshold is dropped.
- Validate internal behavior through checkpoints: QOS_WRED_PROFILE, QOS_ECN_MARK, QOS_WRED_DROP.

## Prerequisite recap

- Required prior labs: `lab30_qos_policing_and_shaping`.
- Confirm target mapping before coding with `routeforge show lab31_qos_congestion_avoidance_wred`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Congestion avoidance with deterministic threshold actions. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`wred_decision_profile, qos_wred_decision`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbols: `wred_decision_profile, qos_wred_decision`
- Why this target: classify queue-depth thresholds first, then resolve FORWARD/MARK/DROP action.
- Stage check: `routeforge check lab31`

Function contract for this stage:

- Symbol: `wred_decision_profile(*, queue_depth: int, min_threshold: int, max_threshold: int) -> Literal["BELOW_MIN", "BETWEEN_THRESHOLDS", "AT_OR_ABOVE_MAX"]`
- Required behavior: classify queue depth into one deterministic threshold profile
- Symbol: `qos_wred_decision(*, queue_depth: int, min_threshold: int, max_threshold: int, ecn_capable: bool) -> Literal["FORWARD", "MARK", "DROP"]`
- Required behavior: map profile + ECN capability into deterministic congestion action

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab31_qos_congestion_avoidance_wred`
3. Edit only `wred_decision_profile, qos_wred_decision` in `src/routeforge/runtime/phase2.py`.
4. Run `routeforge check lab31` until it exits with status `0`.
5. Run `routeforge run lab31_qos_congestion_avoidance_wred --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab31_qos_congestion_avoidance_wred
routeforge check lab31

STATE=/tmp/routeforge-progress.json
routeforge run lab31_qos_congestion_avoidance_wred --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab31` passes when your implementation is complete for this stage.
- `qos_wred_profile` should print `[PASS]` (WRED profile activates above minimum threshold).
- `qos_ecn_mark` should print `[PASS]` (ECN-capable flow is marked before hard drop).
- `qos_wred_drop` should print `[PASS]` (queue beyond max threshold is dropped).
- Run output includes checkpoints: QOS_WRED_PROFILE, QOS_ECN_MARK, QOS_WRED_DROP.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab31_qos_congestion_avoidance_wred --state-file "$STATE" --trace-out /tmp/lab31_qos_congestion_avoidance_wred.jsonl
routeforge debug replay --trace /tmp/lab31_qos_congestion_avoidance_wred.jsonl
routeforge debug explain --trace /tmp/lab31_qos_congestion_avoidance_wred.jsonl --step qos_wred_profile
```

Checkpoint guide:

- `QOS_WRED_PROFILE`: first expected pipeline milestone.
- `QOS_ECN_MARK`: second expected pipeline milestone.
- `QOS_WRED_DROP`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `wred_decision_profile` or `qos_wred_decision` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab31` to confirm tests catch regressions.
- If `routeforge run lab31_qos_congestion_avoidance_wred --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- WRED and ECN congestion management.
