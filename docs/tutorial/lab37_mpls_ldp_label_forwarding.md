# Lab 37: MPLS LDP and Label Forwarding

## Learning objectives

- Implement `mpls_ldp_lfib` in `src/routeforge/runtime/phase2.py`.
- Deliver `ldp_label_alloc`: LDP allocates local label for FEC.
- Deliver `lfib_program`: LFIB programs outgoing label mapping.
- Deliver `mpls_swap_forward`: label swap forwarding path executes deterministically.
- Validate internal behavior through checkpoints: LDP_LABEL_ALLOC, LFIB_PROGRAM, MPLS_SWAP_FORWARD.

## Prerequisite recap

- Required prior labs: `lab36_mpbgp_ipv6_unicast`.
- Confirm target mapping before coding with `routeforge show lab37_mpls_ldp_label_forwarding`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Label distribution and LFIB programming for MPLS forwarding. Student-mode coding target for this stage is `src/routeforge/runtime/phase2.py` (`mpls_ldp_lfib`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/phase2.py`
- Symbol: `mpls_ldp_lfib`
- Why this target: implement the core behavior required by the three lab steps.
- Stage check: `routeforge check lab37`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab37_mpls_ldp_label_forwarding`
3. Edit only `mpls_ldp_lfib` in `src/routeforge/runtime/phase2.py`.
4. Run `routeforge check lab37` until it exits with status `0`.
5. Run `routeforge run lab37_mpls_ldp_label_forwarding --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab37_mpls_ldp_label_forwarding
routeforge check lab37

STATE=/tmp/routeforge-progress.json
routeforge run lab37_mpls_ldp_label_forwarding --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab37` passes when your implementation is complete for this stage.
- `ldp_label_alloc` should print `[PASS]` (LDP allocates local label for FEC).
- `lfib_program` should print `[PASS]` (LFIB programs outgoing label mapping).
- `mpls_swap_forward` should print `[PASS]` (label swap forwarding path executes deterministically).
- Run output includes checkpoints: LDP_LABEL_ALLOC, LFIB_PROGRAM, MPLS_SWAP_FORWARD.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab37_mpls_ldp_label_forwarding --state-file "$STATE" --trace-out /tmp/lab37_mpls_ldp_label_forwarding.jsonl
routeforge debug replay --trace /tmp/lab37_mpls_ldp_label_forwarding.jsonl
routeforge debug explain --trace /tmp/lab37_mpls_ldp_label_forwarding.jsonl --step ldp_label_alloc
```

Checkpoint guide:

- `LDP_LABEL_ALLOC`: first expected pipeline milestone.
- `LFIB_PROGRAM`: second expected pipeline milestone.
- `MPLS_SWAP_FORWARD`: third expected pipeline milestone.

## Failure drills and troubleshooting flow

- Intentionally break `mpls_ldp_lfib` in `src/routeforge/runtime/phase2.py` and rerun `routeforge check lab37` to confirm tests catch regressions.
- If `routeforge run lab37_mpls_ldp_label_forwarding --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- MPLS LDP and LFIB behavior.
