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


def _elect_root_bridge(bridges: list[Bridge]) -> Bridge:
    """Return the bridge with the lowest BridgeID.

    ``BridgeID`` is a dataclass with ``order=True``, so Python compares
    ``(priority, mac)`` field by field — lower priority wins; on a tie,
    lower MAC string wins (lexicographic).

    Example: ``BridgeID(priority=4096, mac="ff:ff:ff:ff:ff:ff")`` beats
    ``BridgeID(priority=32768, mac="00:00:00:00:00:01")`` because 4096 < 32768.

    Use ``min(bridges, key=...)`` — ``Bridge.bridge_id`` is the sort key.

    See ``docs/tutorial/lab04_stp.md`` for the concept walkthrough.
    """
    return min(bridges, key=lambda bridge: bridge.bridge_id)


def _compute_root_path_costs(
    root: Bridge, bridges: list[Bridge], links: list[Link]
) -> dict[str, int]:
    """BFS/Dijkstra from root to compute minimum cost from every bridge to root.

    Algorithm:
    1. Initialize: ``cost = {root.node_id: 0}``; all others not present (treat
       as infinity).
    2. Use a min-heap of ``(cost, node_id)``; start with ``(0, root.node_id)``.
    3. Pop the cheapest entry.  For each link touching that node, check the
       neighbor's known cost.  If ``cost[current] + link.cost`` is lower, update
       and push ``(new_cost, neighbor_node_id)``.
    4. Use ``_neighbor(endpoint, link)`` to find the other end of a link.
       To find links for a node, iterate ``links`` and check ``link.a.node_id``
       and ``link.b.node_id``.

    Return ``{node_id: minimum_cost_to_root}`` for all reachable bridges.

    See ``docs/tutorial/lab04_stp.md`` for the concept walkthrough.
    """
    links_by_node: dict[str, list[Link]] = {bridge.node_id: [] for bridge in bridges}
    for link in links:
        links_by_node.setdefault(link.a.node_id, []).append(link)
        links_by_node.setdefault(link.b.node_id, []).append(link)

    root_cost: dict[str, int] = {root.node_id: 0}

    # Relax path choices until stable; tie-break with neighbor bridge-id and port-id.
    for _ in range(len(bridges) * 4):
        changed = False
        for bridge in bridges:
            node = bridge.node_id
            if node == root.node_id:
                continue
            best_cost: int | None = None
            for link in links_by_node.get(node, []):
                if link.a.node_id == node:
                    local = link.a
                else:
                    local = link.b
                remote = _neighbor(local, link)
                remote_cost = root_cost.get(remote.node_id)
                if remote_cost is None:
                    continue
                candidate_cost = remote_cost + link.cost
                if best_cost is None or candidate_cost < best_cost:
                    best_cost = candidate_cost
            if best_cost is None:
                continue
            if root_cost.get(node) != best_cost:
                root_cost[node] = best_cost
                changed = True
        if not changed:
            break

    return root_cost


def _compute_root_ports(
    root: Bridge,
    bridges: list[Bridge],
    links: list[Link],
    root_path_cost: dict[str, int],
) -> dict[str, str]:
    """Determine the root port for every non-root bridge.

    The root port is the port on the lowest-cost path toward the root.
    Tiebreak: lower ``port_id`` string (lexicographic) wins.

    Algorithm:
    - For each non-root bridge, iterate its links.
    - For each link, compute candidate path cost:
      ``root_path_cost[neighbor_node_id] + link.cost``.
    - The port (``a`` or ``b`` side) on the local bridge side of the best link
      is the root port.
    - Ignore links to unreachable neighbors (not in ``root_path_cost``).

    Return ``{node_id: port_id}`` for non-root bridges only.

    See ``docs/tutorial/lab04_stp.md`` for the concept walkthrough.
    """
    links_by_node: dict[str, list[Link]] = {bridge.node_id: [] for bridge in bridges}
    for link in links:
        links_by_node.setdefault(link.a.node_id, []).append(link)
        links_by_node.setdefault(link.b.node_id, []).append(link)

    bridge_by_node = {bridge.node_id: bridge for bridge in bridges}
    root_port: dict[str, str] = {}

    for bridge in bridges:
        node = bridge.node_id
        if node == root.node_id:
            continue
        best: tuple[int, BridgeID, str, str] | None = None
        for link in links_by_node.get(node, []):
            if link.a.node_id == node:
                local = link.a
            else:
                local = link.b
            remote = _neighbor(local, link)
            remote_cost = root_path_cost.get(remote.node_id)
            if remote_cost is None:
                continue
            remote_bridge_id = bridge_by_node[remote.node_id].bridge_id
            candidate = (remote_cost + link.cost, remote_bridge_id, remote.port_id, local.port_id)
            if best is None or candidate < best:
                best = candidate
        if best is not None:
            _, _, _, candidate_port = best
            root_port[node] = candidate_port

    return root_port


