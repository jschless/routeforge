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

### The problem: iBGP's full-mesh requirement does not scale

Within a single AS, BGP speakers use iBGP to distribute externally learned routes. A fundamental iBGP rule is that a router does not re-advertise a route learned from one iBGP peer to another iBGP peer — this prevents routing loops inside the AS. The consequence is that every iBGP speaker must peer directly with every other iBGP speaker (a full mesh). In a network with N routers, that requires N*(N-1)/2 peering sessions. At 50 routers that is 1,225 sessions; at 100 it is 4,950. The full mesh becomes operationally unmanageable as networks grow.

Route Reflection (RFC 4456) solves this by designating one or more routers as **Route Reflectors (RR)**. Clients peer only with the RR, not with each other. The RR is permitted to re-advertise a route learned from one client to all other clients, breaking the iBGP re-advertisement prohibition in a controlled way.

### Key terms

- **Route Reflector (RR)**: a router that re-advertises iBGP routes received from a client to other clients in the same cluster.
- **RR client**: a router that has a peering session only with the RR, relying on it for full iBGP reachability.
- **Reflection**: the act of copying prefixes learned from one client into the routing tables of other clients via the RR.
- **Convergence**: the state where routing tables have stabilized — no peer has a different view of the network than it had in the previous iteration.

### Topology

```
        AS 65001 — Route Reflector Cluster

    Client A          Client B
   (10.0.1.0/24)    (10.0.2.0/24)
       |                 |
       +----> [ RR ] <---+
              /    \
             /      \
        Client C   Client D
       (10.0.3.0/24) (10.0.4.0/24)

  Client A announces 10.0.1.0/24 to RR
  RR reflects to: B, C, D  (all clients except A)
  Client B, C, D learn 10.0.1.0/24 without peering with A directly
```

### How it works

`route_reflect` takes a `learned` dict mapping each client name to the list of prefixes that client has announced, and a `source_client` identifying which client originated the routes being reflected in this call. It returns a new dict mapping every other client to the source client's prefix list.

The key insight: the RR does not merge or modify the prefix list. It distributes the source client's prefixes verbatim to the other clients. Each call to `route_reflect` handles one source client's routes at a time — if you need to reflect routes from multiple clients, you call the function once per client.

`convergence_mark` compares two routing-table snapshots (`before` and `after`) and returns `True` if they are identical. It models the check an operator or control-plane daemon would run to determine whether a topology event (a link going down, a new peer coming up) has finished propagating. When `before == after`, the network has converged; further reflection passes will not change any routing table.

### Correct behavior

Given `learned = {"A": ["10.0.1.0/24", "10.0.2.0/24"], "B": [...], "C": [...]}` and `source_client = "A"`, the return value maps `"B"` and `"C"` each to `["10.0.1.0/24", "10.0.2.0/24"]`. Client `"A"` does not appear as a key in the output. For `convergence_mark`, passing two equal dicts returns `True`; any differing value for any key returns `False`.

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

- `BGP_RR_REFLECT`: fires when `route_reflect` distributes the source client's prefixes to the other clients. If this checkpoint is absent, the function was not called or returned before populating the output dict. If it fires but the source client appears as a key in the returned dict, the exclusion logic is missing — the source should never receive its own reflected routes. If other clients are missing from the output, verify that you are iterating over all keys in `learned` except `source_client`.
- `BGP_CONVERGENCE_MARK`: fires when `convergence_mark` evaluates whether the before and after routing-table snapshots are identical. If this checkpoint is absent, the convergence check step was skipped entirely. If it fires but returns the wrong boolean, confirm that you are doing a direct equality comparison (`before == after`) rather than checking only a subset of keys or using identity comparison (`is`).

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/bgp.py` and rerun `routeforge check lab24` to confirm tests catch regressions.
- If `routeforge run lab24_bgp_scaling_patterns --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 4271 (BGP-4).
