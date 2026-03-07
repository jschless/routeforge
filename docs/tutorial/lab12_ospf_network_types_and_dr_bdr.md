# Lab 12: OSPF Network Types and DR/BDR

## Learning objectives

- Implement `failover_dr_bdr` in `src/routeforge/runtime/ospf.py`.
- Deliver `ospf_dr_bdr_election`: DR/BDR selection follows deterministic priority and router-id ordering.
- Deliver `ospf_dr_failover`: BDR is promoted to DR when original DR fails.
- Validate internal behavior through checkpoints: OSPF_DR_ELECT, OSPF_BDR_ELECT, OSPF_DR_FAILOVER.

## Prerequisite recap

- Required prior labs: lab11_ospf_adjacency_fsm.
- Confirm target mapping before coding with `routeforge show lab12_ospf_network_types_and_dr_bdr`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

OSPF network type behavior and DR/BDR election/failover. Student-mode coding target for this stage is `src/routeforge/runtime/ospf.py` (`failover_dr_bdr`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/ospf.py`
- Symbols: `failover_dr_bdr`
- Why this target: Re-elect DR/BDR after node loss.
- Stage check: `routeforge check lab12`

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

- `OSPF_DR_ELECT`: OSPF network type behavior and DR/BDR election/failover.
- `OSPF_BDR_ELECT`: OSPF network type behavior and DR/BDR election/failover.
- `OSPF_DR_FAILOVER`: OSPF network type behavior and DR/BDR election/failover.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/ospf.py` and rerun `routeforge check lab12` to confirm tests catch regressions.
- If `routeforge run lab12_ospf_network_types_and_dr_bdr --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 2328 (OSPFv2).

