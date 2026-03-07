"""IPv6 control-plane mechanisms: ND/SLAAC, OSPFv3, and MP-BGP for IPv6.

IPv6 replaces many IPv4 mechanisms with cleaner, integrated protocols:

- **Neighbor Discovery (ND)** — the IPv6 equivalent of ARP; routers send
  Router Advertisements (RAs) to announce prefixes.  *RA Guard* protects
  hosts by dropping RA messages from untrusted ports (rogue router prevention).
- **SLAAC (Stateless Address Autoconfiguration)** — hosts derive their own
  global unicast address from the RA prefix + their link-local interface ID.
- **OSPFv3** — the IPv6 extension of OSPFv2; same adjacency FSM and LSDB
  mechanics but adapted for IPv6 link-local addressing.
- **MP-BGP for IPv6 Unicast** — BGP with MultiProtocol extensions (RFC 4760)
  carries IPv6 prefixes.  Best-path selection uses the same priority chain as
  IPv4 BGP (local-pref, AS-path length, next-hop).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Ospfv3State = Literal["DOWN", "FULL"]


def derive_slaac_host_id(*, source_link_local: str) -> str:
    """Derive a deterministic SLAAC host ID from a link-local address.

    Extract the part after ``"fe80::"``.  If empty (i.e., the address is
    exactly ``"fe80::"``) return ``"1"`` as the minimum host identifier.

    Examples:
    - ``"fe80::10"`` → ``"10"``
    - ``"fe80::"`` → ``"1"``

    # TODO(student): implement derive_slaac_host_id.
    """
    raise NotImplementedError("TODO: implement derive_slaac_host_id")


def ospfv3_neighbor_result(*, hello_ok: bool) -> Ospfv3State:
    """Map hello acceptance to OSPFv3 adjacency state.

    - ``hello_ok=True`` → ``"FULL"``
    - ``hello_ok=False`` → ``"DOWN"``

    # TODO(student): implement ospfv3_neighbor_result.
    """
    raise NotImplementedError("TODO: implement ospfv3_neighbor_result")


def ipv6_nd_slaac_ra_guard(
    *, ra_trusted: bool, source_link_local: str, prefix: str
) -> tuple[str, str]:
    """Enforce RA Guard and derive a SLAAC address from a trusted RA.

    Rules:
    - ``ra_trusted=False`` → ``("DROP", "")``  — discard untrusted RA.
    - ``ra_trusted=True`` → allow and derive SLAAC address:
      Extract the host portion from ``source_link_local`` (the part after
      ``"fe80::"``) and append it to ``prefix`` (strip its trailing ``"::"``
      if present).
      Example: prefix ``"2001:db8:100::"`` + link-local ``"fe80::10"``
      → SLAAC address ``"2001:db8:100::10"``.
      Return ``("ALLOW", slaac_address)``.

    See ``docs/tutorial/lab34_ipv6_nd_slaac_and_ra_guard.md``.

    # TODO(student): implement ipv6_nd_slaac_ra_guard.
    """
    raise NotImplementedError("TODO: implement ipv6_nd_slaac_ra_guard")


def ospfv3_adjacency_lsdb(
    *, hello_ok: bool, lsa_id: str, lsdb: set[str]
) -> tuple[str, set[str]]:
    """Transition OSPFv3 adjacency state and install LSAs into the LSDB.

    Rules:
    - ``hello_ok=False`` → adjacency is ``"DOWN"``; do not install LSA.
      Return ``("DOWN", lsdb)`` (unchanged lsdb).
    - ``hello_ok=True`` → adjacency is ``"FULL"``; install the LSA.
      Return ``("FULL", lsdb | {lsa_id})``.

    See ``docs/tutorial/lab35_ospfv3_adjacency_and_lsdb.md``.

    # TODO(student): implement ospfv3_adjacency_lsdb.
    """
    raise NotImplementedError("TODO: implement ospfv3_adjacency_lsdb")


@dataclass(frozen=True)
class MpbgpPath:
    """An MP-BGP path entry for an IPv6 prefix."""

    prefix: str
    local_pref: int
    as_path_len: int
    next_hop: str


def rank_mpbgp_path(path: MpbgpPath) -> tuple[int, int, str]:
    """Return a stable sort key for an MP-BGP path.

    Tiebreak tuple: ``(-local_pref, as_path_len, next_hop)``.

    Negating ``local_pref`` means ``sorted()`` (ascending) will prefer higher
    local-pref.  Shorter AS-path and lexicographically lower next-hop break
    remaining ties.

    # TODO(student): implement rank_mpbgp_path.
    """
    raise NotImplementedError("TODO: implement rank_mpbgp_path")


def mpbgp_ipv6_unicast(paths: list[MpbgpPath]) -> MpbgpPath:
    """Choose the best MP-BGP path for an IPv6 unicast prefix.

    Raises ``ValueError`` if ``paths`` is empty.

    Tiebreak chain (highest priority first):

    1. **Highest local_pref** — larger wins.
    2. **Shortest AS path** — smaller ``as_path_len`` wins.
    3. **Lowest next_hop** — lexicographic string compare; lower wins.

    See ``docs/tutorial/lab36_mpbgp_ipv6_unicast.md``.

    # TODO(student): implement mpbgp_ipv6_unicast using the tiebreak chain above.
    """
    raise NotImplementedError("TODO: implement mpbgp_ipv6_unicast")
