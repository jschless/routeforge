"""Deterministic BGP helpers for labs 21-24."""

from __future__ import annotations

from dataclasses import dataclass


def bgp_session_transition(*, current_state: str, event: str) -> str:
    # TODO(student): implement deterministic BGP FSM transitions.
    raise NotImplementedError("TODO: implement bgp_session_transition")


@dataclass(frozen=True)
class BgpPath:
    prefix: str
    prefix_len: int
    next_hop: str
    neighbor_id: str
    local_pref: int
    as_path: tuple[int, ...]
    med: int
    origin: str


def _origin_rank(origin: str) -> int:
    return {"igp": 0, "egp": 1, "incomplete": 2}.get(origin.lower(), 3)


def select_best_path(paths: list[BgpPath]) -> BgpPath:
    # TODO(student): choose best path with stable BGP tie-break ordering.
    raise NotImplementedError("TODO: implement select_best_path")


def apply_export_policy(*, paths: list[BgpPath], denied_prefixes: set[str], local_pref_override: int | None = None) -> list[BgpPath]:
    # TODO(student): filter denied prefixes and apply optional local-pref override.
    raise NotImplementedError("TODO: implement apply_export_policy")


def route_reflect(*, learned: dict[str, list[str]], source_client: str) -> dict[str, list[str]]:
    # TODO(student): reflect source client routes to all other clients.
    raise NotImplementedError("TODO: implement route_reflect")


def convergence_mark(*, before: dict[str, str], after: dict[str, str]) -> bool:
    return before == after
