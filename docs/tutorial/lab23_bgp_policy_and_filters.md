# Lab 23: BGP Policy and Filters

## Learning objectives

- Implement `apply_export_policy` in `src/routeforge/runtime/bgp.py`.
- Deliver `bgp_policy_apply`: export policy filters denied prefixes deterministically.
- Deliver `bgp_update_export`: allowed routes are exported with policy-applied attributes.
- Validate internal behavior through checkpoints: BGP_POLICY_APPLY, BGP_UPDATE_EXPORT.

## Prerequisite recap

- Required prior labs: lab22_bgp_attributes_and_bestpath.
- Confirm target mapping before coding with `routeforge show lab23_bgp_policy_and_filters`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Import/export controls with prefix, AS-path, and community policy. Student-mode coding target for this stage is `src/routeforge/runtime/bgp.py` (`apply_export_policy`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/bgp.py`
- Symbols: `apply_export_policy`
- Why this target: Apply outbound policy filters and attribute rewrites.
- Stage check: `routeforge check lab23`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab23_bgp_policy_and_filters`
3. Edit only the listed symbols in `src/routeforge/runtime/bgp.py`.
4. Run `routeforge check lab23` until it exits with status `0`.
5. Run `routeforge run lab23_bgp_policy_and_filters --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab23_bgp_policy_and_filters
routeforge check lab23

STATE=/tmp/routeforge-progress.json
routeforge run lab23_bgp_policy_and_filters --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab23` passes when your implementation is complete for this stage.
- `bgp_policy_apply` should print `[PASS]` (export policy filters denied prefixes deterministically).
- `bgp_update_export` should print `[PASS]` (allowed routes are exported with policy-applied attributes).
- Run output includes checkpoints: BGP_POLICY_APPLY, BGP_UPDATE_EXPORT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab23_bgp_policy_and_filters --state-file "$STATE" --trace-out /tmp/lab23_bgp_policy_and_filters.jsonl
routeforge debug replay --trace /tmp/lab23_bgp_policy_and_filters.jsonl
routeforge debug explain --trace /tmp/lab23_bgp_policy_and_filters.jsonl --step bgp_policy_apply
```

Checkpoint guide:

- `BGP_POLICY_APPLY`: Import/export controls with prefix, AS-path, and community policy.
- `BGP_UPDATE_EXPORT`: Import/export controls with prefix, AS-path, and community policy.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/bgp.py` and rerun `routeforge check lab23` to confirm tests catch regressions.
- If `routeforge run lab23_bgp_policy_and_filters --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 4271 (BGP-4).

