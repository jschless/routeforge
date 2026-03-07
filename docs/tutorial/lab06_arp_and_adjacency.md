# Lab 06: ARP and Adjacency

## Learning objectives

- Implement `ArpAdjacencyTable.queue_packet, ArpAdjacencyTable.resolve` in `src/routeforge/runtime/adjacency.py`.
- Deliver `arp_request_and_queue`: ARP miss queues packet and emits request.
- Deliver `arp_reply_and_cache_update`: ARP reply installs cache entry and releases pending packets.
- Validate internal behavior through checkpoints: ARP_REQUEST_TX, ARP_REPLY_RX, ARP_CACHE_UPDATE.

## Prerequisite recap

- Required prior labs: lab05_stp_convergence_and_protection.
- Confirm target mapping before coding with `routeforge show lab06_arp_and_adjacency`.
- Work on the `student` branch so you are editing TODO stubs, not solved reference code.

## Concept walkthrough

ARP resolution, cache updates, and pending queue behavior. Student-mode coding target for this stage is `src/routeforge/runtime/adjacency.py` (`ArpAdjacencyTable.queue_packet, ArpAdjacencyTable.resolve`).

## Implementation TODO map

Primary target for this stage:

- File: `src/routeforge/runtime/adjacency.py`
- Symbols: `ArpAdjacencyTable.queue_packet, ArpAdjacencyTable.resolve`
- Why this target: Implement both sides of ARP miss handling: queue-on-miss and release-on-resolve.
- Stage check: `routeforge check lab06`

Function contract for this stage:

- Symbol: `ArpAdjacencyTable.queue_packet(self, *, next_hop_ip: str, packet_id: str) -> bool`
- Required behavior: append packet to per-next-hop queue, return `True` only for first unresolved packet
- Symbol: `ArpAdjacencyTable.resolve(self, *, next_hop_ip: str, mac: str) -> list[str]`
- Required behavior: install cache entry and return all queued packets for that next hop in order

Suggested student walkthrough:

1. `git switch student`
2. `routeforge show lab06_arp_and_adjacency`
3. Edit only the listed symbols in `src/routeforge/runtime/adjacency.py`.
4. Run `routeforge check lab06` until it exits with status `0`.
5. Run `routeforge run lab06_arp_and_adjacency --state-file "$STATE"` to confirm visible lab behavior and progress state updates.

## Verification commands and expected outputs

```bash
routeforge show lab06_arp_and_adjacency
routeforge check lab06

STATE=/tmp/routeforge-progress.json
routeforge run lab06_arp_and_adjacency --state-file "$STATE"
```

Expected outcomes:

- `routeforge show` prints `student.stage`, `student.target`, and `student.symbols` matching this chapter.
- `routeforge check lab06` passes when your implementation is complete for this stage.
- `arp_request_and_queue` should print `[PASS]` (ARP miss queues packet and emits request).
- `arp_reply_and_cache_update` should print `[PASS]` (ARP reply installs cache entry and releases pending packets).
- Run output includes checkpoints: ARP_REQUEST_TX, ARP_REPLY_RX, ARP_CACHE_UPDATE.

## Debug trace checkpoints and interpretation guidance

Generate trace artifacts when a step fails:

```bash
routeforge run lab06_arp_and_adjacency --state-file "$STATE" --trace-out /tmp/lab06_arp_and_adjacency.jsonl
routeforge debug replay --trace /tmp/lab06_arp_and_adjacency.jsonl
routeforge debug explain --trace /tmp/lab06_arp_and_adjacency.jsonl --step arp_request_and_queue
```

Checkpoint guide:

- `ARP_REQUEST_TX`: ARP resolution, cache updates, and pending queue behavior.
- `ARP_REPLY_RX`: ARP resolution, cache updates, and pending queue behavior.
- `ARP_CACHE_UPDATE`: ARP resolution, cache updates, and pending queue behavior.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/adjacency.py` and rerun `routeforge check lab06` to confirm tests catch regressions.
- If `routeforge run lab06_arp_and_adjacency --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 791 (IPv4).
- RFC 792 (ICMP).
- RFC 826 (ARP).
