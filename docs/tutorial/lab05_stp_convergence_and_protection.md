# Lab 05: STP Convergence and Protection

## Learning objectives

- Implement `bpdu_guard_decision` in `src/routeforge/runtime/stp.py`.
- Deliver `stp_topology_change`: link failure triggers deterministic STP re-convergence.
- Deliver `stp_guard_action`: BPDU guard puts an edge port into errdisable state.
- Validate internal behavior through checkpoints: STP_TOPOLOGY_CHANGE, STP_GUARD_ACTION.

## Prerequisite recap

- Required prior labs: lab04_stp.
- Confirm target mapping before coding with `routeforge show lab05_stp_convergence_and_protection`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Topology change handling and protection semantics. Student-mode coding target for this stage is `src/routeforge/runtime/stp.py` (`bpdu_guard_decision`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/stp.py`
- Symbols: `bpdu_guard_decision`
- Why this target: Apply BPDU guard behavior on edge ports.
- Stage check: `routeforge check lab05`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab05_stp_convergence_and_protection`
3. Edit only the listed symbols in `src/routeforge/runtime/stp.py`.
4. Run `routeforge check lab05` until it exits with status `0`.
5. Run `routeforge run lab05_stp_convergence_and_protection --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab05_stp_convergence_and_protection
routeforge check lab05

STATE=/tmp/routeforge-progress.json
routeforge run lab05_stp_convergence_and_protection --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab05` passes when your implementation is complete for this stage.
- `stp_topology_change` should print `[PASS]` (link failure triggers deterministic STP re-convergence).
- `stp_guard_action` should print `[PASS]` (BPDU guard puts an edge port into errdisable state).
- Run output includes checkpoints: STP_TOPOLOGY_CHANGE, STP_GUARD_ACTION.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab05_stp_convergence_and_protection --state-file "$STATE" --trace-out /tmp/lab05_stp_convergence_and_protection.jsonl
routeforge debug replay --trace /tmp/lab05_stp_convergence_and_protection.jsonl
routeforge debug explain --trace /tmp/lab05_stp_convergence_and_protection.jsonl --step stp_topology_change
```

Checkpoint guide:

- `STP_TOPOLOGY_CHANGE`: Topology change handling and protection semantics.
- `STP_GUARD_ACTION`: Topology change handling and protection semantics.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/stp.py` and rerun `routeforge check lab05` to confirm tests catch regressions.
- If `routeforge run lab05_stp_convergence_and_protection --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IEEE 802.1D (bridging and STP fundamentals).
- IEEE 802.1Q (VLAN tagging and trunk behavior).

