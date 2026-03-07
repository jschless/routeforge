# Lab 06: ARP and Adjacency

## Learning objectives

- Model ARP miss behavior with pending packet queueing.
- Process ARP reply events into cache updates.
- Release queued packets deterministically after adjacency resolution.

## Prerequisite recap

- Complete `lab05_stp_convergence_and_protection`.
- Understand next-hop resolution requirements for L3 forwarding.

## Concept walkthrough

`lab06` bridges L2 and L3 behavior with adjacency resolution. Packets to unknown next-hops are queued while ARP is requested. ARP replies install cache entries and release pending packets.

## Implementation TODO map

- `src/routeforge/runtime/adjacency.py`: ARP cache and pending-queue behavior.
- `src/routeforge/labs/exercises.py`: request/reply lab flow and assertions.

## Verification commands and expected outputs

```bash
PYTHONPATH=src python -m routeforge run lab06_arp_and_adjacency --completed lab01_frame_and_headers --completed lab02_mac_learning_switch --completed lab03_vlan_and_trunks --completed lab04_stp --completed lab05_stp_convergence_and_protection
```

Expected:

- `arp_request_and_queue` step `PASS`.
- `arp_reply_and_cache_update` step `PASS`.
- Checkpoints include `ARP_REQUEST_TX`, `ARP_REPLY_RX`, `ARP_CACHE_UPDATE`.

## Debug trace checkpoints and interpretation guidance

- `ARP_REQUEST_TX`: unresolved next-hop triggered ARP request emission.
- `ARP_REPLY_RX`: ARP reply received from neighbor.
- `ARP_CACHE_UPDATE`: adjacency table updated and queued packet(s) released.

## Failure drills and troubleshooting flow

- Queue multiple packets before reply and confirm all are released in order.
- Reply with unexpected mapping and verify deterministic cache overwrite behavior.

## Standards and references

- RFC 826 (ARP).
