# Lab 22: BGP Attributes and Best Path

## Learning objectives

- Implement `select_best_path` in `src/routeforge/runtime/bgp.py`.
- Deliver `bgp_update_receive`: BGP update set is ingested for best-path selection.
- Deliver `bgp_best_path_select`: deterministic best-path logic selects expected candidate.
- Validate internal behavior through checkpoints: BGP_UPDATE_RX, BGP_BEST_PATH.

## Prerequisite recap

- Required prior labs: lab21_bgp_session_fsm_and_transport.
- Confirm target mapping before coding with `routeforge show lab22_bgp_attributes_and_bestpath`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### What problem does BGP best-path solve?

A BGP router often receives multiple paths to the same prefix from different peers.  The *best-path selection algorithm* picks exactly one path to install in the RIB and use for forwarding.  The algorithm must be *deterministic* — given the same inputs, always produce the same winner — so the network converges to a stable state.

### Topology

```
AS 65001          AS 65002
  R1 ─────────────  R2
  |    eBGP peer    |
  |                 |
  R3               R4
    \             /
     AS 65003 (R5, the prefix originator)
```

R1 receives two paths to `10.0.0.0/8` — one via R2 (local_pref=100, AS path 65002 65003) and one via R3 (local_pref=200, shorter AS path).  Best-path selection chooses the winner.

### Decision chain (this lab's scope)

Apply these criteria in order — the first one that distinguishes the candidates wins:

| Priority | Criterion | Higher/Lower wins |
|---|---|---|
| 1 | `local_pref` | Higher wins |
| 2 | `len(as_path)` | Shorter (lower) wins |
| 3 | `origin` (igp/egp/incomplete) | Lower rank wins (igp=0, egp=1, incomplete=2) |
| 4 | `med` | Lower wins |
| 5 | `next_hop` (string) | Lexicographically lower wins |

### Worked example

Three paths to `10.0.0.0/8`:
```
Path A: local_pref=100, as_path=(65002, 65003), origin=igp, med=0, next_hop="10.1.1.2"
Path B: local_pref=200, as_path=(65003,),       origin=igp, med=0, next_hop="10.1.1.3"
Path C: local_pref=200, as_path=(65003, 65004), origin=igp, med=0, next_hop="10.1.1.1"
```

Step 1: local_pref — B and C (200) beat A (100).  A is eliminated.
Step 2: as_path length — B (len=1) beats C (len=2).  **Winner: B.**

Student-mode coding target for this stage is `src/routeforge/runtime/bgp.py` (`select_best_path`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/bgp.py`
- Symbols: `select_best_path`
- Why this target: Select deterministic BGP best path from candidates.
- Stage check: `routeforge check lab22`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab22_bgp_attributes_and_bestpath`
3. Edit only the listed symbols in `src/routeforge/runtime/bgp.py`.
4. Run `routeforge check lab22` until it exits with status `0`.
5. Run `routeforge run lab22_bgp_attributes_and_bestpath --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab22_bgp_attributes_and_bestpath
routeforge check lab22

STATE=/tmp/routeforge-progress.json
routeforge run lab22_bgp_attributes_and_bestpath --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab22` passes when your implementation is complete for this stage.
- `bgp_update_receive` should print `[PASS]` (BGP update set is ingested for best-path selection).
- `bgp_best_path_select` should print `[PASS]` (deterministic best-path logic selects expected candidate).
- Run output includes checkpoints: BGP_UPDATE_RX, BGP_BEST_PATH.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab22_bgp_attributes_and_bestpath --state-file "$STATE" --trace-out /tmp/lab22_bgp_attributes_and_bestpath.jsonl
routeforge debug replay --trace /tmp/lab22_bgp_attributes_and_bestpath.jsonl
routeforge debug explain --trace /tmp/lab22_bgp_attributes_and_bestpath.jsonl --step bgp_update_receive
```

Checkpoint guide:

- `BGP_UPDATE_RX`: A batch of BGP path updates was received and queued for best-path
  evaluation.  If missing, the update ingestion step before `select_best_path` was not reached.
- `BGP_BEST_PATH`: `select_best_path` ran and produced a winner.  If missing, the function
  raised an exception.  If the wrong path is selected, check your tiebreak order — a common
  mistake is applying MED before AS path length, or using `>` instead of `<` for MED.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/bgp.py` and rerun `routeforge check lab22` to confirm tests catch regressions.
- If `routeforge run lab22_bgp_attributes_and_bestpath --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 4271 (BGP-4).

