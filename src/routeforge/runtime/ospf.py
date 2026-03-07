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


def run_spf(graph: dict[str, list[tuple[str, int]]], *, root_router_id: str) -> SpfResult:
    """Run Dijkstra's SPF from ``root_router_id`` over ``graph``.

    ``graph`` maps each router_id to a list of ``(neighbor_router_id, link_cost)``
    tuples representing adjacencies.

    Algorithm:
    1. Initialize: cost[root] = 0, cost[all others] = infinity.
       Set parent[root] = None.
    2. Use a min-heap of ``(cost, router_id)`` to process nodes in cost order.
    3. For each node popped from the heap, relax its neighbors:
       if cost[node] + link_cost < cost[neighbor], update cost[neighbor] and
       set parent[neighbor] = node, then push (new_cost, neighbor) to the heap.
    4. For determinism, when two paths have equal cost, prefer the neighbor
       with the **lexicographically smaller** router_id (i.e., compare IDs as
       strings when costs are equal).
    5. Continue until the heap is empty.

    Return a ``SpfResult`` with:
    - ``root_router_id``: the starting router (unchanged from input)
    - ``cost_by_router``: ``{router_id: minimum_cost}`` for all reachable routers
    - ``parent_by_router``: ``{router_id: parent_router_id | None}``
      (root's parent is None; unreachable nodes are omitted)

    See ``docs/tutorial/lab14_ospf_spf_and_route_install.md`` for the walkthrough.

    # TODO(student): implement run_spf using Dijkstra's algorithm above.
    """
    raise NotImplementedError("TODO: implement run_spf")


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
