# Lab 21: BGP Session FSM and Transport

## Learning objectives

- Model deterministic BGP FSM transitions from `IDLE` to `ESTABLISHED`.
- Validate OPEN/KEEPALIVE sequencing behavior.
- Observe transport-timer reset behavior (hold timer expiry).

## Prerequisite recap

- Complete `lab20_qos_marking_and_queueing`.
- Recall TCP session establishment from `lab16_udp_tcp_fundamentals`.

## Concept walkthrough

`lab21` starts the BGP track. The scenario models a minimal FSM path (`IDLE -> CONNECT -> OPENSENT -> ESTABLISHED`) and timer-driven fallback to `IDLE`.

## Implementation TODO map

- `src/routeforge/runtime/bgp.py`: BGP FSM transition helper.
- `src/routeforge/labs/exercises.py`: session establish/reset lab scenario.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab21_bgp_session_fsm_and_transport --completed <all-labs-lab01-through-lab20>
```

Expected:

- `bgp_open_and_establish` step `PASS`.
- `bgp_hold_timer_reset` step `PASS`.
- Checkpoints include `BGP_OPEN_RX` and `BGP_SESSION_CHANGE`.

## Debug trace checkpoints and interpretation guidance

- `BGP_OPEN_RX`: OPEN message received and accepted.
- `BGP_SESSION_CHANGE`: FSM transition occurred.

## Failure drills and troubleshooting flow

- Trigger `NOTIFICATION_RX` or hold-timer expiry and confirm reset to `IDLE`.
- Skip KEEPALIVE handling and confirm the session never reaches `ESTABLISHED`.

## Standards and references

- RFC 4271 (BGP-4), session state and message handling model.
