# Lab 15: OSPF Multi-Area ABR

## Learning objectives

- Implement `originate_summaries` in `src/routeforge/runtime/ospf.py`.
- Deliver `ospf_summary_originate`: ABR originates deterministic summaries from non-backbone areas.
- Deliver `ospf_interarea_install`: summary routes are installed as inter-area reachability.
- Validate internal behavior through checkpoints: OSPF_SUMMARY_ORIGINATE, OSPF_INTERAREA_ROUTE_INSTALL.

## Prerequisite recap

- Required prior labs: lab14_ospf_spf_and_route_install.
- Confirm target mapping before coding with `routeforge show lab15_ospf_multi_area_abr`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### What problem do multiple OSPF areas solve?

A single OSPF area with hundreds of routers means every router runs SPF on a massive LSDB.  OSPF areas divide the network into zones — each area runs its own SPF internally, and *Area Border Routers (ABRs)* summarize each area's routes before advertising them into the backbone (Area 0).  This reduces LSDB size and SPF computation on non-ABR routers.

### Topology

```
           Area 0 (backbone)
    ┌─────────────────────────────┐
    │                             │
   ABR1                          ABR2
    │                             │
    └──── Area 1 ────┐   ┌──── Area 2 ────┘
          10.1.x.x   │   │   10.2.x.x
         routers      │   │   routers
```

ABR1 is connected to both Area 0 and Area 1.  It summarizes all `10.1.x.x/24` routes from Area 1 into a single `10.1.0.0/16` summary advertised into Area 0.

### How summarization works (this lab)

`originate_summaries` takes a flat list of `AreaRoute` objects from all areas and produces one `/16` summary per non-backbone area:

1. Filter out `area_id == 0` (backbone routes don't get summarized).
2. Group remaining routes by `area_id`.
3. For each area group, emit one `AreaRoute`:
   - `prefix`: derive from the routes in the group — first two octets + `.0.0`
     (e.g., routes with `10.1.1.0` and `10.1.2.0` → summary prefix `10.1.0.0`)
   - `prefix_len`: 16
   - `cost`: `max(cost for route in group)` (worst-case advertisement)
4. Return all summaries sorted by `(area_id, prefix)`.

### Worked example

Input routes:
```
AreaRoute(area_id=1, prefix="10.1.1.0", prefix_len=24, cost=10)
AreaRoute(area_id=1, prefix="10.1.2.0", prefix_len=24, cost=15)
AreaRoute(area_id=0, prefix="10.0.0.0", prefix_len=8,  cost=1)   ← skip (backbone)
```

Output summaries:
```
AreaRoute(area_id=1, prefix="10.1.0.0", prefix_len=16, cost=15)
```

Student-mode coding target for this stage is `src/routeforge/runtime/ospf.py` (`originate_summaries`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/ospf.py`
- Symbols: `originate_summaries`
- Why this target: Produce inter-area summary routes.
- Stage check: `routeforge check lab15`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab15_ospf_multi_area_abr`
3. Edit only the listed symbols in `src/routeforge/runtime/ospf.py`.
4. Run `routeforge check lab15` until it exits with status `0`.
5. Run `routeforge run lab15_ospf_multi_area_abr --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab15_ospf_multi_area_abr
routeforge check lab15

STATE=/tmp/routeforge-progress.json
routeforge run lab15_ospf_multi_area_abr --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab15` passes when your implementation is complete for this stage.
- `ospf_summary_originate` should print `[PASS]` (ABR originates deterministic summaries from non-backbone areas).
- `ospf_interarea_install` should print `[PASS]` (summary routes are installed as inter-area reachability).
- Run output includes checkpoints: OSPF_SUMMARY_ORIGINATE, OSPF_INTERAREA_ROUTE_INSTALL.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab15_ospf_multi_area_abr --state-file "$STATE" --trace-out /tmp/lab15_ospf_multi_area_abr.jsonl
routeforge debug replay --trace /tmp/lab15_ospf_multi_area_abr.jsonl
routeforge debug explain --trace /tmp/lab15_ospf_multi_area_abr.jsonl --step ospf_summary_originate
```

Checkpoint guide:

- `OSPF_SUMMARY_ORIGINATE`: `originate_summaries` ran and produced at least one summary
  route.  If missing, the function either raised an exception or returned an empty list
  when summaries were expected.  Check that you're not accidentally filtering out non-zero
  area routes — the filter should exclude `area_id == 0`, not include it.
- `OSPF_INTERAREA_ROUTE_INSTALL`: A summary route was installed into the RIB as an
  inter-area route.  If missing but `OSPF_SUMMARY_ORIGINATE` fired, the route installation
  step after summary generation was not reached.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/ospf.py` and rerun `routeforge check lab15` to confirm tests catch regressions.
- If `routeforge run lab15_ospf_multi_area_abr --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 2328 (OSPFv2).

