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
    # TODO(student): implement OSPF neighbor hello-state transitions.
    raise NotImplementedError("TODO: implement neighbor_hello_transition")


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
    # TODO(student): re-elect DR/BDR from active routers only.
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
        # TODO(student): age LSAs, remove max-age records, return expired keys.
        raise NotImplementedError("TODO: implement Lsdb.age_tick")


@dataclass(frozen=True)
class SpfResult:
    root_router_id: str
    cost_by_router: dict[str, int]
    parent_by_router: dict[str, str | None]


def run_spf(graph: dict[str, list[tuple[str, int]]], *, root_router_id: str) -> SpfResult:
    # TODO(student): run deterministic SPF and return costs/parents.
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
    # TODO(student): summarize non-backbone area routes into deterministic inter-area summaries.
    raise NotImplementedError("TODO: implement originate_summaries")
