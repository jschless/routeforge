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

### What problem does ARP solve?

IP routing determines *which host* to send to (L3), but Ethernet requires a *MAC address* (L2) to actually deliver the frame.  ARP (Address Resolution Protocol) bridges this gap by broadcasting "who has IP X?" and caching the response so future packets can be sent directly without asking again.

### Topology

```
Host A              Router R1              Host B
(10.0.0.1)  ──eth0──(10.0.0.254)──eth1──  (10.0.0.2)
```

When R1 needs to forward a packet to Host B, it must look up B's MAC address.  If the ARP cache doesn't have an entry, R1 queues the packet and sends an ARP request on the outgoing interface.

### How it works

1. **Packet arrives** for a next-hop IP not in the ARP cache.
2. **ARP miss** → `queue_packet()` returns `True` (first queued packet) → router sends ARP request broadcast.
3. More packets for the same IP → `queue_packet()` returns `False` (already pending) → they join the queue.
4. **ARP reply arrives** → `resolve()` is called:
   - Install `(next_hop_ip → mac)` in the cache.
   - Pop and return all queued packet IDs so the caller can forward them now.

### What correct behavior looks like

- `resolve(next_hop_ip="10.0.0.2", mac="00:bb:cc:dd:ee:ff")` after queuing two packets:
  - cache now has `{"10.0.0.2": "00:bb:cc:dd:ee:ff"}`
  - returns `["pkt-1", "pkt-2"]` (the queued packet IDs)
  - pending queue for `"10.0.0.2"` is cleared

Student-mode coding target for this stage is `src/routeforge/runtime/adjacency.py` (`ArpAdjacencyTable.resolve`).

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

- `ARP_REQUEST_TX`: An ARP request was queued for transmission — first packet to an unknown
  next-hop triggered the request.  If missing, `queue_packet()` may not be returning `True`
  for the first miss, or the scenario isn't wiring up the return value correctly.
- `ARP_REPLY_RX`: An ARP reply was received and `resolve()` was called.  If missing, the
  scenario didn't reach the reply step — likely because the request step failed first.
- `ARP_CACHE_UPDATE`: `resolve()` successfully installed the cache entry.  If missing but
  `ARP_REPLY_RX` fired, your `resolve()` raised an exception before updating `self.cache`.

## Failure drills and troubleshooting flow

- Intentionally break one listed symbol in `src/routeforge/runtime/adjacency.py` and rerun `routeforge check lab06` to confirm tests catch regressions.
- If `routeforge run lab06_arp_and_adjacency --state-file "$STATE"` prints `blocked`, complete prerequisites first or mark prior labs in your state file.
- Use `routeforge debug explain ... --step <failing_step>` to isolate exactly which assertion failed.
- Compare your local output with the expected steps/checkpoints in this chapter before changing unrelated files.

## Standards and references

- RFC 791 (IPv4).
- RFC 792 (ICMP).
- RFC 826 (ARP).

