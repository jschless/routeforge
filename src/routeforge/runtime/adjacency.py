"""ARP adjacency cache and pending queue helpers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ArpAdjacencyTable:
    cache: dict[str, str] = field(default_factory=dict)
    pending_packets: dict[str, list[str]] = field(default_factory=dict)

    def lookup(self, ip: str) -> str | None:
        return self.cache.get(ip)

    def queue_packet(self, *, next_hop_ip: str, packet_id: str) -> bool:
        queue = self.pending_packets.setdefault(next_hop_ip, [])
        should_send_request = len(queue) == 0 and next_hop_ip not in self.cache
        queue.append(packet_id)
        return should_send_request

    def resolve(self, *, next_hop_ip: str, mac: str) -> list[str]:
        """Install an ARP cache entry and release all queued packets.

        Steps:
        1. Store ``mac`` in ``self.cache`` keyed by ``next_hop_ip``.
        2. Pop and return all packet IDs from ``self.pending_packets[next_hop_ip]``
           (the queue built by ``queue_packet``).
        3. Remove the ``next_hop_ip`` key from ``self.pending_packets``.
        4. Return the list of released packet IDs (may be empty if nothing was queued).
        """
        self.cache[next_hop_ip] = mac
        released = self.pending_packets.pop(next_hop_ip, [])
        return released
