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

Deterministic SPF, ECMP policy, and route installation. Student-mode coding target for this stage is `src/routeforge/runtime/ospf.py` (`run_spf`).

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

- `OSPF_SPF_RUN`: Deterministic SPF, ECMP policy, and route installation.
- `RIB_ROUTE_INSTALL`: Deterministic SPF route install into RIB after SPF computation.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/ospf.py` and rerun `routeforge check lab14` to confirm tests catch regressions.
- If `routeforge run lab14_ospf_spf_and_route_install --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 2328 (OSPFv2).
