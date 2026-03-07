# Lab 29: Port Security and IP Source Guard

## Learning objectives

- Implement `port_security_ip_source_guard` in `src/routeforge/runtime/phase2.py`.
- Deliver `portsec_learn`: first host is learned under port-security limit.
- Deliver `portsec_violation`: exceeding secure MAC limit triggers violation.
- Deliver `ipsg_deny`: invalid source IP is denied.
- Validate internal behavior through checkpoints: PORTSEC_LEARN, PORTSEC_VIOLATION, IPSG_DENY.

## Prerequisite recap

- Required prior labs: `lab28_dhcp_snooping_and_dai`.
- Confirm target mapping before coding with `routeforge show lab29_port_security_and_ip_source_guard`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Edge port identity controls with secure MAC and source validation. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`port_security_ip_source_guard`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbol: `port_security_ip_source_guard`
- Why this target: implement the core behavior required by the three lab steps.
- Stage check: `routeforge check lab29`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab29_port_security_and_ip_source_guard`
3. Edit only `port_security_ip_source_guard` in `src/routeforge/runtime/phase2.py`.
4. Run `routeforge check lab29` until it exits with status `0`.
5. Run `routeforge run lab29_port_security_and_ip_source_guard --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab29_port_security_and_ip_source_guard
routeforge check lab29

STATE=/tmp/routeforge-progress.json
routeforge run lab29_port_security_and_ip_source_guard --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab29` passes when your implementation is complete for this stage.
- `portsec_learn` should print `[PASS]` (first host is learned under port-security limit).
- `portsec_violation` should print `[PASS]` (exceeding secure MAC limit triggers violation).
- `ipsg_deny` should print `[PASS]` (invalid source IP is denied).
- Run output includes checkpoints: PORTSEC_LEARN, PORTSEC_VIOLATION, IPSG_DENY.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab29_port_security_and_ip_source_guard --state-file "$STATE" --trace-out /tmp/lab29_port_security_and_ip_source_guard.jsonl
routeforge debug replay --trace /tmp/lab29_port_security_and_ip_source_guard.jsonl
routeforge debug explain --trace /tmp/lab29_port_security_and_ip_source_guard.jsonl --step portsec_learn
```

Checkpoint guide:

- `PORTSEC_LEARN`: first expected pipeline milestone.
- `PORTSEC_VIOLATION`: second expected pipeline milestone.
- `IPSG_DENY`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `port_security_ip_source_guard` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab29` to confirm tests catch regressions.
- If `routeforge run lab29_port_security_and_ip_source_guard --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- Port security and IP source guard behavior.
