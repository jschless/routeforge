# Lab 22: BGP Attributes and Best Path

## Learning objectives

- Implement `select_best_path` in `src/routeforge/runtime/bgp.py`.
- Deliver `bgp_update_receive`: BGP update set is ingested for best-path selection.
- Deliver `bgp_best_path_select`: deterministic best-path logic selects expected candidate.
- Validate internal behavior through checkpoints: BGP_UPDATE_RX, BGP_BEST_PATH.

## Prerequisite recap

- Required prior labs: lab21_bgp_session_fsm_and_transport.
- Confirm target mapping before coding with `routeforge show lab22_bgp_attributes_and_bestpath`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Deterministic best-path selection over core attributes/tie-breakers. Student-mode coding target for this stage is `src/routeforge/runtime/bgp.py` (`select_best_path`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/bgp.py`
- Symbols: `select_best_path`
- Why this target: Select deterministic BGP best path from candidates.
- Stage check: `routeforge check lab22`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab22_bgp_attributes_and_bestpath`
3. Edit only the listed symbols in `src/routeforge/runtime/bgp.py`.
4. Run `routeforge check lab22` until it exits with status `0`.
5. Run `routeforge run lab22_bgp_attributes_and_bestpath --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab22_bgp_attributes_and_bestpath
routeforge check lab22

STATE=/tmp/routeforge-progress.json
routeforge run lab22_bgp_attributes_and_bestpath --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab22` passes when your implementation is complete for this stage.
- `bgp_update_receive` should print `[PASS]` (BGP update set is ingested for best-path selection).
- `bgp_best_path_select` should print `[PASS]` (deterministic best-path logic selects expected candidate).
- Run output includes checkpoints: BGP_UPDATE_RX, BGP_BEST_PATH.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab22_bgp_attributes_and_bestpath --state-file "$STATE" --trace-out /tmp/lab22_bgp_attributes_and_bestpath.jsonl
routeforge debug replay --trace /tmp/lab22_bgp_attributes_and_bestpath.jsonl
routeforge debug explain --trace /tmp/lab22_bgp_attributes_and_bestpath.jsonl --step bgp_update_receive
```

Checkpoint guide:

- `BGP_UPDATE_RX`: Deterministic best-path selection over core attributes/tie-breakers.
- `BGP_BEST_PATH`: Deterministic best-path selection over core attributes/tie-breakers.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/bgp.py` and rerun `routeforge check lab22` to confirm tests catch regressions.
- If `routeforge run lab22_bgp_attributes_and_bestpath --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 4271 (BGP-4).

