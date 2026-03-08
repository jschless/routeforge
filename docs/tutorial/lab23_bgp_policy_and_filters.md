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

### The problem: not everything in your RIB should leave your network

BGP speakers learn routes from many sources — iBGP peers, eBGP neighbors, redistributed IGP prefixes — and by default would advertise all of them to every neighbor. That is almost never what an operator wants. A transit provider must suppress customer prefixes from leaking to other customers. An enterprise must prevent internal infrastructure prefixes from being announced to the internet. Without outbound filtering, a single misconfiguration can cause a route leak that misdirects global traffic.

Export policy is the mechanism that controls what a BGP speaker announces and how it presents the routes it does announce. It sits between the local RIB (all known best paths) and the UPDATE messages sent to a neighbor.

### Key terms

- **Export policy**: a set of rules evaluated against each candidate route before it is sent to a neighbor. Rules can permit, deny, or modify routes.
- **Denied prefix**: a prefix (e.g., `10.0.0.0/8`) explicitly blocked by policy; matching routes are dropped and never sent.
- **local_pref**: a BGP path attribute used within an AS to express preference. Higher values are preferred. Export policy can override local_pref to influence how receiving peers rank the route.
- **Outbound filter**: another name for export policy — it is applied on the way out, not on receipt.

### Topology

```
    AS 65001                    AS 65002
  +-----------+               +-----------+
  |  Router A | -- eBGP ---> |  Router B |
  |           |               |           |
  |  RIB:     |  apply_export_policy      |
  | 10.1.0/24 |  filters denied_prefixes  |
  | 10.2.0/24 |  rewrites local_pref      |
  | 192.0.2/24|               |           |
  +-----------+               +-----------+
        |
  denied_prefixes = {"192.0.2.0/24"}
  local_pref_override = 200
        |
  Exported to B: 10.1.0/24 (lp=200), 10.2.0/24 (lp=200)
  Suppressed:    192.0.2.0/24
```

### How it works

`apply_export_policy` processes a list of `BgpPath` objects in order and applies two transformations:

1. **Prefix filter**: any path whose `prefix` field appears in `denied_prefixes` is removed from the output entirely. The check is an exact match on the prefix string — a path for `10.1.0.0/24` is not suppressed by a denied entry of `10.1.0.0/8`.

2. **Attribute rewrite**: if `local_pref_override` is not `None`, every path that survived the filter has its `local_pref` replaced with the override value. All other fields (`next_hop`, `as_path`, `med`, `origin`, etc.) are left unchanged.

The function returns the surviving paths in the same relative order they appeared in the input list. Order preservation matters because tie-breaking in best-path selection is sensitive to the position of equal-attribute routes.

### Correct behavior

Given paths for `10.1.0.0/24`, `10.2.0.0/24`, and `192.0.2.0/24` with `denied_prefixes={"192.0.2.0/24"}` and `local_pref_override=200`, correct output contains exactly the first two paths with `local_pref` set to `200`. The `192.0.2.0/24` path is absent. If `local_pref_override` is `None`, `local_pref` values are passed through unchanged.

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

- `BGP_POLICY_APPLY`: fires when `apply_export_policy` evaluates the `denied_prefixes` set against the candidate path list. If this checkpoint is missing from the trace, the function returned early or was never called. If it fires but the wrong paths are present in subsequent output, the prefix-matching logic has a bug — check that you are comparing the path's `prefix` field exactly against the set members, not doing a subnet containment check.
- `BGP_UPDATE_EXPORT`: fires after the prefix filter has been applied and any `local_pref_override` has been written onto surviving paths, marking them as ready for export. If this checkpoint appears but exported paths still carry the original `local_pref`, the attribute rewrite step was skipped or applied to a copy rather than the returned objects. If this checkpoint is absent despite `BGP_POLICY_APPLY` firing, the function may be returning before completing the attribute rewrite phase.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/bgp.py` and rerun `routeforge check lab23` to confirm tests catch regressions.
- If `routeforge run lab23_bgp_policy_and_filters --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 4271 (BGP-4).

