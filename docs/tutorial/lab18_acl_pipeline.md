# Lab 18: ACL Pipeline

## Learning objectives

- Implement `evaluate_acl` in `src/routeforge/runtime/policy_acl.py`.
- Deliver `acl_permit`: permit rule matches before implicit deny.
- Deliver `acl_deny`: non-matching traffic is denied deterministically.
- Validate internal behavior through checkpoints: ACL_EVALUATE, ACL_PERMIT, ACL_DENY.

## Prerequisite recap

- Required prior labs: lab17_bfd_for_liveness.
- Confirm target mapping before coding with `routeforge show lab18_acl_pipeline`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

ACL first-match ordered evaluation and implicit deny. Student-mode coding target for this stage is `src/routeforge/runtime/policy_acl.py` (`evaluate_acl`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/policy_acl.py`
- Symbols: `evaluate_acl`
- Why this target: Evaluate ACLs with first-match semantics.
- Stage check: `routeforge check lab18`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab18_acl_pipeline`
3. Edit only the listed symbols in `src/routeforge/runtime/policy_acl.py`.
4. Run `routeforge check lab18` until it exits with status `0`.
5. Run `routeforge run lab18_acl_pipeline --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab18_acl_pipeline
routeforge check lab18

STATE=/tmp/routeforge-progress.json
routeforge run lab18_acl_pipeline --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab18` passes when your implementation is complete for this stage.
- `acl_permit` should print `[PASS]` (permit rule matches before implicit deny).
- `acl_deny` should print `[PASS]` (non-matching traffic is denied deterministically).
- Run output includes checkpoints: ACL_EVALUATE, ACL_PERMIT, ACL_DENY.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab18_acl_pipeline --state-file "$STATE" --trace-out /tmp/lab18_acl_pipeline.jsonl
routeforge debug replay --trace /tmp/lab18_acl_pipeline.jsonl
routeforge debug explain --trace /tmp/lab18_acl_pipeline.jsonl --step acl_permit
```

Checkpoint guide:

- `ACL_EVALUATE`: ACL first-match ordered evaluation and implicit deny.
- `ACL_PERMIT`: ACL first-match ordered evaluation and implicit deny.
- `ACL_DENY`: ACL first-match ordered evaluation and implicit deny.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/policy_acl.py` and rerun `routeforge check lab18` to confirm tests catch regressions.
- If `routeforge run lab18_acl_pipeline --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- Ordered first-match ACL evaluation patterns used by routers/firewalls.

