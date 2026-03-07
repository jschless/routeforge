"""Deterministic STP core model for foundational loop-prevention labs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class BridgeID:
    priority: int
    mac: str


@dataclass(frozen=True)
class PortRef:
    node_id: str
    port_id: str

    def key(self) -> tuple[str, str]:
        return (self.node_id, self.port_id)


@dataclass(frozen=True)
class Link:
    a: PortRef
    b: PortRef
    cost: int = 4


@dataclass(frozen=True)
class Bridge:
    node_id: str
    bridge_id: BridgeID


@dataclass(frozen=True)
class STPResult:
    root_node_id: str
    root_path_cost: dict[str, int]
    root_port_by_node: dict[str, str]
    port_roles: dict[tuple[str, str], str]


@dataclass(frozen=True)
class GuardDecision:
    port: tuple[str, str]
    action: str
    reason: str


def _neighbor(endpoint: PortRef, link: Link) -> PortRef:
    if endpoint == link.a:
        return link.b
    if endpoint == link.b:
        return link.a
    raise ValueError("endpoint not in link")


def compute_stp(bridges: list[Bridge], links: list[Link]) -> STPResult:
    if not bridges:
        raise ValueError("bridges must not be empty")

    bridge_by_node = {bridge.node_id: bridge for bridge in bridges}
    links_by_node: dict[str, list[Link]] = {bridge.node_id: [] for bridge in bridges}
    for link in links:
        links_by_node.setdefault(link.a.node_id, []).append(link)
        links_by_node.setdefault(link.b.node_id, []).append(link)

    root = min(bridges, key=lambda bridge: bridge.bridge_id)
    root_node = root.node_id

    root_cost: dict[str, int] = {root_node: 0}
    root_port: dict[str, str] = {}

    # Relax path choices until stable; tie-break with neighbor bridge-id and port-id.
    for _ in range(len(bridges) * 4):
        changed = False
        for bridge in bridges:
            node = bridge.node_id
            if node == root_node:
                continue
            best: tuple[int, BridgeID, str, str] | None = None
            for link in links_by_node.get(node, []):
                if link.a.node_id == node:
                    local = link.a
                else:
                    local = link.b
                remote = _neighbor(local, link)
                remote_cost = root_cost.get(remote.node_id)
                if remote_cost is None:
                    continue
                remote_bridge_id = bridge_by_node[remote.node_id].bridge_id
                candidate = (remote_cost + link.cost, remote_bridge_id, remote.port_id, local.port_id)
                if best is None or candidate < best:
                    best = candidate
            if best is None:
                continue
            candidate_cost, _, _, candidate_port = best
            if root_cost.get(node) != candidate_cost or root_port.get(node) != candidate_port:
                root_cost[node] = candidate_cost
                root_port[node] = candidate_port
                changed = True
        if not changed:
            break

    roles: dict[tuple[str, str], str] = {}

    for node, port in root_port.items():
        roles[(node, port)] = "ROOT"

    for link in links:
        a, b = link.a, link.b
        a_vector = (
            root_cost.get(a.node_id, 10**9),
            bridge_by_node[a.node_id].bridge_id,
            a.port_id,
        )
        b_vector = (
            root_cost.get(b.node_id, 10**9),
            bridge_by_node[b.node_id].bridge_id,
            b.port_id,
        )
        if a_vector <= b_vector:
            designated = a
            other = b
        else:
            designated = b
            other = a

        designated_key = designated.key()
        if roles.get(designated_key) != "ROOT":
            roles[designated_key] = "DESIGNATED"

        other_key = other.key()
        if roles.get(other_key) is None:
            roles[other_key] = "ALTERNATE"

    for bridge in bridges:
        for link in links_by_node.get(bridge.node_id, []):
            local = link.a if link.a.node_id == bridge.node_id else link.b
            roles.setdefault(local.key(), "ALTERNATE")

    return STPResult(
        root_node_id=root_node,
        root_path_cost=root_cost,
        root_port_by_node=root_port,
        port_roles=roles,
    )


def remove_link(links: list[Link], *, a: tuple[str, str], b: tuple[str, str]) -> list[Link]:
    filtered: list[Link] = []
    for link in links:
        endpoints = {(link.a.node_id, link.a.port_id), (link.b.node_id, link.b.port_id)}
        if endpoints == {a, b}:
            continue
        filtered.append(link)
    return filtered


def role_changes(previous: STPResult, current: STPResult) -> dict[tuple[str, str], tuple[str, str]]:
    keys = set(previous.port_roles) | set(current.port_roles)
    changes: dict[tuple[str, str], tuple[str, str]] = {}
    for key in keys:
        old = previous.port_roles.get(key, "DOWN")
        new = current.port_roles.get(key, "DOWN")
        if old != new:
            changes[key] = (old, new)
    return changes


def bpdu_guard_decision(*, port: tuple[str, str], edge_port: bool, bpdu_received: bool) -> GuardDecision:
    if edge_port and bpdu_received:
        return GuardDecision(
            port=port,
            action="ERRDISABLE",
            reason="STP_BPDU_GUARD_TRIPPED",
        )
    return GuardDecision(
        port=port,
        action="FORWARD",
        reason="STP_GUARD_CLEAR",
    )
