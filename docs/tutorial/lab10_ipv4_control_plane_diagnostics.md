# Lab 10: IPv4 Diagnostics

## Learning objectives

- Implement `explain_drop` in `src/routeforge/runtime/l3.py`.
- Deliver `diagnostic_explain`: explain output exposes deterministic drop reason.
- Deliver `diagnostic_assert_reason`: drop reason assertion matches expected behavior.
- Validate internal behavior through checkpoints: EXPLAIN_CHECKPOINT, DROP_REASON_ASSERT.

## Prerequisite recap

- Required prior labs: lab09_icmp_and_control_responses.
- Confirm target mapping before coding with `routeforge show lab10_ipv4_control_plane_diagnostics`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Deterministic troubleshooting and explainability checkpoints. Student-mode coding target for this stage is `src/routeforge/runtime/l3.py` (`explain_drop`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/l3.py`
- Symbols: `explain_drop`
- Why this target: Explain deterministic drop reasons for diagnostics.
- Stage check: `routeforge check lab10`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab10_ipv4_control_plane_diagnostics`
3. Edit only the listed symbols in `src/routeforge/runtime/l3.py`.
4. Run `routeforge check lab10` until it exits with status `0`.
5. Run `routeforge run lab10_ipv4_control_plane_diagnostics --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab10_ipv4_control_plane_diagnostics
routeforge check lab10

STATE=/tmp/routeforge-progress.json
routeforge run lab10_ipv4_control_plane_diagnostics --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab10` passes when your implementation is complete for this stage.
- `diagnostic_explain` should print `[PASS]` (explain output exposes deterministic drop reason).
- `diagnostic_assert_reason` should print `[PASS]` (drop reason assertion matches expected behavior).
- Run output includes checkpoints: EXPLAIN_CHECKPOINT, DROP_REASON_ASSERT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab10_ipv4_control_plane_diagnostics --state-file "$STATE" --trace-out /tmp/lab10_ipv4_control_plane_diagnostics.jsonl
routeforge debug replay --trace /tmp/lab10_ipv4_control_plane_diagnostics.jsonl
routeforge debug explain --trace /tmp/lab10_ipv4_control_plane_diagnostics.jsonl --step diagnostic_explain
```

Checkpoint guide:

- `EXPLAIN_CHECKPOINT`: Deterministic troubleshooting and explainability checkpoints.
- `DROP_REASON_ASSERT`: Deterministic troubleshooting and explainability checkpoints.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/l3.py` and rerun `routeforge check lab10` to confirm tests catch regressions.
- If `routeforge run lab10_ipv4_control_plane_diagnostics --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 791 (IPv4).
- RFC 792 (ICMP).
- RFC 826 (ARP).

