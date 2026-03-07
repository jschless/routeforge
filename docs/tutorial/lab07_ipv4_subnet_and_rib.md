# Lab 07: IPv4 Subnet and RIB

## Learning objectives

- Implement `RibTable.lookup` in `src/routeforge/runtime/l3.py`.
- Deliver `rib_install_and_lpm`: route install and deterministic longest-prefix selection.
- Validate internal behavior through checkpoints: RIB_ROUTE_INSTALL, ROUTE_LOOKUP, ROUTE_SELECT.

## Prerequisite recap

- Required prior labs: lab06_arp_and_adjacency.
- Confirm target mapping before coding with `routeforge show lab07_ipv4_subnet_and_rib`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Connected/static route install and deterministic LPM selection. Student-mode coding target for this stage is `src/routeforge/runtime/l3.py` (`RibTable.lookup`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/l3.py`
- Symbols: `RibTable.lookup`
- Why this target: Perform deterministic LPM route lookup.
- Stage check: `routeforge check lab07`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab07_ipv4_subnet_and_rib`
3. Edit only the listed symbols in `src/routeforge/runtime/l3.py`.
4. Run `routeforge check lab07` until it exits with status `0`.
5. Run `routeforge run lab07_ipv4_subnet_and_rib --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab07_ipv4_subnet_and_rib
routeforge check lab07

STATE=/tmp/routeforge-progress.json
routeforge run lab07_ipv4_subnet_and_rib --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab07` passes when your implementation is complete for this stage.
- `rib_install_and_lpm` should print `[PASS]` (route install and deterministic longest-prefix selection).
- Run output includes checkpoints: RIB_ROUTE_INSTALL, ROUTE_LOOKUP, ROUTE_SELECT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab07_ipv4_subnet_and_rib --state-file "$STATE" --trace-out /tmp/lab07_ipv4_subnet_and_rib.jsonl
routeforge debug replay --trace /tmp/lab07_ipv4_subnet_and_rib.jsonl
routeforge debug explain --trace /tmp/lab07_ipv4_subnet_and_rib.jsonl --step rib_install_and_lpm
```

Checkpoint guide:

- `RIB_ROUTE_INSTALL`: Connected/static route install and deterministic LPM selection.
- `ROUTE_LOOKUP`: Connected/static route install and deterministic LPM selection.
- `ROUTE_SELECT`: Connected/static route install and deterministic LPM selection.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/l3.py` and rerun `routeforge check lab07` to confirm tests catch regressions.
- If `routeforge run lab07_ipv4_subnet_and_rib --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 791 (IPv4).
- RFC 792 (ICMP).
- RFC 826 (ARP).
