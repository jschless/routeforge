# Lab 32: Route Redistribution and Loop Prevention

## Learning objectives

- Implement `build_redistribution_tag, redistribute_with_loop_guard` in `src/routeforge/runtime/phase2.py`.
- Deliver `redist_import`: new route is imported into target protocol.
- Deliver `redist_tag_set`: redistributed route is tagged for loop prevention.
- Deliver `redist_loop_suppress`: re-seen tag is suppressed to prevent loops.
- Validate internal behavior through checkpoints: REDIST_IMPORT, TAG_SET, LOOP_SUPPRESS.

## Prerequisite recap

- Required prior labs: `lab31_qos_congestion_avoidance_wred`.
- Confirm target mapping before coding with `routeforge show lab32_route_redistribution_and_loop_prevention`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Controlled redistribution using protocol tags to stop feedback loops. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`build_redistribution_tag, redistribute_with_loop_guard`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbols: `build_redistribution_tag, redistribute_with_loop_guard`
- Why this target: build canonical tags and enforce one-time import loop guard behavior.
- Stage check: `routeforge check lab32`

Function contract for this stage:

- Symbol: `build_redistribution_tag(*, source_prefix: str, source_protocol: str) -> str`
- Required behavior: return uppercase canonical tag in `PROTOCOL:prefix` format
- Symbol: `redistribute_with_loop_guard(*, source_prefix: str, source_protocol: str, existing_tags: set[str]) -> tuple[set[str], Literal["IMPORT", "LOOP_SUPPRESS"]]`
- Required behavior: import once per canonical tag; suppress re-import when tag is already present

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab32_route_redistribution_and_loop_prevention`
3. Edit only `build_redistribution_tag, redistribute_with_loop_guard` in `src/routeforge/runtime/phase2.py`.
4. Run `routeforge check lab32` until it exits with status `0`.
5. Run `routeforge run lab32_route_redistribution_and_loop_prevention --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab32_route_redistribution_and_loop_prevention
routeforge check lab32

STATE=/tmp/routeforge-progress.json
routeforge run lab32_route_redistribution_and_loop_prevention --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab32` passes when your implementation is complete for this stage.
- `redist_import` should print `[PASS]` (new route is imported into target protocol).
- `redist_tag_set` should print `[PASS]` (redistributed route is tagged for loop prevention).
- `redist_loop_suppress` should print `[PASS]` (re-seen tag is suppressed to prevent loops).
- Run output includes checkpoints: REDIST_IMPORT, TAG_SET, LOOP_SUPPRESS.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab32_route_redistribution_and_loop_prevention --state-file "$STATE" --trace-out /tmp/lab32_route_redistribution_and_loop_prevention.jsonl
routeforge debug replay --trace /tmp/lab32_route_redistribution_and_loop_prevention.jsonl
routeforge debug explain --trace /tmp/lab32_route_redistribution_and_loop_prevention.jsonl --step redist_import
```

Checkpoint guide:

- `REDIST_IMPORT`: first expected pipeline milestone.
- `TAG_SET`: second expected pipeline milestone.
- `LOOP_SUPPRESS`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `build_redistribution_tag` or `redistribute_with_loop_guard` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab32` to confirm tests catch regressions.
- If `routeforge run lab32_route_redistribution_and_loop_prevention --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- Route redistribution loop prevention patterns.
