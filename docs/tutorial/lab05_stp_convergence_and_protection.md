# Lab 05: STP Convergence and Protection

## Learning objectives

- Implement `role_changes, bpdu_guard_decision` in `src/routeforge/runtime/stp.py`.
- Deliver `stp_topology_change`: link failure triggers deterministic STP re-convergence.
- Deliver `stp_guard_action`: BPDU guard puts an edge port into errdisable state.
- Validate internal behavior through checkpoints: STP_TOPOLOGY_CHANGE, STP_GUARD_ACTION.

## Prerequisite recap

- Required prior labs: lab04_stp.
- Confirm target mapping before coding with `routeforge show lab05_stp_convergence_and_protection`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### STP topology change (re-convergence)

When a link fails, the bridges on adjacent segments detect the loss and must re-run STP to elect a new tree.  This lab simulates that by removing a link with `remove_link()` and calling `compute_stp()` again — an *alternate* port that was blocking can become the new designated or root port.

### BPDU Guard

*Edge ports* connect to end-hosts (PCs, servers), not to other switches.  End-hosts should never send BPDUs.  If a BPDU arrives on an edge port, it means someone connected a rogue switch — BPDU Guard shuts the port down immediately (`ERR_DISABLE`) to prevent loops.

### What correct behavior looks like

- `bpdu_guard_decision(port=("sw1","eth0"), edge_port=True, bpdu_received=True)`:
  → `GuardDecision(port=("sw1","eth0"), action="ERR_DISABLE", reason="BPDU_GUARD_VIOLATION")`
- `bpdu_guard_decision(port=("sw1","eth1"), edge_port=True, bpdu_received=False)`:
  → `GuardDecision(port=("sw1","eth1"), action="ALLOW", reason="OK")`
- `bpdu_guard_decision(port=("sw1","eth2"), edge_port=False, bpdu_received=True)`:
  → `GuardDecision(port=("sw1","eth2"), action="ALLOW", reason="OK")` (non-edge, expected to see BPDUs)

Student-mode coding target for this stage is `src/routeforge/runtime/stp.py` (`role_changes, bpdu_guard_decision`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/stp.py`
- Symbols: `role_changes, bpdu_guard_decision`
- Why this target: Compute reconvergence role deltas and enforce BPDU guard control-plane safety.
- Stage check: `routeforge check lab05`

Function contract for this stage:

- Symbol: `role_changes(previous: STPResult, current: STPResult) -> dict[tuple[str, str], tuple[str, str]]`
- Required behavior: include every port role transition, and map missing ports as `DOWN`
- Symbol: `bpdu_guard_decision(*, port: tuple[str, str], edge_port: bool, bpdu_received: bool) -> GuardDecision`
- Required outputs: `ERRDISABLE/STP_BPDU_GUARD_TRIPPED` for edge+BPDU, otherwise `FORWARD/STP_GUARD_CLEAR`

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

- `STP_TOPOLOGY_CHANGE`: Re-convergence completed after a link removal — `role_changes()`
  detected that at least one port changed role (e.g., ALTERNATE → DESIGNATED).  If missing,
  `compute_stp()` may be returning identical roles as before the link was removed, or
  `role_changes()` is not being called to detect the difference.
- `STP_GUARD_ACTION`: `bpdu_guard_decision()` produced an `ERR_DISABLE` action for an edge
  port that received a BPDU.  If missing, check that your implementation returns
  `ERR_DISABLE` (not `ALLOW`) when `edge_port=True` and `bpdu_received=True`.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/stp.py` and rerun `routeforge check lab05` to confirm tests catch regressions.
- If `routeforge run lab05_stp_convergence_and_protection --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IEEE 802.1D (bridging and STP fundamentals).
- IEEE 802.1Q (VLAN tagging and trunk behavior).

