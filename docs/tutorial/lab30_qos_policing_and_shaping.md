# Lab 30: QoS Policing and Shaping

## Learning objectives

- Implement `apply_policer, qos_police_shape` in `src/routeforge/runtime/phase2.py`.
- Deliver `qos_police_rate`: traffic above CIR is policed.
- Deliver `qos_shape_queue`: excess traffic is queued by shaper.
- Deliver `qos_shape_release`: queued traffic is released at shape rate.
- Validate internal behavior through checkpoints: QOS_POLICE, QOS_SHAPE_QUEUE, QOS_SHAPE_RELEASE.

## Prerequisite recap

- Required prior labs: `lab29_port_security_and_ip_source_guard`.
- Confirm target mapping before coding with `routeforge show lab30_qos_policing_and_shaping`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Rate enforcement pipeline with police and shape stages. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`apply_policer, qos_police_shape`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbols: `apply_policer, qos_police_shape`
- Why this target: implement CIR policing logic and deterministic shaping release behavior.
- Stage check: `routeforge check lab30`

Function contract for this stage:

- Symbol: `apply_policer(*, offered_kbps: int, cir_kbps: int) -> int`
- Required behavior: return admitted rate at or below CIR with zero-floor normalization
- Symbol: `qos_police_shape(*, offered_kbps: int, cir_kbps: int, shape_rate_kbps: int) -> tuple[int, int]`
- Required behavior: return `(admitted, released)` where released is shape-limited from admitted

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab30_qos_policing_and_shaping`
3. Edit only `apply_policer, qos_police_shape` in `src/routeforge/runtime/phase2.py`.
4. Run `routeforge check lab30` until it exits with status `0`.
5. Run `routeforge run lab30_qos_policing_and_shaping --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab30_qos_policing_and_shaping
routeforge check lab30

STATE=/tmp/routeforge-progress.json
routeforge run lab30_qos_policing_and_shaping --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab30` passes when your implementation is complete for this stage.
- `qos_police_rate` should print `[PASS]` (traffic above CIR is policed).
- `qos_shape_queue` should print `[PASS]` (excess traffic is queued by shaper).
- `qos_shape_release` should print `[PASS]` (queued traffic is released at shape rate).
- Run output includes checkpoints: QOS_POLICE, QOS_SHAPE_QUEUE, QOS_SHAPE_RELEASE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab30_qos_policing_and_shaping --state-file "$STATE" --trace-out /tmp/lab30_qos_policing_and_shaping.jsonl
routeforge debug replay --trace /tmp/lab30_qos_policing_and_shaping.jsonl
routeforge debug explain --trace /tmp/lab30_qos_policing_and_shaping.jsonl --step qos_police_rate
```

Checkpoint guide:

- `QOS_POLICE`: first expected pipeline milestone.
- `QOS_SHAPE_QUEUE`: second expected pipeline milestone.
- `QOS_SHAPE_RELEASE`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `apply_policer` or `qos_police_shape` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab30` to confirm tests catch regressions.
- If `routeforge run lab30_qos_policing_and_shaping --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- Traffic policing and shaping principles.
