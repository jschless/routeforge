# Lab 26: Observability and Operations

## Learning objectives

- Perform deterministic readiness checks across subsystems.
- Emit telemetry in stable, parseable structure.
- Correlate health and telemetry outputs for operations workflows.

## Prerequisite recap

- Complete `lab25_tunnels_and_ipsec`.
- Recall deterministic troubleshooting outputs from `lab10`.

## Concept walkthrough

`lab26` is an operations-focused lab. It validates readiness state and emits normalized telemetry payloads that support repeatable monitoring and checks.

## Implementation TODO map

- `src/routeforge/runtime/observability.py`: readiness and telemetry helpers.
- `src/routeforge/labs/exercises.py`: operations health + telemetry scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab26_observability_and_ops --completed <all-labs-lab01-through-lab25>
```

Expected:

- `ops_readiness_check` step `PASS`.
- `ops_telemetry_emit` step `PASS`.
- Checkpoints include `OPS_READINESS_CHECK` and `TELEMETRY_EMIT`.

## Debug trace checkpoints and interpretation guidance

- `OPS_READINESS_CHECK`: deterministic pass/fail status per subsystem.
- `TELEMETRY_EMIT`: sorted counter payload for stable parsing.

## Failure drills and troubleshooting flow

- Force a failed readiness probe and verify failed check names are listed.
- Change telemetry counters and confirm structure remains stable.

## Standards and references

- Operations telemetry and SRE readiness-check design patterns.
