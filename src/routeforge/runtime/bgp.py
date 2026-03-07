"""Deterministic BGP helpers for labs 21-24."""

from __future__ import annotations

from dataclasses import dataclass


def bgp_session_transition(*, current_state: str, event: str) -> str:
    """Return the next BGP session state given ``current_state`` and ``event``.

    Simplified FSM used in this lab (subset of RFC 4271 §8):

    | State        | Event            | Next state   |
    |-------------|------------------|--------------|
    | IDLE         | START            | CONNECT      |
    | IDLE         | (any other)      | IDLE         |
    | CONNECT      | TCP_OPEN         | OPEN_SENT    |
    | CONNECT      | TCP_FAIL         | IDLE         |
    | CONNECT      | (any other)      | IDLE         |
    | OPEN_SENT    | OPEN_RECEIVED    | OPEN_CONFIRM |
    | OPEN_SENT    | ERROR            | IDLE         |
    | OPEN_SENT    | (any other)      | IDLE         |
    | OPEN_CONFIRM | KEEPALIVE        | ESTABLISHED  |
    | OPEN_CONFIRM | ERROR            | IDLE         |
    | OPEN_CONFIRM | (any other)      | IDLE         |
    | ESTABLISHED  | KEEPALIVE        | ESTABLISHED  |
    | ESTABLISHED  | NOTIFICATION     | IDLE         |
    | ESTABLISHED  | (any other)      | IDLE         |

    Valid states: ``"IDLE"``, ``"CONNECT"``, ``"OPEN_SENT"``,
    ``"OPEN_CONFIRM"``, ``"ESTABLISHED"``.

    Unknown current_state should return ``"IDLE"``.

    See ``docs/tutorial/lab21_bgp_session_fsm_and_transport.md`` for the walkthrough.

    # TODO(student): implement bgp_session_transition using the table above.
    """
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

    # TODO(student): implement select_best_path using the chain above.
    """
    raise NotImplementedError("TODO: implement select_best_path")


def apply_export_policy(*, paths: list[BgpPath], denied_prefixes: set[str], local_pref_override: int | None = None) -> list[BgpPath]:
    """Filter and modify paths according to an export policy.

    1. Remove any path whose ``prefix`` is in ``denied_prefixes``.
    2. If ``local_pref_override`` is not None, replace ``local_pref`` on all
       remaining paths with the override value.
    3. Return the filtered/modified list preserving original order.

    # TODO(student): implement apply_export_policy.
    """
    raise NotImplementedError("TODO: implement apply_export_policy")


def route_reflect(*, learned: dict[str, list[str]], source_client: str) -> dict[str, list[str]]:
    """Reflect routes learned from ``source_client`` to all other clients.

    ``learned`` maps client_id → list of prefix strings that client advertised.

    Return a new dict mapping every client_id *except* ``source_client`` to
    the list of prefixes that ``source_client`` advertised.  Clients not in
    ``learned`` who should receive reflections are identified by the keys in
    ``learned`` minus ``source_client``.

    Result keys: all keys in ``learned`` except ``source_client``.
    Result values: ``learned[source_client]`` (the same list object is fine).

    # TODO(student): implement route_reflect.
    """
    raise NotImplementedError("TODO: implement route_reflect")


def convergence_mark(*, before: dict[str, str], after: dict[str, str]) -> bool:
    return before == after
