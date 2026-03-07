# Lab 35: OSPFv3 Adjacency and LSDB

## Learning objectives

- Implement `ospfv3_neighbor_result, ospfv3_adjacency_lsdb` in `src/routeforge/runtime/phase2.py`.
- Deliver `ospfv3_hello_rx`: valid hello advances adjacency.
- Deliver `ospfv3_neighbor_full`: adjacency reaches FULL state.
- Deliver `ospfv3_lsa_install`: IPv6 LSA is installed in LSDB.
- Validate internal behavior through checkpoints: OSPFV3_HELLO_RX, OSPFV3_NEIGHBOR_FULL, OSPFV3_LSA_INSTALL.

## Prerequisite recap

- Required prior labs: `lab34_ipv6_nd_slaac_and_ra_guard`.
- Confirm target mapping before coding with `routeforge show lab35_ospfv3_adjacency_and_lsdb`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

OSPFv3 neighbor formation and IPv6 LSDB state transitions. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`ospfv3_neighbor_result, ospfv3_adjacency_lsdb`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbols: `ospfv3_neighbor_result, ospfv3_adjacency_lsdb`
- Why this target: derive neighbor state transition and LSDB install output from one deterministic pipeline.
- Stage check: `routeforge check lab35`

Function contract for this stage:

- Symbol: `ospfv3_neighbor_result(*, hello_ok: bool) -> Literal["DOWN", "FULL"]`
- Required behavior: map hello acceptance into deterministic adjacency state
- Symbol: `ospfv3_adjacency_lsdb(*, hello_ok: bool, lsa_id: str, lsdb: set[str]) -> tuple[Literal["DOWN", "FULL"], set[str]]`
- Required behavior: return state + LSDB snapshot, adding LSA only when state is FULL

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab35_ospfv3_adjacency_and_lsdb`
3. Edit only `ospfv3_neighbor_result, ospfv3_adjacency_lsdb` in `src/routeforge/runtime/phase2.py`.
4. Run `routeforge check lab35` until it exits with status `0`.
5. Run `routeforge run lab35_ospfv3_adjacency_and_lsdb --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab35_ospfv3_adjacency_and_lsdb
routeforge check lab35

STATE=/tmp/routeforge-progress.json
routeforge run lab35_ospfv3_adjacency_and_lsdb --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab35` passes when your implementation is complete for this stage.
- `ospfv3_hello_rx` should print `[PASS]` (valid hello advances adjacency).
- `ospfv3_neighbor_full` should print `[PASS]` (adjacency reaches FULL state).
- `ospfv3_lsa_install` should print `[PASS]` (IPv6 LSA is installed in LSDB).
- Run output includes checkpoints: OSPFV3_HELLO_RX, OSPFV3_NEIGHBOR_FULL, OSPFV3_LSA_INSTALL.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab35_ospfv3_adjacency_and_lsdb --state-file "$STATE" --trace-out /tmp/lab35_ospfv3_adjacency_and_lsdb.jsonl
routeforge debug replay --trace /tmp/lab35_ospfv3_adjacency_and_lsdb.jsonl
routeforge debug explain --trace /tmp/lab35_ospfv3_adjacency_and_lsdb.jsonl --step ospfv3_hello_rx
```

Checkpoint guide:

- `OSPFV3_HELLO_RX`: first expected pipeline milestone.
- `OSPFV3_NEIGHBOR_FULL`: second expected pipeline milestone.
- `OSPFV3_LSA_INSTALL`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `ospfv3_neighbor_result` or `ospfv3_adjacency_lsdb` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab35` to confirm tests catch regressions.
- If `routeforge run lab35_ospfv3_adjacency_and_lsdb --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- OSPFv3 adjacency and LSDB fundamentals.
