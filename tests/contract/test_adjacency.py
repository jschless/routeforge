from __future__ import annotations

from routeforge.runtime.adjacency import ArpAdjacencyTable


def test_arp_queue_and_resolve_flow() -> None:
    table = ArpAdjacencyTable()

    first_request = table.queue_packet(next_hop_ip="192.0.2.1", packet_id="pkt-1")
    second_request = table.queue_packet(next_hop_ip="192.0.2.1", packet_id="pkt-2")
    assert first_request is True
    assert second_request is False

    released = table.resolve(next_hop_ip="192.0.2.1", mac="00:de:ad:be:ef:01")
    assert released == ["pkt-1", "pkt-2"]
    assert table.lookup("192.0.2.1") == "00:de:ad:be:ef:01"
