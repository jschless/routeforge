# Lab 27: Capstone Incident Drill

## Learning objectives

- Apply scenario steps that model multi-protocol incident response.
- Validate deterministic failover and recovery states.
- Assert end-state convergence against baseline expectations.

## Prerequisite recap

- Complete `lab26_observability_and_ops`.
- Recall BFD, OSPF, and BGP interactions from labs `17`, `15`, and `21-24`.

## Concept walkthrough

`lab27` combines control-plane and operations thinking. An incident step introduces failure state, then a recovery step restores baseline reachability and clears alarms.

## Implementation TODO map

- `src/routeforge/runtime/capstone.py`: scenario state and convergence assertion helpers.
- `src/routeforge/labs/exercises.py`: incident apply/recover scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab27_capstone_incident_drill --completed <all-labs-lab01-through-lab26>
```

Expected:

- `scenario_step_apply` step `PASS`.
- `scenario_convergence_assert` step `PASS`.
- Checkpoints include `SCENARIO_STEP_APPLY` and `CONVERGENCE_ASSERT`.

## Debug trace checkpoints and interpretation guidance

- `SCENARIO_STEP_APPLY`: fault/failover step applied.
- `CONVERGENCE_ASSERT`: final routes and alarms match target state.

## Failure drills and troubleshooting flow

- Keep alarm uncleared in recovery step and confirm convergence assertion fails.
- Restore wrong primary route and confirm baseline-stability check fails.

## Standards and references

- Incident response game-day patterns and deterministic post-incident validation.
