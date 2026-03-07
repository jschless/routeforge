# Lab 27: Capstone Incident Drill

## Learning objectives

- Implement `apply_step` in `src/routeforge/runtime/capstone.py`.
- Deliver `scenario_step_apply`: incident step applies deterministic failover route and alarm state.
- Deliver `scenario_convergence_assert`: recovery step clears alarms and returns control plane to baseline.
- Validate internal behavior through checkpoints: SCENARIO_STEP_APPLY, CONVERGENCE_ASSERT.

## Prerequisite recap

- Required prior labs: lab26_observability_and_ops.
- Confirm target mapping before coding with `routeforge show lab27_capstone_incident_drill`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Scenario-driven multi-protocol failure/recovery and convergence assertions. Student-mode coding target for this stage is `src/routeforge/runtime/capstone.py` (`apply_step`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/capstone.py`
- Symbols: `apply_step`
- Why this target: Apply incident/recovery state transitions deterministically.
- Stage check: `routeforge check lab27`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab27_capstone_incident_drill`
3. Edit only the listed symbols in `src/routeforge/runtime/capstone.py`.
4. Run `routeforge check lab27` until it exits with status `0`.
5. Run `routeforge run lab27_capstone_incident_drill --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab27_capstone_incident_drill
routeforge check lab27

STATE=/tmp/routeforge-progress.json
routeforge run lab27_capstone_incident_drill --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab27` passes when your implementation is complete for this stage.
- `scenario_step_apply` should print `[PASS]` (incident step applies deterministic failover route and alarm state).
- `scenario_convergence_assert` should print `[PASS]` (recovery step clears alarms and returns control plane to baseline).
- Run output includes checkpoints: SCENARIO_STEP_APPLY, CONVERGENCE_ASSERT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab27_capstone_incident_drill --state-file "$STATE" --trace-out /tmp/lab27_capstone_incident_drill.jsonl
routeforge debug replay --trace /tmp/lab27_capstone_incident_drill.jsonl
routeforge debug explain --trace /tmp/lab27_capstone_incident_drill.jsonl --step scenario_step_apply
```

Checkpoint guide:

- `SCENARIO_STEP_APPLY`: Scenario-driven multi-protocol failure/recovery and convergence assertions.
- `CONVERGENCE_ASSERT`: Scenario-driven multi-protocol failure/recovery and convergence assertions.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/capstone.py` and rerun `routeforge check lab27` to confirm tests catch regressions.
- If `routeforge run lab27_capstone_incident_drill --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- Incident response runbook patterns and deterministic post-incident verification.

