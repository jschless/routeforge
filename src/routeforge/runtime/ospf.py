"""Deterministic OSPF helpers for labs 11-15."""

from __future__ import annotations

from dataclasses import dataclass, field


def neighbor_hello_transition(
    *,
    current_state: str,
    hello_received: bool,
    dead_timer_expired: bool,
) -> str:
    """Return the next OSPF neighbor state given current state and inputs.

    Simplified two-state model used in this lab (DOWN / FULL):

    - ``dead_timer_expired=True`` → always transition to ``"DOWN"``,
      regardless of current state or hello.
    - ``hello_received=True`` and ``dead_timer_expired=False`` → transition to
      ``"FULL"`` (neighbor is reachable and exchanging hellos).
    - Both False → stay in ``current_state``.

    Valid states: ``"DOWN"``, ``"FULL"``.

    See ``docs/tutorial/lab11_ospf_adjacency_fsm.md`` for the full FSM walkthrough.

    # TODO(student): implement neighbor_hello_transition using the rules above.
    """
    raise NotImplementedError("TODO: implement neighbor_hello_transition")


def neighbor_state_changed(previous: str, current: str) -> bool:
    return previous != current


@dataclass(frozen=True)
class DrCandidate:
    router_id: str
    priority: int


def _election_order(candidates: list[DrCandidate]) -> list[DrCandidate]:
    # TODO(student): order candidates by priority and router ID for deterministic DR/BDR election.
    raise NotImplementedError("TODO: implement _election_order")


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

    # TODO(student): implement failover_dr_bdr.
    """
    raise NotImplementedError("TODO: implement failover_dr_bdr")


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
        """Advance LSA age by ``seconds``, remove max-age records, return expired keys.

        For each record in ``self.records``:
        1. Increment ``record.age`` by ``seconds``.
        2. If the new age >= ``self.max_age``, remove the record from
           ``self.records`` and add its key ``(lsa_id, advertising_router)``
           to the returned list.

        Return the list of expired ``(lsa_id, advertising_router)`` keys.

        # TODO(student): implement Lsdb.age_tick.
        """
        raise NotImplementedError("TODO: implement Lsdb.age_tick")


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

    # TODO(student): implement _dijkstra_init.
    """
    raise NotImplementedError("TODO: implement _dijkstra_init")


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

    # TODO(student): implement _dijkstra_relax.
    """
    raise NotImplementedError("TODO: implement _dijkstra_relax")


def run_spf(graph: dict[str, list[tuple[str, int]]], *, root_router_id: str) -> SpfResult:
    """Run Dijkstra's SPF from ``root_router_id`` over ``graph``.

    This function is pre-filled as a scaffold — implement ``_dijkstra_init``
    and ``_dijkstra_relax`` above, and this will produce the correct
    ``SpfResult``.

    ``graph`` maps each router_id to a list of ``(neighbor_router_id, link_cost)``
    adjacencies.  The heap tuple is ``(cost, router_id)`` so Python's
    ``heapq`` breaks cost ties by router_id string (lexicographically smaller
    wins), satisfying the determinism requirement.

    See ``docs/tutorial/lab14_ospf_spf_and_route_install.md`` for the walkthrough.
    """
    import heapq

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
    """Summarize non-backbone area routes into /16 inter-area summary routes.

    This simulates an ABR (Area Border Router) aggregating intra-area routes
    to advertise compact summaries into the backbone (area 0).

    Algorithm:
    1. Filter out backbone routes: only process routes where ``area_id != 0``.
    2. Group filtered routes by ``area_id``.
    3. For each group, produce one ``AreaRoute`` summary per unique area:
       - ``area_id``: the source area id (unchanged)
       - ``prefix``: the first two octets of the most-specific route in the
         group followed by ``.0.0`` (e.g., ``"10.1.0.0"`` summarizes to
         ``"10.1.0.0"``)
       - ``prefix_len``: 16 (always /16 summaries)
       - ``cost``: the maximum cost among routes in the group (worst-case)
    4. Return summaries sorted deterministically by ``(area_id, prefix)``.

    See ``docs/tutorial/lab15_ospf_multi_area_abr.md`` for the walkthrough.

    # TODO(student): implement originate_summaries following the algorithm above.
    """
    raise NotImplementedError("TODO: implement originate_summaries")
