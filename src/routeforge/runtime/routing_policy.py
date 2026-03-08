"""Routing policy mechanisms: route redistribution and FHRP failover.

This module covers inter-protocol interactions and high-availability routing:

- **Route redistribution** — importing routes from one protocol into another
  (e.g., OSPF → BGP).  Without loop prevention, redistribution can cause
  routing loops where routes bounce back and forth between protocols.  Route
  tagging identifies redistributed routes so they are not re-imported.
- **FHRP (First Hop Redundancy Protocol)** — protocols like HSRP and VRRP
  elect an *active* gateway router that hosts a virtual IP.  When the active
  router's tracked object goes down (e.g., upstream link failure), it yields
  the active role to the *standby* router.
"""

from __future__ import annotations

from typing import Literal, TypeAlias

RedistributionAction: TypeAlias = Literal["IMPORT", "LOOP_SUPPRESS"]
TrackState: TypeAlias = Literal["UP", "DOWN"]


def build_redistribution_tag(*, source_prefix: str, source_protocol: str) -> str:
    """Build canonical redistribution tag used for loop guard."""
    return f"{source_protocol.upper()}:{source_prefix}"


def redistribute_with_loop_guard(
    *,
    source_prefix: str,
    source_protocol: str,
    existing_tags: set[str],
) -> tuple[set[str], RedistributionAction]:
    """Import once per source tag; suppress re-import loops."""
    tag = build_redistribution_tag(source_prefix=source_prefix, source_protocol=source_protocol)
    if tag in existing_tags:
        return existing_tags, "LOOP_SUPPRESS"
    updated = set(existing_tags)
    updated.add(tag)
    return updated, "IMPORT"


def tracked_object_result(*, tracked_object_up: bool) -> TrackState:
    """Convert object boolean into explicit UP/DOWN state."""
    return "UP" if tracked_object_up else "DOWN"


def fhrp_track_failover(*, active_router: str, standby_router: str, tracked_object_up: bool) -> str:
    """Return active router choice based on tracked-object state."""
    if tracked_object_result(tracked_object_up=tracked_object_up) == "UP":
        return active_router
    return standby_router
