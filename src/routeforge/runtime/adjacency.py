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
        # TODO(student): install ARP cache entry and release pending packets.
        raise NotImplementedError("TODO: implement ArpAdjacencyTable.resolve")
