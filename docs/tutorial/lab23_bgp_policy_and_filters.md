# Lab 23: BGP Policy and Filters

## Learning objectives

- Apply deterministic outbound route filtering.
- Validate policy-driven attribute rewrite behavior.
- Confirm only permitted prefixes are exported.

## Prerequisite recap

- Complete `lab22_bgp_attributes_and_bestpath`.
- Understand ordered rule evaluation from `lab18_acl_pipeline`.

## Concept walkthrough

`lab23` applies export policy controls to BGP updates. Denied prefixes are removed, and remaining paths are rewritten with predictable attributes.

## Implementation TODO map

- `src/routeforge/runtime/bgp.py`: export policy helper.
- `src/routeforge/labs/exercises.py`: policy + export scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab23_bgp_policy_and_filters --completed <all-labs-lab01-through-lab22>
```

Expected:

- `bgp_policy_apply` step `PASS`.
- `bgp_update_export` step `PASS`.
- Checkpoints include `BGP_POLICY_APPLY` and `BGP_UPDATE_EXPORT`.

## Debug trace checkpoints and interpretation guidance

- `BGP_POLICY_APPLY`: route filtering/rewrites evaluated.
- `BGP_UPDATE_EXPORT`: final outbound advertisements were generated.

## Failure drills and troubleshooting flow

- Deny all prefixes and confirm exported set is empty.
- Remove deny rule and verify previously blocked route appears in export set.

## Standards and references

- RFC 4271 policy framework concepts for UPDATE propagation.
