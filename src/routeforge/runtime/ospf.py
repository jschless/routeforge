"""Deterministic OSPF helpers for labs 11-15."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from ipaddress import IPv4Network


def neighbor_hello_transition(
    *,
    current_state: str,
    hello_received: bool,
    dead_timer_expired: bool,
) -> str:
    """Return the next OSPF neighbor state given current state and inputs.

    Full FSM used in this implementation (DOWN / INIT / 2WAY / FULL):

    - ``dead_timer_expired=True`` → always transition to ``"DOWN"``,
      regardless of current state or hello.
    - ``hello_received=True`` and ``dead_timer_expired=False`` → transition
      progresses: DOWN→INIT, INIT→2WAY, 2WAY→FULL; FULL stays FULL.
    - Both False → stay in ``current_state``.

    Valid states: ``"DOWN"``, ``"INIT"``, ``"2WAY"``, ``"FULL"``.

    Note: the simplified student model uses only DOWN/FULL; this implementation
    uses the full four-state progression.

    See ``docs/tutorial/lab11_ospf_adjacency_fsm.md`` for the full FSM walkthrough.
    """
    if dead_timer_expired:
        return "DOWN"
    if not hello_received:
        return current_state
    if current_state == "DOWN":
        return "INIT"
    if current_state == "INIT":
        return "2WAY"
    if current_state == "2WAY":
        return "FULL"
    return current_state


def neighbor_state_changed(previous: str, current: str) -> bool:
    return previous != current


@dataclass(frozen=True)
class DrCandidate:
    router_id: str
    priority: int


def _election_order(candidates: list[DrCandidate]) -> list[DrCandidate]:
    return sorted(candidates, key=lambda candidate: (candidate.priority, candidate.router_id), reverse=True)


def elect_dr_bdr(candidates: list[DrCandidate]) -> tuple[str, str | None]:
    ordered = _election_order(candidates)
    if not ordered:
        raise ValueError("at least one candidate is required")
    dr = ordered[0].router_id
    bdr = ordered[1].router_id if len(ordered) > 1 else None
    return dr, bdr


def failover_dr_bdr(candidates: list[DrCandidate], *, active_router_ids: set[str]) -> tuple[str, str | None]:
    """Re-elect DR/BDR from candidates that are currently active.

    Filter ``candidates`` to only those whose ``router_id`` is in
    ``active_router_ids``, then call ``elect_dr_bdr`` on the filtered list.

    Raises ``ValueError`` if no candidates remain after filtering.
    """
    active = [candidate for candidate in candidates if candidate.router_id in active_router_ids]
    return elect_dr_bdr(active)


@dataclass(frozen=True)
class LsaRecord:
    lsa_id: str
    advertising_router: str
    sequence: int
    age: int
    payload: dict[str, object]

    @property
    def key(self) -> tuple[str, str]:
        return (self.lsa_id, self.advertising_router)


@dataclass
class Lsdb:
    max_age: int = 3600
    records: dict[tuple[str, str], LsaRecord] = field(default_factory=dict)

    def install(self, record: LsaRecord) -> LsaRecord:
        self.records[record.key] = record
        return record

    def refresh(self, key: tuple[str, str]) -> LsaRecord:
        current = self.records[key]
        refreshed = LsaRecord(
            lsa_id=current.lsa_id,
            advertising_router=current.advertising_router,
            sequence=current.sequence + 1,
            age=0,
            payload=current.payload,
        )
        self.records[key] = refreshed
        return refreshed

    def age_tick(self, seconds: int = 1) -> list[tuple[str, str]]:
        expired: list[tuple[str, str]] = []
        updated: dict[tuple[str, str], LsaRecord] = {}
        for key, record in self.records.items():
            aged = LsaRecord(
                lsa_id=record.lsa_id,
                advertising_router=record.advertising_router,
                sequence=record.sequence,
                age=record.age + seconds,
                payload=record.payload,
            )
            if aged.age >= self.max_age:
                expired.append(key)
            else:
                updated[key] = aged
        self.records = updated
        return sorted(expired)


@dataclass(frozen=True)
class SpfResult:
    root_router_id: str
    cost_by_router: dict[str, int]
    parent_by_router: dict[str, str | None]


def _dijkstra_init(
    graph: dict[str, list[tuple[str, int]]],
    *,
    root_router_id: str,
) -> tuple[dict[str, int], dict[str, str | None]]:
    """Initialize Dijkstra cost and parent tables for SPF.

    Sets up the two data structures needed before the main heap loop:

    - ``cost_by_router``: maps every router_id in ``graph`` to its current
      best-known cost.  Root starts at ``0``; all others start at
      ``float("inf")`` (unknown/unreachable).
    - ``parent_by_router``: maps ``root_router_id`` to ``None`` (it has no
      parent).  Other routers are not yet added — they are inserted when
      relaxed in the heap loop.

    Return ``(cost_by_router, parent_by_router)``.

    See ``docs/tutorial/lab14_ospf_spf_and_route_install.md`` for the walkthrough.
    """
    cost_by_router: dict[str, int] = {root_router_id: 0}
    parent_by_router: dict[str, str | None] = {root_router_id: None}
    return cost_by_router, parent_by_router


def _dijkstra_relax(
    current: str,
    neighbors: list[tuple[str, int]],
    *,
    cost_by_router: dict[str, int],
    parent_by_router: dict[str, str | None],
) -> list[tuple[int, str]]:
    """Relax all edges from ``current`` and return new heap entries.

    For each ``(neighbor, link_cost)`` in ``neighbors``:
    - Compute ``candidate = cost_by_router[current] + link_cost``.
    - If ``candidate < cost_by_router.get(neighbor, float("inf"))``:
      - Update ``cost_by_router[neighbor] = candidate``.
      - Set ``parent_by_router[neighbor] = current``.
      - Append ``(candidate, neighbor)`` to the returned list.
    - Equal-cost paths: do **not** update (strict ``<`` only); the first path
      found via the heap wins.  For determinism, the heap naturally processes
      cheaper costs first; tie-break on ``router_id`` string is handled by the
      heap tuple ordering ``(cost, router_id)``.

    Return a list of ``(cost, router_id)`` tuples to push onto the heap.
    Modifies ``cost_by_router`` and ``parent_by_router`` in place.

    See ``docs/tutorial/lab14_ospf_spf_and_route_install.md`` for the walkthrough.
    """
    new_entries: list[tuple[int, str]] = []
    current_cost = cost_by_router[current]
    for neighbor, edge_cost in neighbors:
        candidate = current_cost + edge_cost
        known = cost_by_router.get(neighbor, float("inf"))  # type: ignore[arg-type]
        if candidate < known:
            cost_by_router[neighbor] = candidate
            parent_by_router[neighbor] = current
            new_entries.append((candidate, neighbor))
    return new_entries


def run_spf(graph: dict[str, list[tuple[str, int]]], *, root_router_id: str) -> SpfResult:
    """Run Dijkstra's SPF from ``root_router_id`` over ``graph``.

    This function is pre-filled as a scaffold — implement ``_dijkstra_init``
    and ``_dijkstra_relax`` above, and this will produce the correct
    ``SpfResult``.

    The split into init + relax is deliberate: correctness lives in relax.
    ``_dijkstra_init`` sets deterministic starting state (root cost 0, parent
    map shape), while ``_dijkstra_relax`` is where candidate costs, parent
    updates, and strict tie behavior are enforced. If relax is wrong, SPF can
    appear to work on small graphs but fail on tie-break or alternate-path
    scenarios.

    ``graph`` maps each router_id to a list of ``(neighbor_router_id, link_cost)``
    adjacencies.  The heap tuple is ``(cost, router_id)`` so Python's
    ``heapq`` breaks cost ties by router_id string (lexicographically smaller
    wins), satisfying the determinism requirement.

    See ``docs/tutorial/lab14_ospf_spf_and_route_install.md`` for the walkthrough.
    """
    cost_by_router, parent_by_router = _dijkstra_init(graph, root_router_id=root_router_id)
    heap: list[tuple[int, str]] = [(0, root_router_id)]
    visited: set[str] = set()

    while heap:
        _cost, router_id = heapq.heappop(heap)
        if router_id in visited:
            continue
        visited.add(router_id)
        neighbors = graph.get(router_id, [])
        new_entries = _dijkstra_relax(
            router_id, neighbors,
            cost_by_router=cost_by_router,
            parent_by_router=parent_by_router,
        )
        for entry in new_entries:
            heapq.heappush(heap, entry)

    reachable_costs = {k: v for k, v in cost_by_router.items() if v < float("inf")}
    return SpfResult(
        root_router_id=root_router_id,
        cost_by_router=reachable_costs,
        parent_by_router=parent_by_router,
    )


def next_hop_for_destination(spf: SpfResult, *, destination_router_id: str) -> str | None:
    if destination_router_id not in spf.parent_by_router:
        return None
    node = destination_router_id
    parent = spf.parent_by_router[node]
    if parent is None:
        return None
    while parent is not None and parent != spf.root_router_id:
        node = parent
        parent = spf.parent_by_router.get(node)
    return node


@dataclass(frozen=True)
class AreaRoute:
    area_id: int
    prefix: str
    prefix_len: int
    cost: int


def originate_summaries(routes: list[AreaRoute]) -> list[AreaRoute]:
    # Deterministic summary origin: one /16 per source /16 block per non-backbone area.
    summary_map: dict[tuple[int, str], int] = {}
    for route in routes:
        if route.area_id == 0:
            continue
        network = IPv4Network(f"{route.prefix}/{route.prefix_len}", strict=False)
        summary = network.supernet(new_prefix=16) if network.prefixlen > 16 else network
        key = (route.area_id, str(summary.network_address))
        best_cost = summary_map.get(key)
        if best_cost is None or route.cost < best_cost:
            summary_map[key] = route.cost

    summaries = [
        AreaRoute(area_id=area_id, prefix=prefix, prefix_len=16, cost=cost)
        for (area_id, prefix), cost in sorted(summary_map.items(), key=lambda item: (item[0][0], item[0][1]))
    ]
    return summaries
