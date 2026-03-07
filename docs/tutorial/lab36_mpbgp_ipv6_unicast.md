# Lab 36: MP-BGP IPv6 Unicast

## Learning objectives

- Implement `mpbgp_ipv6_unicast` in `src/routeforge/runtime/phase2.py`.
- Deliver `mpbgp_update_rx`: MP-BGP IPv6 updates are ingested.
- Deliver `mpbgp_afi_select`: IPv6 unicast AFI/SAFI context is selected.
- Deliver `mpbgp_bestpath`: best path chosen by deterministic policy.
- Validate internal behavior through checkpoints: BGP_MP_UPDATE_RX, BGP_AF_SELECT, BGP_MP_BESTPATH.

## Prerequisite recap

- Required prior labs: `lab35_ospfv3_adjacency_and_lsdb`.
- Confirm target mapping before coding with `routeforge show lab36_mpbgp_ipv6_unicast`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Multiprotocol BGP path handling for IPv6 unicast. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`mpbgp_ipv6_unicast`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbol: `mpbgp_ipv6_unicast`
- Why this target: implement the core behavior required by the three lab steps.
- Stage check: `routeforge check lab36`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab36_mpbgp_ipv6_unicast`
3. Edit only `mpbgp_ipv6_unicast` in `src/routeforge/runtime/phase2.py`.
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

- `BGP_MP_UPDATE_RX`: first expected pipeline milestone.
- `BGP_AF_SELECT`: second expected pipeline milestone.
- `BGP_MP_BESTPATH`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `mpbgp_ipv6_unicast` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab36` to confirm tests catch regressions.
- If `routeforge run lab36_mpbgp_ipv6_unicast --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- MP-BGP IPv6 route selection.
