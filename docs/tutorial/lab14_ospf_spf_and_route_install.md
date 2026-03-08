# Lab 14: OSPF SPF and Route Install

## Learning objectives

- Implement `run_spf` in `src/routeforge/runtime/ospf.py`.
- Deliver `ospf_spf_run`: SPF produces deterministic cost and next-hop selection.
- Deliver `ospf_route_install`: SPF outcome installs route into RIB.
- Validate internal behavior through checkpoints: OSPF_SPF_RUN, RIB_ROUTE_INSTALL.

## Prerequisite recap

- Required prior labs: lab13_ospf_lsa_flooding_and_lsdb.
- Confirm target mapping before coding with `routeforge show lab14_ospf_spf_and_route_install`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### What problem does SPF solve?

OSPF routers flood Link State Advertisements (LSAs) describing their links and costs until every router has a complete map of the network (the LSDB).  But a map alone doesn't tell you the *best path* — that requires running Dijkstra's Shortest Path First algorithm to compute the minimum-cost tree from your router to every other router.

### Topology

```
     R1 (root)
    /    \
  cost=1  cost=4
  /          \
R2            R3
  \          /
  cost=2  cost=1
    \      /
      R4
```

Graph (adjacency list):
```
R1: [(R2, 1), (R3, 4)]
R2: [(R1, 1), (R4, 2)]
R3: [(R1, 4), (R4, 1)]
R4: [(R2, 2), (R3, 1)]
```

Running SPF from R1:
- R1=0 (root)
- R2=1 (via R1, cost 1)
- R3=4 (via R1, cost 4)
- R4=3 (via R1→R2→R4, cost 1+2=3)  ← cheaper than R1→R3→R4 (4+1=5)

### Dijkstra's algorithm (pseudocode)

```
cost = {root: 0}
parent = {root: None}
heap = [(0, root)]

while heap not empty:
    (c, node) = pop_min(heap)
    if c > cost[node]:
        continue  # stale entry
    for (neighbor, link_cost) in graph[node]:
        new_cost = c + link_cost
        if new_cost < cost.get(neighbor, inf):
            cost[neighbor] = new_cost
            parent[neighbor] = node
            push (new_cost, neighbor) to heap
        elif new_cost == cost[neighbor] and neighbor < parent[neighbor]:
            parent[neighbor] = node  # deterministic tiebreak: lower router_id
```

### What `parent_by_router` means

`parent_by_router[R4] = "R2"` means the best path to R4 goes through R2 as the immediate predecessor.  `next_hop_for_destination()` (already implemented for you) walks this chain back to find the first hop from root.

Student-mode coding target for this stage is `src/routeforge/runtime/ospf.py` (`run_spf`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/ospf.py`
- Symbols: `run_spf`
- Why this target: Compute deterministic SPF costs and parents.
- Stage check: `routeforge check lab14`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab14_ospf_spf_and_route_install`
3. Edit only the listed symbols in `src/routeforge/runtime/ospf.py`.
4. Run `routeforge check lab14` until it exits with status `0`.
5. Run `routeforge run lab14_ospf_spf_and_route_install --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab14_ospf_spf_and_route_install
routeforge check lab14

STATE=/tmp/routeforge-progress.json
routeforge run lab14_ospf_spf_and_route_install --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab14` passes when your implementation is complete for this stage.
- `ospf_spf_run` should print `[PASS]` (SPF produces deterministic cost and next-hop selection).
- `ospf_route_install` should print `[PASS]` (SPF outcome installs route into RIB).
- Run output includes checkpoints: OSPF_SPF_RUN, RIB_ROUTE_INSTALL.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab14_ospf_spf_and_route_install --state-file "$STATE" --trace-out /tmp/lab14_ospf_spf_and_route_install.jsonl
routeforge debug replay --trace /tmp/lab14_ospf_spf_and_route_install.jsonl
routeforge debug explain --trace /tmp/lab14_ospf_spf_and_route_install.jsonl --step ospf_spf_run
```

Checkpoint guide:

- `OSPF_SPF_RUN`: Dijkstra completed — `SpfResult` has been produced with cost and parent
  maps for all reachable routers.  If missing, `run_spf` raised an exception or returned
  before building the result.
- `RIB_ROUTE_INSTALL`: An SPF-computed route was installed into the RIB.  If missing, either
  `run_spf` failed or the route installation step was not reached after SPF.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/ospf.py` and rerun `routeforge check lab14` to confirm tests catch regressions.
- If `routeforge run lab14_ospf_spf_and_route_install --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 2328 (OSPFv2).

## Concept Deepening Notes

SPF correctness depends on deterministic graph traversal and strict tie behavior. Cost/parent maps should be reproducible, then translated into route-install actions that preserve the computed path intent. If install logic diverges from SPF state, downstream forwarding appears correct for some prefixes but unstable for equivalent paths.

## Checkpoint Guide (Expanded)

- `OSPF_SPF_RUN`: Confirm this marker appears when your implementation follows the intended decision path.
- `RIB_ROUTE_INSTALL`: Confirm this marker appears when your implementation follows the intended decision path.
