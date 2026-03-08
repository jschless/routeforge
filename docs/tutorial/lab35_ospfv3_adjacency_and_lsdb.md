# Lab 35: OSPFv3 Adjacency and LSDB

## Learning objectives

- Implement `ospfv3_neighbor_result, ospfv3_adjacency_lsdb` in `src/routeforge/runtime/ipv6.py`.
- Deliver `ospfv3_hello_rx`: valid hello advances adjacency.
- Deliver `ospfv3_neighbor_full`: adjacency reaches FULL state.
- Deliver `ospfv3_lsa_install`: IPv6 LSA is installed in LSDB.
- Validate internal behavior through checkpoints: OSPFV3_HELLO_RX, OSPFV3_NEIGHBOR_FULL, OSPFV3_LSA_INSTALL.

## Prerequisite recap

- Required prior labs: `lab34_ipv6_nd_slaac_and_ra_guard`.
- Confirm target mapping before coding with `routeforge show lab35_ospfv3_adjacency_and_lsdb`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

OSPFv3 is the IPv6 adaptation of the OSPF link-state routing protocol. Like OSPFv2, it discovers neighbors by exchanging Hello packets, synchronizes a Link-State Database (LSDB) through database exchange, and then runs SPF to compute shortest paths. The key difference is that OSPFv3 runs over IPv6 link-local addresses and carries IPv6 topology information in its LSAs.

The adjacency lifecycle has several states, but for this lab only two outcomes matter:

- `FULL`: the neighbor relationship is established and LSAs can be exchanged.
- `DOWN`: the hello handshake failed or was never completed; no LSAs are exchanged.

Hello validation is the gatekeeper. Two routers become neighbors only if their Hello packets agree on area ID, hello interval, dead interval, and certain option flags. If any parameter mismatches, the adjacency stays in `DOWN` and no topology information is shared.

```
  RouterA                        RouterB
  -------                        -------
  hello (area 0, interval 10) -->
                              <-- hello (area 0, interval 10)
  state: FULL                    state: FULL
  LSDB: {lsa-B}                  LSDB: {lsa-A}

  -- vs --

  hello (area 0, interval 10) -->
                              <-- hello (area 1, interval 30)  [mismatch]
  state: DOWN                    state: DOWN
  LSDB: unchanged                LSDB: unchanged
```

Once adjacency reaches `FULL`, the routers flood their LSAs to each other. Each LSA has a unique identifier. The LSDB is simply the set of all LSA IDs that this router has received and stored. When a new LSA arrives it is added to the set; duplicate LSA IDs are ignored (the set deduplicates automatically).

In this lab `ospfv3_adjacency_lsdb` models this in one function call:

- If `hello_ok` is `False`: the adjacency is `DOWN`. Return the existing LSDB unchanged.
- If `hello_ok` is `True`: the adjacency is `FULL`. Return the LSDB with `lsa_id` added.

The helper `ospfv3_neighbor_result` converts the boolean directly to `"FULL"` or `"DOWN"` for use in places where only the adjacency state (not the LSDB) is needed.

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/ipv6.py`
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
3. Edit only `ospfv3_neighbor_result, ospfv3_adjacency_lsdb` in `src/routeforge/runtime/ipv6.py`.
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

- `OSPFV3_HELLO_RX`: fires when the scenario receives the OSPFv3 hello and evaluates whether adjacency can proceed. If this checkpoint is missing, the hello-processing branch is not being executed.
- `OSPFV3_NEIGHBOR_FULL`: fires when the hello handshake succeeds and the adjacency reaches `FULL` state. The function received `hello_ok=True` and returned `"FULL"` as the first tuple element. If this checkpoint is missing, check that your `hello_ok=True` branch returns `"FULL"` and not `"DOWN"`.
- `OSPFV3_LSA_INSTALL`: fires when a new LSA identifier is added to the LSDB as a result of a successful adjacency. This checkpoint fires only alongside `OSPFV3_NEIGHBOR_FULL`. If `OSPFV3_NEIGHBOR_FULL` fires but `OSPFV3_LSA_INSTALL` does not, confirm that you are returning `lsdb | {lsa_id}` (or an equivalent copy with the new element) rather than returning the original set unmodified.

## Failure drills and troubleshooting flow

- Intentionally break `ospfv3_neighbor_result` or `ospfv3_adjacency_lsdb` in `src/routeforge/runtime/ipv6.py` and rerun `routeforge check lab35` to confirm tests catch regressions.
- If `routeforge run lab35_ospfv3_adjacency_and_lsdb --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- OSPFv3 adjacency and LSDB fundamentals.
