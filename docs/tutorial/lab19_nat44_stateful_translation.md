# Lab 19: NAT44 Stateful Translation

## Learning objectives

- Implement `Nat44Table.inbound_translate` in `src/routeforge/runtime/nat44.py`.
- Deliver `nat_session_create`: outbound flow creates deterministic NAT session.
- Deliver `nat_inbound_translate`: return flow matches existing NAT session.
- Deliver `nat_session_expire`: idle NAT session ages out deterministically.
- Validate internal behavior through checkpoints: NAT_SESSION_CREATE, NAT_TRANSLATE_OUTBOUND, NAT_TRANSLATE_INBOUND, NAT_SESSION_EXPIRE.

## Prerequisite recap

- Required prior labs: lab18_acl_pipeline.
- Confirm target mapping before coding with `routeforge show lab19_nat44_stateful_translation`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Stateful NAT44 creation, reuse, return matching, and expiration. Student-mode coding target for this stage is `src/routeforge/runtime/nat44.py` (`Nat44Table.inbound_translate`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/nat44.py`
- Symbols: `Nat44Table.inbound_translate`
- Why this target: Translate return traffic using NAT session state.
- Stage check: `routeforge check lab19`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab19_nat44_stateful_translation`
3. Edit only the listed symbols in `src/routeforge/runtime/nat44.py`.
4. Run `routeforge check lab19` until it exits with status `0`.
5. Run `routeforge run lab19_nat44_stateful_translation --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab19_nat44_stateful_translation
routeforge check lab19

STATE=/tmp/routeforge-progress.json
routeforge run lab19_nat44_stateful_translation --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab19` passes when your implementation is complete for this stage.
- `nat_session_create` should print `[PASS]` (outbound flow creates deterministic NAT session).
- `nat_inbound_translate` should print `[PASS]` (return flow matches existing NAT session).
- `nat_session_expire` should print `[PASS]` (idle NAT session ages out deterministically).
- Run output includes checkpoints: NAT_SESSION_CREATE, NAT_TRANSLATE_OUTBOUND, NAT_TRANSLATE_INBOUND, NAT_SESSION_EXPIRE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab19_nat44_stateful_translation --state-file "$STATE" --trace-out /tmp/lab19_nat44_stateful_translation.jsonl
routeforge debug replay --trace /tmp/lab19_nat44_stateful_translation.jsonl
routeforge debug explain --trace /tmp/lab19_nat44_stateful_translation.jsonl --step nat_session_create
```

Checkpoint guide:

- `NAT_SESSION_CREATE`: Stateful NAT44 creation, reuse, return matching, and expiration.
- `NAT_TRANSLATE_OUTBOUND`: Stateful NAT44 creation, reuse, return matching, and expiration.
- `NAT_TRANSLATE_INBOUND`: Stateful NAT44 creation, reuse, return matching, and expiration.
- `NAT_SESSION_EXPIRE`: Stateful NAT44 creation, reuse, return matching, and expiration.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/nat44.py` and rerun `routeforge check lab19` to confirm tests catch regressions.
- If `routeforge run lab19_nat44_stateful_translation --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 3022 (Traditional NAT).
- RFC 2474 / RFC 2475 (DiffServ marking and QoS service model).
- RFC 4301 (IPsec architecture).

