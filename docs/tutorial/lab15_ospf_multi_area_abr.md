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

Multi-area behavior with ABR summary propagation. Student-mode coding target for this stage is `src/routeforge/runtime/ospf.py` (`originate_summaries`).

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

- `OSPF_SUMMARY_ORIGINATE`: Multi-area behavior with ABR summary propagation.
- `OSPF_INTERAREA_ROUTE_INSTALL`: Multi-area behavior with ABR summary propagation.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/ospf.py` and rerun `routeforge check lab15` to confirm tests catch regressions.
- If `routeforge run lab15_ospf_multi_area_abr --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 2328 (OSPFv2).

