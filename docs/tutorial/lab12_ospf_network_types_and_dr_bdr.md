# Lab 12: OSPF Network Types and DR/BDR

## Learning objectives

- Implement `_election_order, failover_dr_bdr` in `src/routeforge/runtime/ospf.py`.
- Deliver `ospf_dr_bdr_election`: DR/BDR selection follows deterministic priority and router-id ordering.
- Deliver `ospf_dr_failover`: BDR is promoted to DR when original DR fails.
- Validate internal behavior through checkpoints: OSPF_DR_ELECT, OSPF_BDR_ELECT, OSPF_DR_FAILOVER.

## Prerequisite recap

- Required prior labs: lab11_ospf_adjacency_fsm.
- Confirm target mapping before coding with `routeforge show lab12_ospf_network_types_and_dr_bdr`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

### The problem: flooding storms on shared segments

OSPF exchanges Link State Advertisements (LSAs) to build a consistent map of the network. When multiple routers share the same Ethernet segment — a broadcast multi-access network — a naive implementation would have every router flood every LSA to every neighbor. With N routers on a segment, that produces O(N^2) adjacencies and O(N^2) redundant copies of every LSA. On a segment with even a dozen routers, this overhead becomes unmanageable and defeats the scalability goals of a link-state protocol.

OSPF solves this with a Designated Router (DR) and Backup Designated Router (BDR). Instead of a full-mesh of FULL-state adjacencies, every router on the segment forms a FULL adjacency only with the DR and BDR. The DR acts as the central redistribution point: it receives LSAs from DROthers, acknowledges them, and re-floods them to the rest of the segment. The BDR silently monitors all traffic and is prepared to assume the DR role the instant the DR becomes unreachable.

### Key terms

- **DR (Designated Router)**: The single router on a broadcast segment responsible for LSA redistribution. All other routers (DROthers) send LSAs to the AllDRouters multicast address (`224.0.0.6`) and receive re-flooded LSAs from the DR via AllSPFRouters (`224.0.0.5`).
- **BDR (Backup Designated Router)**: The standby router that listens to all LSA traffic on the segment and is ready to promote itself to DR without delay if the DR fails.
- **DROther**: Any router on the segment that is neither DR nor BDR. DROthers maintain FULL adjacency only with the DR and BDR; their adjacency with other DROthers stops at the 2-WAY state.
- **Priority**: A per-interface integer in the range 0–255 that influences election outcome. A priority of 0 means the router is permanently ineligible to become DR or BDR and will never win an election.
- **Router ID**: A 32-bit identifier written as a dotted-quad string (e.g. `10.0.0.4`) that acts as a tiebreaker when two candidates have equal priority.

### Topology: broadcast segment with DR/BDR

```
           192.168.1.0/24  (broadcast multi-access segment)
  ┌──────────────────────────────────────────────────┐
  │                                                  │
  R1            R2            R3            R4        │
  prio=1        prio=5        prio=5        prio=1    │
  id=10.0.0.1   id=10.0.0.2   id=10.0.0.3   id=10.0.0.4
                                  DR            BDR?
```

After applying the election algorithm (highest priority first, then highest router ID):

- R2 and R3 both have priority 5, so router ID breaks the tie.
- `10.0.0.3` > `10.0.0.2` lexicographically, so R3 wins DR.
- R2 is next in the ordered list, so R2 becomes BDR.
- R1 and R4 are DROthers. They maintain FULL adjacency only with R3 (DR) and R2 (BDR), reducing adjacency count from 6 (full mesh) to 4.

LSA originated by R1 travels to the DR multicast address. R3 acknowledges it, then re-floods it to the segment so R2 and R4 receive it. R2 (BDR) tracks this flood passively.

### Election algorithm

Election is deterministic and based on two criteria applied in order:

1. **Highest priority wins.** Candidates are sorted descending by priority. Any candidate with priority 0 is excluded entirely and cannot be elected DR or BDR under any circumstances.
2. **Highest router ID breaks ties.** Among candidates with equal priority, the router with the lexicographically greatest router ID string wins. Router IDs are dotted-quad strings — compare them as strings, not as IP addresses, or sort order may be incorrect for IDs like `10.0.0.9` vs `10.0.0.10`.

After sorting, the first candidate becomes DR and the second becomes BDR (if one exists). There is no randomness in this process: given the same input, the output must always be identical.

### Failover behavior

