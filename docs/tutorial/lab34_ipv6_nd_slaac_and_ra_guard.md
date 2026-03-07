# Lab 34: IPv6 ND, SLAAC, and RA Guard

## Learning objectives

- Implement `ipv6_nd_slaac_ra_guard` in `src/routeforge/runtime/phase2.py`.
- Deliver `ipv6_nd_learn`: neighbor discovery entry is learned on trusted RA.
- Deliver `ipv6_slaac_apply`: SLAAC derives deterministic global address.
- Deliver `ipv6_ra_guard_drop`: untrusted RA is blocked by RA guard.
- Validate internal behavior through checkpoints: ND_NEIGHBOR_LEARN, SLAAC_PREFIX_APPLY, RA_GUARD_DROP.

## Prerequisite recap

- Required prior labs: `lab33_fhrp_tracking_and_failover`.
- Confirm target mapping before coding with `routeforge show lab34_ipv6_nd_slaac_and_ra_guard`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

IPv6 host onboarding flow with RA trust boundaries. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`ipv6_nd_slaac_ra_guard`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbol: `ipv6_nd_slaac_ra_guard`
- Why this target: implement the core behavior required by the three lab steps.
- Stage check: `routeforge check lab34`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab34_ipv6_nd_slaac_and_ra_guard`
3. Edit only `ipv6_nd_slaac_ra_guard` in `src/routeforge/runtime/phase2.py`.
4. Run `routeforge check lab34` until it exits with status `0`.
5. Run `routeforge run lab34_ipv6_nd_slaac_and_ra_guard --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab34_ipv6_nd_slaac_and_ra_guard
routeforge check lab34

STATE=/tmp/routeforge-progress.json
routeforge run lab34_ipv6_nd_slaac_and_ra_guard --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab34` passes when your implementation is complete for this stage.
- `ipv6_nd_learn` should print `[PASS]` (neighbor discovery entry is learned on trusted RA).
- `ipv6_slaac_apply` should print `[PASS]` (SLAAC derives deterministic global address).
- `ipv6_ra_guard_drop` should print `[PASS]` (untrusted RA is blocked by RA guard).
- Run output includes checkpoints: ND_NEIGHBOR_LEARN, SLAAC_PREFIX_APPLY, RA_GUARD_DROP.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab34_ipv6_nd_slaac_and_ra_guard --state-file "$STATE" --trace-out /tmp/lab34_ipv6_nd_slaac_and_ra_guard.jsonl
routeforge debug replay --trace /tmp/lab34_ipv6_nd_slaac_and_ra_guard.jsonl
routeforge debug explain --trace /tmp/lab34_ipv6_nd_slaac_and_ra_guard.jsonl --step ipv6_nd_learn
```

Checkpoint guide:

- `ND_NEIGHBOR_LEARN`: first expected pipeline milestone.
- `SLAAC_PREFIX_APPLY`: second expected pipeline milestone.
- `RA_GUARD_DROP`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `ipv6_nd_slaac_ra_guard` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab34` to confirm tests catch regressions.
- If `routeforge run lab34_ipv6_nd_slaac_and_ra_guard --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- IPv6 ND, SLAAC, and RA guard controls.
