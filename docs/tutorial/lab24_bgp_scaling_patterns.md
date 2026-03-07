# Lab 24: BGP Scaling Patterns

## Learning objectives

- Model route-reflector dissemination behavior.
- Validate deterministic convergence markers.
- Inspect multipath-eligible route selection outcomes.

## Prerequisite recap

- Complete `lab23_bgp_policy_and_filters`.
- Recall steady-state verification from `lab10_ipv4_control_plane_diagnostics`.

## Concept walkthrough

`lab24` focuses on scaling behaviors: route reflection for client fanout and convergence checks that verify stable outputs across repeated runs.

## Implementation TODO map

- `src/routeforge/runtime/bgp.py`: reflection + convergence helpers.
- `src/routeforge/labs/exercises.py`: RR fanout and stability scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab24_bgp_scaling_patterns --completed <all-labs-lab01-through-lab23>
```

Expected:

- `bgp_route_reflection` step `PASS`.
- `bgp_convergence_mark` step `PASS`.
- Checkpoints include `BGP_RR_REFLECT` and `BGP_CONVERGENCE_MARK`.

## Debug trace checkpoints and interpretation guidance

- `BGP_RR_REFLECT`: reflected route fanout to non-origin clients.
- `BGP_CONVERGENCE_MARK`: stable post-convergence state assertion.
- `BGP_MULTIPATH_SELECT`: optional multipath install marker.

## Failure drills and troubleshooting flow

- Remove one client from RR outputs and confirm convergence checks fail.
- Introduce unequal attributes and confirm multipath selection is no longer valid.

## Standards and references

- RFC 4456 route-reflector behavior fundamentals.
