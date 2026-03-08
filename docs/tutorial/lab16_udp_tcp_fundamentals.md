# Lab 16: UDP/TCP Fundamentals

## Learning objectives

- Implement `classify_flow, validate_udp` in `src/routeforge/runtime/transport.py`.
- Deliver `flow_classify`: 5-tuple flow classification is deterministic.
- Deliver `tcp_state_change`: TCP state machine reaches ESTABLISHED.
- Deliver `udp_validate`: UDP header validation accepts valid datagram.
- Validate internal behavior through checkpoints: FLOW_CLASSIFY, TCP_STATE_CHANGE, UDP_VALIDATE.

## Prerequisite recap

- Required prior labs: lab15_ospf_multi_area_abr.
- Confirm target mapping before coding with `routeforge show lab16_udp_tcp_fundamentals`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

TCP/UDP parsing and TCP state behavior for flow-level reasoning. Student-mode coding target for this stage is `src/routeforge/runtime/transport.py` (`classify_flow, validate_udp`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/transport.py`
- Symbols: `classify_flow, validate_udp`
- Why this target: Build deterministic 5-tuple flow identity and enforce UDP validity rules.
- Stage check: `routeforge check lab16`

Function contract for this stage:

- Symbol: `classify_flow(*, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: str) -> FlowKey`
- Required behavior: preserve endpoint/port values and normalize protocol casing deterministically
- Symbol: `validate_udp(*, length_bytes: int, checksum_valid: bool) -> bool`
- Required behavior: reject headers smaller than 8 bytes and reject invalid checksums

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab16_udp_tcp_fundamentals`
3. Edit only the listed symbols in `src/routeforge/runtime/transport.py`.
4. Run `routeforge check lab16` until it exits with status `0`.
5. Run `routeforge run lab16_udp_tcp_fundamentals --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab16_udp_tcp_fundamentals
routeforge check lab16

STATE=/tmp/routeforge-progress.json
routeforge run lab16_udp_tcp_fundamentals --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab16` passes when your implementation is complete for this stage.
- `flow_classify` should print `[PASS]` (5-tuple flow classification is deterministic).
- `tcp_state_change` should print `[PASS]` (TCP state machine reaches ESTABLISHED).
- `udp_validate` should print `[PASS]` (UDP header validation accepts valid datagram).
- Run output includes checkpoints: FLOW_CLASSIFY, TCP_STATE_CHANGE, UDP_VALIDATE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab16_udp_tcp_fundamentals --state-file "$STATE" --trace-out /tmp/lab16_udp_tcp_fundamentals.jsonl
routeforge debug replay --trace /tmp/lab16_udp_tcp_fundamentals.jsonl
routeforge debug explain --trace /tmp/lab16_udp_tcp_fundamentals.jsonl --step flow_classify
```

Checkpoint guide:

- `FLOW_CLASSIFY`: TCP/UDP parsing and TCP state behavior for flow-level reasoning.
- `TCP_STATE_CHANGE`: TCP/UDP parsing and TCP state behavior for flow-level reasoning.
- `UDP_VALIDATE`: TCP/UDP parsing and TCP state behavior for flow-level reasoning.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/transport.py` and rerun `routeforge check lab16` to confirm tests catch regressions.
- If `routeforge run lab16_udp_tcp_fundamentals --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 768 (UDP).
- RFC 9293 (TCP core behavior, obsoletes RFC 793).

## Concept Deepening Notes

Transport fundamentals in RouteForge are contract-first. Flow classification defines stable identity, TCP FSM tracks legal transitions, and UDP validation enforces minimum header sanity. Treat these as separate concerns so transport behavior remains explainable when BGP session logic starts consuming TCP outcomes.

## Checkpoint Guide (Expanded)

- `FLOW_CLASSIFY`: Confirm this marker appears when your implementation follows the intended decision path.
- `TCP_STATE_CHANGE`: Confirm this marker appears when your implementation follows the intended decision path.
- `UDP_VALIDATE`: Confirm this marker appears when your implementation follows the intended decision path.
