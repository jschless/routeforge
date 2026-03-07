# Lab 09: ICMP and Control Responses

## Learning objectives

- Produce ICMP echo reply for valid echo request handling.
- Generate ICMP unreachable when no route exists.
- Generate ICMP time exceeded for TTL expiry.

## Prerequisite recap

- Complete `lab08_fib_forwarding_pipeline`.
- Understand how forwarding failures map to control-plane ICMP output.

## Concept walkthrough

`lab09` adds control responses for common operational behaviors. Data-plane outcomes now drive ICMP responses that are deterministic and testable.

## Implementation TODO map

- `src/routeforge/runtime/l3.py`: ICMP control decision helper.
- `src/routeforge/labs/exercises.py`: echo/unreachable/time-exceeded scenarios.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab09_icmp_and_control_responses --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection --completed lab06_arp_and_adjacency --completed lab07_ipv4_subnet_and_rib --completed lab08_fib_forwarding_pipeline
```

Expected:

- `icmp_echo_reply` step `PASS`.
- `icmp_unreachable` step `PASS`.
- `icmp_time_exceeded` step `PASS`.
- Checkpoints include `ICMP_ECHO_REPLY`, `ICMP_UNREACHABLE`, `ICMP_TIME_EXCEEDED`.

## Debug trace checkpoints and interpretation guidance

- `ICMP_ECHO_REPLY`: reply generated for echo request.
- `ICMP_UNREACHABLE`: route failure translated to unreachable response.
- `ICMP_TIME_EXCEEDED`: TTL expiry translated to time-exceeded response.

## Failure drills and troubleshooting flow

- Change packet type away from echo request and inspect no-op control behavior.
- Vary TTL values to confirm transition between reply and time-exceeded.

## Standards and references

- RFC 792 (ICMP).
