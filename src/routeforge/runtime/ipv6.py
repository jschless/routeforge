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
from typing import Literal, TypeAlias

RaGuardAction: TypeAlias = Literal["ALLOW", "DROP"]
Ospfv3State: TypeAlias = Literal["DOWN", "FULL"]


def derive_slaac_host_id(*, source_link_local: str) -> str:
    """Extract deterministic host-id from link-local address."""
    return source_link_local.split("::")[-1] or "1"


def ipv6_nd_slaac_ra_guard(
    *, ra_trusted: bool, source_link_local: str, prefix: str
) -> tuple[RaGuardAction, str]:
    """Apply RA guard and derive SLAAC host address when allowed."""
    if not ra_trusted:
        return "DROP", ""
    host = derive_slaac_host_id(source_link_local=source_link_local)
    address = f"{prefix}{host}"
    return "ALLOW", address


def ospfv3_neighbor_result(*, hello_ok: bool) -> Ospfv3State:
    """Derive OSPFv3 adjacency state from hello acceptance."""
    return "FULL" if hello_ok else "DOWN"


def ospfv3_adjacency_lsdb(
    *, hello_ok: bool, lsa_id: str, lsdb: set[str]
) -> tuple[Ospfv3State, set[str]]:
    """Return adjacency state and LSDB snapshot after hello/LSA handling."""
    state = ospfv3_neighbor_result(hello_ok=hello_ok)
    if state == "DOWN":
        return state, set(lsdb)
    updated = set(lsdb)
    updated.add(lsa_id)
    return state, updated


@dataclass(frozen=True)
class MpbgpPath:
    """An MP-BGP path entry for an IPv6 prefix."""

    prefix: str
    local_pref: int
    as_path_len: int
    next_hop: str


def rank_mpbgp_path(path: MpbgpPath) -> tuple[int, int, str]:
    """Return stable rank tuple for MP-BGP path selection."""
    return (-path.local_pref, path.as_path_len, path.next_hop)


def mpbgp_ipv6_unicast(paths: list[MpbgpPath]) -> MpbgpPath:
    """Pick deterministic MP-BGP best path (local-pref, AS-path, next-hop)."""
    if not paths:
        raise ValueError("at least one path is required")
    return min(paths, key=rank_mpbgp_path)