def _assign_port_roles(
    root: Bridge,
    bridges: list[Bridge],
    links: list[Link],
    root_path_cost: dict[str, int],
    root_port_by_node: dict[str, str],
) -> dict[tuple[str, str], str]:
    """Assign DESIGNATED, ROOT, or ALTERNATE role to every port.

    Rules (apply in order):

    1. Root bridge ports are always ``"DESIGNATED"``.
    2. For every non-root bridge, the root port (from ``root_port_by_node``) is
       ``"ROOT"``.
    3. For each link segment, the designated port is on the bridge with the
       **lower** root path cost.  Tiebreak: lower ``bridge_id`` (compare
       ``Bridge.bridge_id``), then lower ``port_id`` string.
       The designated port gets role ``"DESIGNATED"``; the other is
       ``"ALTERNATE"``.

    Use ``_neighbor(endpoint, link)`` to find the far end of a link.
    Look up the bridge object by ``node_id`` to access its ``bridge_id``.

    Return ``{(node_id, port_id): role}`` covering all ports of all bridges.

    See ``docs/tutorial/lab04_stp.md`` for the concept walkthrough.
    """
    bridge_by_node = {bridge.node_id: bridge for bridge in bridges}
    links_by_node: dict[str, list[Link]] = {bridge.node_id: [] for bridge in bridges}
    for link in links:
        links_by_node.setdefault(link.a.node_id, []).append(link)
        links_by_node.setdefault(link.b.node_id, []).append(link)

    roles: dict[tuple[str, str], str] = {}

    for node, port in root_port_by_node.items():
        roles[(node, port)] = "ROOT"

    for link in links:
        a, b = link.a, link.b
        a_vector = (
            root_path_cost.get(a.node_id, 10**9),
            bridge_by_node[a.node_id].bridge_id,
            a.port_id,
        )
        b_vector = (
            root_path_cost.get(b.node_id, 10**9),
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

    return roles


def compute_stp(bridges: list[Bridge], links: list[Link]) -> STPResult:
    """Compute deterministic STP root, root path costs, and port roles.

    This function is pre-filled as a scaffold — implement the four helper
    functions above and this will produce the correct ``STPResult``.

    The algorithm (IEEE 802.1D simplified) is broken into steps:
    1. ``_elect_root_bridge`` — lowest BridgeID wins.
    2. ``_compute_root_path_costs`` — Dijkstra from root.
    3. ``_compute_root_ports`` — best port toward root per non-root bridge.
    4. ``_assign_port_roles`` — DESIGNATED / ROOT / ALTERNATE per port.

    See ``docs/tutorial/lab04_stp.md`` for the full concept walkthrough.
    """
    if not bridges:
        raise ValueError("bridges must not be empty")
    root = _elect_root_bridge(bridges)
    root_path_cost = _compute_root_path_costs(root, bridges, links)
    root_port_by_node = _compute_root_ports(root, bridges, links, root_path_cost)
    port_roles = _assign_port_roles(root, bridges, links, root_path_cost, root_port_by_node)
    return STPResult(
        root_node_id=root.node_id,
        root_path_cost=root_path_cost,
        root_port_by_node=root_port_by_node,
        port_roles=port_roles,
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
    """Return all deterministic port-role transitions between two STP computations.

    Compare ``previous.port_roles`` and ``current.port_roles``.  For every
    port key that appears in either dict, if the role changed, include it in
    the result.  Ports that appear in one dict but not the other are treated as
    having role ``"DOWN"`` in the missing dict.

    Return ``{(node_id, port_id): (old_role, new_role)}`` for every port whose
    role changed.
    """
    keys = set(previous.port_roles) | set(current.port_roles)
    changes: dict[tuple[str, str], tuple[str, str]] = {}
    for key in keys:
        old = previous.port_roles.get(key, "DOWN")
        new = current.port_roles.get(key, "DOWN")
        if old != new:
            changes[key] = (old, new)
    return changes


def bpdu_guard_decision(*, port: tuple[str, str], edge_port: bool, bpdu_received: bool) -> GuardDecision:
    """Decide whether to err-disable a port that received a BPDU.

    Rules:
    - If ``edge_port`` is True and ``bpdu_received`` is True:
      return ``GuardDecision(port=port, action="ERRDISABLE", reason="STP_BPDU_GUARD_TRIPPED")``.
    - Otherwise (non-edge port, or no BPDU received):
      return ``GuardDecision(port=port, action="FORWARD", reason="STP_GUARD_CLEAR")``.

    Edge ports are ports connected to end-hosts; receiving a BPDU on one
    indicates a rogue switch is attached, so the port is shut down.
    """
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
