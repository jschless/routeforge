# Lab 13: OSPF LSA Flooding and LSDB

## Learning objectives

- Implement `Lsdb.age_tick` in `src/routeforge/runtime/ospf.py`.
- Deliver `ospf_lsa_install`: new LSA is installed into LSDB.
- Deliver `ospf_lsa_refresh`: LSA refresh increments sequence and resets age.
- Deliver `ospf_lsa_age_out`: max-age LSAs are removed deterministically.
- Validate internal behavior through checkpoints: OSPF_LSA_INSTALL, OSPF_LSA_REFRESH, OSPF_LSA_AGE_OUT.

## Prerequisite recap

- Required prior labs: lab12_ospf_network_types_and_dr_bdr.
- Confirm target mapping before coding with `routeforge show lab13_ospf_lsa_flooding_and_lsdb`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

LSA flooding, sequence handling, and aging in LSDB. Student-mode coding target for this stage is `src/routeforge/runtime/ospf.py` (`Lsdb.age_tick`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/ospf.py`
- Symbols: `Lsdb.age_tick`
- Why this target: Age LSAs and remove max-age entries.
- Stage check: `routeforge check lab13`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab13_ospf_lsa_flooding_and_lsdb`
3. Edit only the listed symbols in `src/routeforge/runtime/ospf.py`.
4. Run `routeforge check lab13` until it exits with status `0`.
5. Run `routeforge run lab13_ospf_lsa_flooding_and_lsdb --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab13_ospf_lsa_flooding_and_lsdb
routeforge check lab13

STATE=/tmp/routeforge-progress.json
routeforge run lab13_ospf_lsa_flooding_and_lsdb --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab13` passes when your implementation is complete for this stage.
- `ospf_lsa_install` should print `[PASS]` (new LSA is installed into LSDB).
- `ospf_lsa_refresh` should print `[PASS]` (LSA refresh increments sequence and resets age).
- `ospf_lsa_age_out` should print `[PASS]` (max-age LSAs are removed deterministically).
- Run output includes checkpoints: OSPF_LSA_INSTALL, OSPF_LSA_REFRESH, OSPF_LSA_AGE_OUT.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab13_ospf_lsa_flooding_and_lsdb --state-file "$STATE" --trace-out /tmp/lab13_ospf_lsa_flooding_and_lsdb.jsonl
routeforge debug replay --trace /tmp/lab13_ospf_lsa_flooding_and_lsdb.jsonl
routeforge debug explain --trace /tmp/lab13_ospf_lsa_flooding_and_lsdb.jsonl --step ospf_lsa_install
```

Checkpoint guide:

- `OSPF_LSA_INSTALL`: LSA flooding, sequence handling, and aging in LSDB.
- `OSPF_LSA_REFRESH`: LSA flooding, sequence handling, and aging in LSDB.
- `OSPF_LSA_AGE_OUT`: LSA flooding, sequence handling, and aging in LSDB.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/ospf.py` and rerun `routeforge check lab13` to confirm tests catch regressions.
- If `routeforge run lab13_ospf_lsa_flooding_and_lsdb --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 2328 (OSPFv2).

