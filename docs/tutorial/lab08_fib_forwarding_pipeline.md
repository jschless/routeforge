# Lab 08: FIB Forwarding Pipeline

## Learning objectives

- Use selected route information to forward IPv4 traffic.
- Apply deterministic TTL decrement semantics.
- Emit explicit drop checkpoints when forwarding cannot continue.

## Prerequisite recap

- Complete `lab07_ipv4_subnet_and_rib`.
- Understand distinction between route lookup and forwarding action.

## Concept walkthrough

`lab08` turns routing decisions into forwarding outcomes. A route hit forwards packets and decrements TTL; missing route or invalid TTL causes deterministic drops.

## Implementation TODO map

- `src/routeforge/runtime/l3.py`: forwarding decision logic.
- `src/routeforge/labs/exercises.py`: forward and drop verification steps.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab08_fib_forwarding_pipeline --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection --completed lab06_arp_and_adjacency --completed lab07_ipv4_subnet_and_rib
```

Expected:

- `fib_forward_and_ttl` step `PASS`.
- `fib_drop_no_route` step `PASS`.
- Checkpoints include `FIB_FORWARD`, `FIB_DROP`, `TTL_DECREMENT`.

## Debug trace checkpoints and interpretation guidance

- `FIB_FORWARD`: packet forwarded toward next hop.
- `TTL_DECREMENT`: forwarding reduced TTL by one.
- `FIB_DROP`: forwarding terminated with a normalized reason.

## Failure drills and troubleshooting flow

- Force TTL=1 and verify `TTL_EXPIRED` drop behavior.
- Remove route and verify `NO_ROUTE` drop reason.

## Standards and references

- RFC 791 TTL behavior.
