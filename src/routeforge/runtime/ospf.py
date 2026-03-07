"""Deterministic OSPF helpers for labs 11-15."""

from __future__ import annotations

from dataclasses import dataclass, field
from ipaddress import IPv4Network
import heapq


def neighbor_hello_transition(
    *,
    current_state: str,
    hello_received: bool,
    dead_timer_expired: bool,
) -> str:
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


def run_spf(graph: dict[str, list[tuple[str, int]]], *, root_router_id: str) -> SpfResult:
    costs: dict[str, int] = {root_router_id: 0}
    parent: dict[str, str | None] = {root_router_id: None}
    pq: list[tuple[int, str]] = [(0, root_router_id)]
    visited: set[str] = set()

    while pq:
        current_cost, node = heapq.heappop(pq)
        if node in visited:
            continue
        visited.add(node)
        for neighbor, edge_cost in sorted(graph.get(node, []), key=lambda entry: entry[0]):
            candidate_cost = current_cost + edge_cost
            known = costs.get(neighbor)
            if known is None or candidate_cost < known:
                costs[neighbor] = candidate_cost
                parent[neighbor] = node
                heapq.heappush(pq, (candidate_cost, neighbor))
            elif candidate_cost == known and node < (parent.get(neighbor) or "~"):
                parent[neighbor] = node

    return SpfResult(root_router_id=root_router_id, cost_by_router=costs, parent_by_router=parent)


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
