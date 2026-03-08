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

    assert result.root_node_id == "S1", (
        f"Expected root bridge S1 (lowest MAC 00:00:00:00:00:01) but got {result.root_node_id!r}; "
        "compute_stp must elect the bridge with lowest BridgeID (priority, then MAC) as root"
    )
    assert result.root_port_by_node["S2"] == "Gi0/1", (
        f"Expected S2 root port Gi0/1 (direct link to S1, cost=4) but got {result.root_port_by_node.get('S2')!r}; "
        "the root port is the port with the lowest root path cost to the root bridge"
    )
    assert result.root_port_by_node["S3"] == "Gi0/1", (
        f"Expected S3 root port Gi0/1 (direct link to S1, cost=4) but got {result.root_port_by_node.get('S3')!r}; "
        "direct path to S1 (cost=4) is cheaper than via S2 (cost=4+4=8)"
    )
    assert result.port_roles[("S2", "Gi0/2")] == "DESIGNATED", (
        f"Expected S2:Gi0/2 DESIGNATED but got {result.port_roles.get(('S2', 'Gi0/2'))!r}; "
        "on the S2-S3 segment, S2 has the lower accumulated root cost so its port is DESIGNATED"
    )
    assert result.port_roles[("S3", "Gi0/2")] == "ALTERNATE", (
        f"Expected S3:Gi0/2 ALTERNATE but got {result.port_roles.get(('S3', 'Gi0/2'))!r}; "
        "on the S2-S3 segment, S3 has higher root path cost so its non-root port becomes ALTERNATE (blocked)"
    )


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

    assert ("S3", "Gi0/1") in changes, (
        f"Expected S3:Gi0/1 in role_changes after removing S1-S3 link but got {changes}; "
        "that port's role changed because S3 must now route through S2 to reach the root"
    )
    assert after.root_port_by_node["S3"] == "Gi0/2", (
        f"Expected S3 root port to be Gi0/2 after S1-S3 link removal but got {after.root_port_by_node.get('S3')!r}; "
        "with S1-S3 direct link gone, S3 must use Gi0/2 (to S2) as its root port"
    )

    guard = bpdu_guard_decision(port=("S2", "Gi0/10"), edge_port=True, bpdu_received=True)
    assert guard.action == "ERRDISABLE", (
        f"Expected ERRDISABLE but got {guard.action!r}; "
        "BPDU guard err-disables an edge (portfast) port that receives a BPDU, preventing rogue switches"
    )