When the current DR disappears from the segment (link failure, process restart, or keepalive timeout), the BDR assumes the DR role immediately without rerunning the full election from scratch. This is intentional: the BDR already holds a complete, synchronized LSDB copy acquired during its normal FULL adjacency with the former DR, so it can begin serving as DR the moment it detects the DR is gone.

A new BDR is then elected from the remaining active candidates to fill the now-vacant BDR slot. This two-step promotion design keeps convergence time short and avoids the brief interval where the segment has no DR.

Your `failover_dr_bdr` function must accept the full candidate list along with an `active_router_ids` set and filter the candidates before running the election. Candidates whose router IDs are absent from `active_router_ids` are treated as if they do not exist — they should never appear in the returned DR or BDR roles.

### What correct behavior looks like

- `_election_order` returns candidates sorted descending by priority; within the same priority, candidates are sorted descending by router ID string.
- The first entry in the sorted list is always the DR winner; the second (if present) is the BDR winner.
- `failover_dr_bdr` returns a `(dr_router_id, bdr_router_id)` tuple. After a DR failure, the returned DR router ID should match what was previously the BDR.
- If only one active candidate remains after filtering, `failover_dr_bdr` returns `(dr_router_id, None)`.

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/ospf.py`
- Symbols: `_election_order, failover_dr_bdr`
- Why this target: Implement deterministic candidate ordering and active-set failover election.
- Stage check: `routeforge check lab12`

Function contract for this stage:

- Symbol: `_election_order(candidates: list[DrCandidate]) -> list[DrCandidate]`
- Required behavior: sort by highest priority first, then highest router-id
- Symbol: `failover_dr_bdr(candidates: list[DrCandidate], *, active_router_ids: set[str]) -> tuple[str, str | None]`
- Required behavior: filter to active routers, then elect DR/BDR using deterministic order

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab12_ospf_network_types_and_dr_bdr`
3. Edit only the listed symbols in `src/routeforge/runtime/ospf.py`.
4. Run `routeforge check lab12` until it exits with status `0`.
5. Run `routeforge run lab12_ospf_network_types_and_dr_bdr --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab12_ospf_network_types_and_dr_bdr
routeforge check lab12

STATE=/tmp/routeforge-progress.json
routeforge run lab12_ospf_network_types_and_dr_bdr --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab12` passes when your implementation is complete for this stage.
- `ospf_dr_bdr_election` should print `[PASS]` (DR/BDR selection follows deterministic priority and router-id ordering).
- `ospf_dr_failover` should print `[PASS]` (BDR is promoted to DR when original DR fails).
- Run output includes checkpoints: OSPF_DR_ELECT, OSPF_BDR_ELECT, OSPF_DR_FAILOVER.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab12_ospf_network_types_and_dr_bdr --state-file "$STATE" --trace-out /tmp/lab12_ospf_network_types_and_dr_bdr.jsonl
routeforge debug replay --trace /tmp/lab12_ospf_network_types_and_dr_bdr.jsonl
routeforge debug explain --trace /tmp/lab12_ospf_network_types_and_dr_bdr.jsonl --step ospf_dr_bdr_election
```

Checkpoint guide:

- `OSPF_DR_ELECT`: Fires when a router has been selected as Designated Router for the segment. The trace details include the elected DR's router ID and priority. If this checkpoint is missing, `_election_order` is not returning candidates in the correct order, or the election logic upstream is not invoking `_election_order` at all. Verify that your sort key places highest priority first and uses router ID as a secondary descending key — if you sort ascending on either dimension, the wrong candidate wins.
- `OSPF_BDR_ELECT`: Fires when a Backup Designated Router has been identified, meaning at least two eligible candidates (both with priority > 0) were present on the segment. The trace details include the BDR's router ID. If this checkpoint is missing but `OSPF_DR_ELECT` fired, verify that your implementation extracts the second entry from the ordered candidate list as BDR rather than stopping at the first. If there is genuinely only one eligible candidate on the segment, this checkpoint legitimately does not fire and the BDR value should be `None`.
- `OSPF_DR_FAILOVER`: Fires during the failover scenario when the active candidate set has changed — the original DR's router ID is absent from `active_router_ids` — and a new DR has been elected from the remaining candidates. If this checkpoint is missing, check that `failover_dr_bdr` is filtering candidates before calling the election logic. Passing an unfiltered list (including the failed router) will yield a stale result where the dead router is still elected DR, and the scenario will not register the failover as having occurred.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/ospf.py` and rerun `routeforge check lab12` to confirm tests catch regressions.
- If `routeforge run lab12_ospf_network_types_and_dr_bdr --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 2328 (OSPFv2).
