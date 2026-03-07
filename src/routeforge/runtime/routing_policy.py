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

from typing import Literal

TrackState = Literal["UP", "DOWN"]


def tracked_object_result(*, tracked_object_up: bool) -> TrackState:
    """Convert tracked-object boolean into deterministic UP/DOWN state string.

    - ``tracked_object_up=True`` → ``"UP"``
    - ``tracked_object_up=False`` → ``"DOWN"``

    # TODO(student): implement tracked_object_result.
    """
    raise NotImplementedError("TODO: implement tracked_object_result")


def build_redistribution_tag(*, source_prefix: str, source_protocol: str) -> str:
    """Build a canonical redistribution tag in ``PROTOCOL:prefix`` format.

    The protocol portion is uppercased: ``f"{source_protocol.upper()}:{source_prefix}"``.

    Example: ``build_redistribution_tag(source_prefix="10.40.0.0/16", source_protocol="ospf")``
    → ``"OSPF:10.40.0.0/16"``

    # TODO(student): implement build_redistribution_tag.
    """
    raise NotImplementedError("TODO: implement build_redistribution_tag")


def redistribute_with_loop_guard(
    *,
    source_prefix: str,
    source_protocol: str,
    existing_tags: set[str],
) -> tuple[set[str], str]:
    """Tag redistributed routes and suppress looped re-imports.

    A route is identified by a tag string ``"<protocol>:<prefix>"``.

    Steps:
    1. Compute the tag: ``tag = f"{source_protocol}:{source_prefix}"``.
    2. If ``tag`` is already in ``existing_tags`` → this is a loop.
       Return ``(existing_tags, "LOOP_SUPPRESS")`` without modifying tags.
    3. Otherwise → safe to import.
       Add ``tag`` to a copy of ``existing_tags``.
       Return ``(new_tags, "IMPORT")``.

    See ``docs/tutorial/lab32_route_redistribution_and_loop_prevention.md``.

    # TODO(student): implement redistribute_with_loop_guard.
    """
    raise NotImplementedError("TODO: implement redistribute_with_loop_guard")


def fhrp_track_failover(
    *, active_router: str, standby_router: str, tracked_object_up: bool
) -> str:
    """Choose the active FHRP router based on tracked object state.

    - ``tracked_object_up=True`` → return ``active_router`` (no failover needed).
    - ``tracked_object_up=False`` → return ``standby_router`` (active has failed).

    See ``docs/tutorial/lab33_fhrp_tracking_and_failover.md``.

    # TODO(student): implement fhrp_track_failover.
    """
    raise NotImplementedError("TODO: implement fhrp_track_failover")
