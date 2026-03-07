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
    # TODO(student): compute deterministic STP root, root ports, and roles.
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
    # TODO(student): implement BPDU guard enforcement on edge ports.
    raise NotImplementedError("TODO: implement bpdu_guard_decision")
