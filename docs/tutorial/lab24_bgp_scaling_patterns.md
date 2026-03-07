# Lab 24: BGP Scaling Patterns

## Learning objectives

- Implement `route_reflect` in `src/routeforge/runtime/bgp.py`.
- Deliver `bgp_route_reflection`: route-reflector reflects client routes to non-originating clients.
- Deliver `bgp_convergence_mark`: steady-state reflection output is stable across iterations.
- Deliver `bgp_multipath_select`: equal-cost/equal-policy paths are selected for multipath install.
- Validate internal behavior through checkpoints: BGP_RR_REFLECT, BGP_CONVERGENCE_MARK, BGP_MULTIPATH_SELECT.

## Prerequisite recap

- Required prior labs: lab23_bgp_policy_and_filters.
- Confirm target mapping before coding with `routeforge show lab24_bgp_scaling_patterns`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Route-reflector behavior and deterministic convergence semantics. Student-mode coding target for this stage is `src/routeforge/runtime/bgp.py` (`route_reflect`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/bgp.py`
- Symbols: `route_reflect`
- Why this target: Reflect client routes to non-originating clients.
- Stage check: `routeforge check lab24`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab24_bgp_scaling_patterns`
3. Edit only the listed symbols in `src/routeforge/runtime/bgp.py`.
4. Run `routeforge check lab24` until it exits with status `0`.
5. Run `routeforge run lab24_bgp_scaling_patterns --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab24_bgp_scaling_patterns
routeforge check lab24

STATE=/tmp/routeforge-progress.json
routeforge run lab24_bgp_scaling_patterns --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab24` passes when your implementation is complete for this stage.
- `bgp_route_reflection` should print `[PASS]` (route-reflector reflects client routes to non-originating clients).
- `bgp_convergence_mark` should print `[PASS]` (steady-state reflection output is stable across iterations).
- `bgp_multipath_select` should print `[PASS]` (equal-cost/equal-policy paths are selected for multipath install).
- Run output includes checkpoints: BGP_RR_REFLECT, BGP_CONVERGENCE_MARK, BGP_MULTIPATH_SELECT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab24_bgp_scaling_patterns --state-file "$STATE" --trace-out /tmp/lab24_bgp_scaling_patterns.jsonl
routeforge debug replay --trace /tmp/lab24_bgp_scaling_patterns.jsonl
routeforge debug explain --trace /tmp/lab24_bgp_scaling_patterns.jsonl --step bgp_route_reflection
```

Checkpoint guide:

- `BGP_RR_REFLECT`: Route-reflector behavior and deterministic convergence semantics.
- `BGP_CONVERGENCE_MARK`: Route-reflector behavior and deterministic convergence semantics.
- `BGP_MULTIPATH_SELECT`: Multipath route install where policy and tie-breaks allow.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/bgp.py` and rerun `routeforge check lab24` to confirm tests catch regressions.
- If `routeforge run lab24_bgp_scaling_patterns --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 4271 (BGP-4).

