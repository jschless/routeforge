# Lab 25: Tunnels and IPsec

## Learning objectives

- Implement `evaluate_ipsec_policy` in `src/routeforge/runtime/tunnel_ipsec.py`.
- Deliver `tunnel_encap_push`: inner payload is encapsulated with deterministic outer tunnel headers.
- Deliver `tunnel_decap_pop`: tunnel decapsulation restores original inner packet metadata.
- Deliver `ipsec_policy_evaluate`: destination-prefix policy deterministically selects PROTECT action.
- Deliver `ipsec_sa_lookup`: security association lookup returns expected SPI for tunnel peer.
- Validate internal behavior through checkpoints: ENCAP_PUSH, ENCAP_POP, IPSEC_POLICY_EVALUATE, IPSEC_SA_LOOKUP.

## Prerequisite recap

- Required prior labs: lab24_bgp_scaling_patterns.
- Confirm target mapping before coding with `routeforge show lab25_tunnels_and_ipsec`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

Tunnel encapsulation/decapsulation and policy-driven IPsec outcomes. Student-mode coding target for this stage is `src/routeforge/runtime/tunnel_ipsec.py` (`evaluate_ipsec_policy`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/tunnel_ipsec.py`
- Symbols: `evaluate_ipsec_policy`
- Why this target: Classify flows as PROTECT or BYPASS by prefix policy.
- Stage check: `routeforge check lab25`

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab25_tunnels_and_ipsec`
3. Edit only the listed symbols in `src/routeforge/runtime/tunnel_ipsec.py`.
4. Run `routeforge check lab25` until it exits with status `0`.
5. Run `routeforge run lab25_tunnels_and_ipsec --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab25_tunnels_and_ipsec
routeforge check lab25

STATE=/tmp/routeforge-progress.json
routeforge run lab25_tunnels_and_ipsec --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab25` passes when your implementation is complete for this stage.
- `tunnel_encap_push` should print `[PASS]` (inner payload is encapsulated with deterministic outer tunnel headers).
- `tunnel_decap_pop` should print `[PASS]` (tunnel decapsulation restores original inner packet metadata).
- `ipsec_policy_evaluate` should print `[PASS]` (destination-prefix policy deterministically selects PROTECT action).
- `ipsec_sa_lookup` should print `[PASS]` (security association lookup returns expected SPI for tunnel peer).
- Run output includes checkpoints: ENCAP_PUSH, ENCAP_POP, IPSEC_POLICY_EVALUATE, IPSEC_SA_LOOKUP.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab25_tunnels_and_ipsec --state-file "$STATE" --trace-out /tmp/lab25_tunnels_and_ipsec.jsonl
routeforge debug replay --trace /tmp/lab25_tunnels_and_ipsec.jsonl
routeforge debug explain --trace /tmp/lab25_tunnels_and_ipsec.jsonl --step tunnel_encap_push
```

Checkpoint guide:

- `ENCAP_PUSH`: Tunnel encapsulation/decapsulation and policy-driven IPsec outcomes.
- `ENCAP_POP`: Tunnel encapsulation/decapsulation and policy-driven IPsec outcomes.
- `IPSEC_POLICY_EVALUATE`: Tunnel encapsulation/decapsulation and policy-driven IPsec outcomes.
- `IPSEC_SA_LOOKUP`: Tunnel encapsulation/decapsulation and policy-driven IPsec outcomes.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/tunnel_ipsec.py` and rerun `routeforge check lab25` to confirm tests catch regressions.
- If `routeforge run lab25_tunnels_and_ipsec --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 3022 (Traditional NAT).
- RFC 2474 / RFC 2475 (DiffServ marking and QoS service model).
- RFC 4301 (IPsec architecture).

