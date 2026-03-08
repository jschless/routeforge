# Lab 36: MP-BGP IPv6 Unicast

## Learning objectives

- Implement `rank_mpbgp_path, mpbgp_ipv6_unicast` in `src/routeforge/runtime/ipv6.py`.
- Deliver `mpbgp_update_rx`: MP-BGP IPv6 updates are ingested.
- Deliver `mpbgp_afi_select`: IPv6 unicast AFI/SAFI context is selected.
- Deliver `mpbgp_bestpath`: best path chosen by deterministic policy.
- Validate internal behavior through checkpoints: BGP_MP_UPDATE_RX, BGP_AF_SELECT, BGP_MP_BESTPATH.

## Prerequisite recap

- Required prior labs: `lab35_ospfv3_adjacency_and_lsdb`.
- Confirm target mapping before coding with `routeforge show lab36_mpbgp_ipv6_unicast`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Standard BGP was designed for IPv4 and carries IPv4 reachability information in its UPDATE messages. Multiprotocol BGP (MP-BGP) extends BGP to carry routing information for additional address families, including IPv6, MPLS VPNs, and VXLANs. It does this through two new optional attributes — MP_REACH_NLRI and MP_UNREACH_NLRI — that carry next-hop and prefix information for whichever address family is in use.

For IPv6 unicast, an MP-BGP speaker advertises each prefix alongside an IPv6 next-hop address. When a router receives multiple paths to the same IPv6 prefix from different peers, it must run best-path selection to choose the single route it will install in the forwarding table.

The BGP decision process is applied in a fixed priority order. The most commonly relevant tiebreakers are:

1. Highest LOCAL_PREF — a locally assigned preference that overrides learned paths. Higher is better.
2. Shortest AS path — fewer autonomous system hops to the destination. Shorter is better.
3. Lowest next-hop (lexicographic) — a deterministic tiebreaker when everything else is equal.

```
  Peer A:  prefix 2001:db8::/32, local_pref=200, as_path_len=2, next_hop=2001:db8::1
  Peer B:  prefix 2001:db8::/32, local_pref=100, as_path_len=1, next_hop=2001:db8::2
  Peer C:  prefix 2001:db8::/32, local_pref=200, as_path_len=3, next_hop=2001:db8::3

  Step 1 — highest LOCAL_PREF: Peer A and Peer C both have 200; Peer B eliminated.
  Step 2 — shortest AS path:   Peer A has len=2, Peer C has len=3; Peer C eliminated.
  Winner: Peer A
```

In this lab `rank_mpbgp_path` produces a sort key tuple from a single `MpbgpPath` object. Because Python's `min` sorts ascending, the key must negate `local_pref` to make higher values sort first: `(-local_pref, as_path_len, next_hop)`.

`mpbgp_ipv6_unicast` takes the full list of candidate paths, raises `ValueError` if the list is empty (there is no route to select), and otherwise returns the path whose sort key is smallest — which corresponds to the best path under the decision process above.

`MpbgpPath` has four fields: `prefix` (str), `local_pref` (int), `as_path_len` (int), `next_hop` (str).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/ipv6.py`
- Symbols: `rank_mpbgp_path, mpbgp_ipv6_unicast`
- Why this target: define deterministic path ranking key, then apply best-path selection.
- Stage check: `routeforge check lab36`

Function contract for this stage:

- Symbol: `rank_mpbgp_path(path: MpbgpPath) -> tuple[int, int, str]`
- Required behavior: rank by local-pref desc, AS-path length asc, next-hop asc
- Symbol: `mpbgp_ipv6_unicast(paths: list[MpbgpPath]) -> MpbgpPath`
- Required behavior: raise `ValueError` on empty input; return path with best rank otherwise

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab36_mpbgp_ipv6_unicast`
3. Edit only `rank_mpbgp_path, mpbgp_ipv6_unicast` in `src/routeforge/runtime/ipv6.py`.
4. Run `routeforge check lab36` until it exits with status `0`.
5. Run `routeforge run lab36_mpbgp_ipv6_unicast --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab36_mpbgp_ipv6_unicast
routeforge check lab36

STATE=/tmp/routeforge-progress.json
routeforge run lab36_mpbgp_ipv6_unicast --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab36` passes when your implementation is complete for this stage.
- `mpbgp_update_rx` should print `[PASS]` (MP-BGP IPv6 updates are ingested).
- `mpbgp_afi_select` should print `[PASS]` (IPv6 unicast AFI/SAFI context is selected).
- `mpbgp_bestpath` should print `[PASS]` (best path chosen by deterministic policy).
- Run output includes checkpoints: BGP_MP_UPDATE_RX, BGP_AF_SELECT, BGP_MP_BESTPATH.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab36_mpbgp_ipv6_unicast --state-file "$STATE" --trace-out /tmp/lab36_mpbgp_ipv6_unicast.jsonl
routeforge debug replay --trace /tmp/lab36_mpbgp_ipv6_unicast.jsonl
routeforge debug explain --trace /tmp/lab36_mpbgp_ipv6_unicast.jsonl --step mpbgp_update_rx
```

Checkpoint guide:

- `BGP_MP_UPDATE_RX`: fires when the lab scenario receives the candidate MP-BGP IPv6 path set and begins best-path evaluation. If this checkpoint is missing, the scenario did not reach the update-ingest step.
- `BGP_AF_SELECT`: fires when the scenario locks onto the IPv6 unicast AFI/SAFI context before ranking paths. If this checkpoint is missing, the control-flow into the IPv6 selection branch is wrong.
- `BGP_MP_BESTPATH`: fires when best-path selection completes and a winner is returned. The function received a non-empty `paths` list and returned the `MpbgpPath` with the lowest rank key. If this checkpoint fires but the wrong path is selected, print the rank key for each candidate and confirm that `local_pref` is negated, `as_path_len` is used as-is, and `next_hop` breaks remaining ties lexicographically. A common mistake is forgetting the negation, which causes the path with the lowest local preference to win instead of the highest.

## Failure drills and troubleshooting flow

- Intentionally break `rank_mpbgp_path` or `mpbgp_ipv6_unicast` in `src/routeforge/runtime/ipv6.py` and rerun `routeforge check lab36` to confirm tests catch regressions.
- If `routeforge run lab36_mpbgp_ipv6_unicast --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- MP-BGP IPv6 route selection.
