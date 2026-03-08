"""Deterministic BGP helpers for labs 21-24."""

from __future__ import annotations

from dataclasses import dataclass


def bgp_session_transition(*, current_state: str, event: str) -> str:
    """Return the next BGP session state given ``current_state`` and ``event``.

    Simplified FSM used in this implementation (subset of RFC 4271 §8).
    Events are compared case-insensitively (uppercased before matching).

    Transitions:
    - IDLE + TCP_CONNECTED → CONNECT
    - CONNECT + OPEN_RX → OPENSENT
    - OPENSENT + KEEPALIVE_RX → ESTABLISHED
    - Any state + NOTIFICATION_RX or HOLD_TIMER_EXPIRE → IDLE
    - Any other event → stay in current_state

    Note: the student FSM table uses different event/state names (START,
    TCP_OPEN, OPEN_RECEIVED, etc.); this implementation uses the event names
    that appear in the contract tests (TCP_CONNECTED, OPEN_RX, KEEPALIVE_RX,
    HOLD_TIMER_EXPIRE).

    See ``docs/tutorial/lab21_bgp_session_fsm_and_transport.md`` for the walkthrough.
    """
    event = event.upper()
    if current_state == "IDLE" and event == "TCP_CONNECTED":
        return "CONNECT"
    if current_state == "CONNECT" and event == "OPEN_RX":
        return "OPENSENT"
    if current_state == "OPENSENT" and event == "KEEPALIVE_RX":
        return "ESTABLISHED"
    if event in {"NOTIFICATION_RX", "HOLD_TIMER_EXPIRE"}:
        return "IDLE"
    return current_state


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
    """Choose the best BGP path using a stable, deterministic tie-break chain.

    Raises ``ValueError`` if ``paths`` is empty.

    Decision process (highest priority first):

    1. **Highest local_pref** — larger ``local_pref`` wins.
    2. **Shortest AS path** — smaller ``len(as_path)`` wins.
    3. **Lowest origin** — ``igp`` (0) < ``egp`` (1) < ``incomplete`` (2).
       Use ``_origin_rank()`` which is already defined above.
    4. **Lowest MED** — smaller ``med`` wins.
    5. **Lowest next_hop** — lexicographic string compare; lower wins.

    Return the single winning ``BgpPath``.

    See ``docs/tutorial/lab22_bgp_attributes_and_bestpath.md`` for the walkthrough.
    """
    if not paths:
        raise ValueError("at least one path is required")
    return min(
        paths,
        key=lambda path: (
            -path.local_pref,
            len(path.as_path),
            _origin_rank(path.origin),
            path.med,
            path.neighbor_id,
            path.next_hop,
        ),
    )


def apply_export_policy(*, paths: list[BgpPath], denied_prefixes: set[str], local_pref_override: int | None = None) -> list[BgpPath]:
    exported: list[BgpPath] = []
    for path in paths:
        prefix = f"{path.prefix}/{path.prefix_len}"
        if prefix in denied_prefixes:
            continue
        if local_pref_override is None:
            exported.append(path)
        else:
            exported.append(
                BgpPath(
                    prefix=path.prefix,
                    prefix_len=path.prefix_len,
                    next_hop=path.next_hop,
                    neighbor_id=path.neighbor_id,
                    local_pref=local_pref_override,
                    as_path=path.as_path,
                    med=path.med,
                    origin=path.origin,
                )
            )
    return exported


def route_reflect(*, learned: dict[str, list[str]], source_client: str) -> dict[str, list[str]]:
    reflected: dict[str, list[str]] = {}
    source_routes = learned.get(source_client, [])
    for client_id in sorted(learned):
        if client_id == source_client:
            continue
        reflected[client_id] = sorted(source_routes)
    return reflected


def convergence_mark(*, before: dict[str, str], after: dict[str, str]) -> bool:
    return before == after
