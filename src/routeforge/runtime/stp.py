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
    """Compute deterministic STP root, root path costs, and port roles.

    Algorithm (IEEE 802.1D simplified):

    1. **Elect root bridge** — the bridge with the lowest ``BridgeID``
       (compare ``(priority, mac)`` lexicographically; lower wins).

    2. **Compute root path costs** — BFS/Dijkstra from the root across all
       links.  Each link has a ``cost`` field; accumulate costs to find the
       minimum-cost path from every bridge to the root.

    3. **Assign root ports** — for every non-root bridge, the port on the
       lowest-cost path toward the root is the *root port*.  Tiebreak on
       port_id lexicographically (lower port_id wins).

    4. **Assign designated ports** — for each link segment, one port is
       *designated* (the end closer to the root, i.e., lower root path cost
       from that bridge's side).  Tiebreak: lower ``bridge_id``, then lower
       ``port_id``.

    5. **Block remaining ports** — any port not elected as root or designated
       becomes *alternate* (blocked).

    Return a ``STPResult`` with:
    - ``root_node_id``: node_id of the elected root bridge
    - ``root_path_cost``: mapping ``node_id -> cost`` to reach root (root=0)
    - ``root_port_by_node``: mapping ``node_id -> port_id`` for non-root bridges
    - ``port_roles``: mapping ``(node_id, port_id) -> role`` where role is one
      of ``"ROOT"``, ``"DESIGNATED"``, or ``"ALTERNATE"``

    See ``docs/tutorial/lab04_stp.md`` for the concept walkthrough.

    # TODO(student): implement compute_stp following the algorithm above.
    """
    raise NotImplementedError("TODO: implement compute_stp")


def remove_link(links: list[Link], *, a: tuple[str, str], b: tuple[str, str]) -> list[Link]:
    filtered: list[Link] = []
    for link in links:
        endpoints = {(link.a.node_id, link.a.port_id), (link.b.node_id, link.b.port_id)}
        if endpoints == {a, b}:
            continue
        filtered.append(link)
    return filtered


def role_changes(previous: STPResult, current: STPResult) -> dict[tuple[str, str], tuple[str, str]]:
    # TODO(student): return all deterministic port-role transitions, defaulting missing ports to DOWN.
    raise NotImplementedError("TODO: implement role_changes")


def bpdu_guard_decision(*, port: tuple[str, str], edge_port: bool, bpdu_received: bool) -> GuardDecision:
    """Decide whether to err-disable a port that received a BPDU.

    Rules:
    - If ``edge_port`` is True and ``bpdu_received`` is True:
      return ``GuardDecision(port=port, action="ERR_DISABLE", reason="BPDU_GUARD_VIOLATION")``.
    - Otherwise (non-edge port, or no BPDU received):
      return ``GuardDecision(port=port, action="ALLOW", reason="OK")``.

    Edge ports are ports connected to end-hosts; receiving a BPDU on one
    indicates a rogue switch is attached, so the port is shut down.

    # TODO(student): implement bpdu_guard_decision.
    """
    raise NotImplementedError("TODO: implement bpdu_guard_decision")
