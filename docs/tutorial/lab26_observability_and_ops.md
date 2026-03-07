# Lab 26: Observability and Operations

## Learning objectives

- Implement `readiness_check, emit_telemetry` in `src/routeforge/runtime/observability.py`.
- Deliver `ops_readiness_check`: service health checks produce deterministic readiness status.
- Deliver `ops_telemetry_emit`: telemetry export emits sorted counter payload for reproducible parsing.
- Validate internal behavior through checkpoints: OPS_READINESS_CHECK, TELEMETRY_EMIT.

## Prerequisite recap

- Required prior labs: lab25_tunnels_and_ipsec.
- Confirm target mapping before coding with `routeforge show lab26_observability_and_ops`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Operational telemetry/readiness checks with deterministic outputs. Student-mode coding target for this stage is `src/routeforge/runtime/observability.py` (`readiness_check, emit_telemetry`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/observability.py`
- Symbols: `readiness_check, emit_telemetry`
- Why this target: Build deterministic readiness and telemetry outputs for operations workflows.
- Stage check: `routeforge check lab26`

Function contract for this stage:

- Symbol: `readiness_check(*, checks: dict[str, bool]) -> ReadinessResult`
- Required behavior: sort failing check names and return `ready=False` when any fail
- Symbol: `emit_telemetry(*, component: str, counters: dict[str, int], timestamp_s: int) -> dict[str, object]`
- Required behavior: emit counters in stable key order and preserve component/timestamp

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab26_observability_and_ops`
3. Edit only the listed symbols in `src/routeforge/runtime/observability.py`.
4. Run `routeforge check lab26` until it exits with status `0`.
5. Run `routeforge run lab26_observability_and_ops --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab26_observability_and_ops
routeforge check lab26

STATE=/tmp/routeforge-progress.json
routeforge run lab26_observability_and_ops --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab26` passes when your implementation is complete for this stage.
- `ops_readiness_check` should print `[PASS]` (service health checks produce deterministic readiness status).
- `ops_telemetry_emit` should print `[PASS]` (telemetry export emits sorted counter payload for reproducible parsing).
- Run output includes checkpoints: OPS_READINESS_CHECK, TELEMETRY_EMIT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab26_observability_and_ops --state-file "$STATE" --trace-out /tmp/lab26_observability_and_ops.jsonl
routeforge debug replay --trace /tmp/lab26_observability_and_ops.jsonl
routeforge debug explain --trace /tmp/lab26_observability_and_ops.jsonl --step ops_readiness_check
```

Checkpoint guide:

- `OPS_READINESS_CHECK`: Operational telemetry/readiness checks with deterministic outputs.
- `TELEMETRY_EMIT`: Operational telemetry/readiness checks with deterministic outputs.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/observability.py` and rerun `routeforge check lab26` to confirm tests catch regressions.
- If `routeforge run lab26_observability_and_ops --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- Operational readiness checks, telemetry hygiene, and deterministic output contracts.
