from __future__ import annotations

from routeforge.runtime.stp import (
    Bridge,
    BridgeID,
    Link,
    PortRef,
    bpdu_guard_decision,
    compute_stp,
    remove_link,
    role_changes,
)


def test_stp_root_election_and_roles_are_deterministic() -> None:
    bridges = [
        Bridge(node_id="S1", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:01")),
        Bridge(node_id="S2", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:02")),
        Bridge(node_id="S3", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:03")),
    ]
    links = [
        Link(a=PortRef("S1", "Gi0/1"), b=PortRef("S2", "Gi0/1"), cost=4),
        Link(a=PortRef("S1", "Gi0/2"), b=PortRef("S3", "Gi0/1"), cost=4),
        Link(a=PortRef("S2", "Gi0/2"), b=PortRef("S3", "Gi0/2"), cost=4),
    ]

    result = compute_stp(bridges, links)

    assert result.root_node_id == "S1"
    assert result.root_port_by_node["S2"] == "Gi0/1"
    assert result.root_port_by_node["S3"] == "Gi0/1"
    assert result.port_roles[("S2", "Gi0/2")] == "DESIGNATED"
    assert result.port_roles[("S3", "Gi0/2")] == "ALTERNATE"


def test_stp_topology_change_and_guard_action() -> None:
    bridges = [
        Bridge(node_id="S1", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:01")),
        Bridge(node_id="S2", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:02")),
        Bridge(node_id="S3", bridge_id=BridgeID(priority=32768, mac="00:00:00:00:00:03")),
    ]
    links = [
        Link(a=PortRef("S1", "Gi0/1"), b=PortRef("S2", "Gi0/1"), cost=4),
        Link(a=PortRef("S1", "Gi0/2"), b=PortRef("S3", "Gi0/1"), cost=4),
        Link(a=PortRef("S2", "Gi0/2"), b=PortRef("S3", "Gi0/2"), cost=4),
    ]

    before = compute_stp(bridges, links)
    after = compute_stp(bridges, remove_link(links, a=("S1", "Gi0/2"), b=("S3", "Gi0/1")))
    changes = role_changes(before, after)

    assert ("S3", "Gi0/1") in changes
    assert after.root_port_by_node["S3"] == "Gi0/2"

    guard = bpdu_guard_decision(port=("S2", "Gi0/10"), edge_port=True, bpdu_received=True)
    assert guard.action == "ERRDISABLE"
