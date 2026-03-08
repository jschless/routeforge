from __future__ import annotations

from routeforge.runtime.bgp import (
    BgpPath,
    apply_export_policy,
    bgp_session_transition,
    convergence_mark,
    route_reflect,
    select_best_path,
)


def test_bgp_session_fsm_establish_and_reset() -> None:
    state = "IDLE"
    state = bgp_session_transition(current_state=state, event="TCP_CONNECTED")
    state = bgp_session_transition(current_state=state, event="OPEN_RX")
    state = bgp_session_transition(current_state=state, event="KEEPALIVE_RX")
    assert state == "ESTABLISHED", (
        f"Expected ESTABLISHED after TCP_CONNECTED→OPEN_RX→KEEPALIVE_RX but got {state!r}; "
        "check bgp_session_transition for each event in the FSM table"
    )
    final = bgp_session_transition(current_state=state, event="HOLD_TIMER_EXPIRE")
    assert final == "IDLE", (
        f"Expected IDLE after HOLD_TIMER_EXPIRE from ESTABLISHED but got {final!r}; "
        "any unrecognized or error event from ESTABLISHED must return IDLE"
    )


def test_bgp_bestpath_policy_reflection_and_convergence() -> None:
    paths = [
        BgpPath(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.10",
            neighbor_id="2.2.2.2",
            local_pref=200,
            as_path=(65010, 65100),
            med=20,
            origin="igp",
        ),
        BgpPath(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.11",
            neighbor_id="3.3.3.3",
            local_pref=200,
            as_path=(65020, 65100, 65200),
            med=10,
            origin="igp",
        ),
        BgpPath(
            prefix="198.51.100.0",
            prefix_len=24,
            next_hop="192.0.2.12",
            neighbor_id="4.4.4.4",
            local_pref=150,
            as_path=(65030, 65100),
            med=5,
            origin="igp",
        ),
    ]
    best = select_best_path(paths[:2])
    assert best.neighbor_id == "2.2.2.2", (
        f"Expected best path from neighbor 2.2.2.2 (shorter AS path: 2 hops) but got {best.neighbor_id!r}; "
        "both paths have equal local_pref=200, so shortest AS path (2 vs 3 hops) breaks the tie"
    )

    exported = apply_export_policy(
        paths=paths,
        denied_prefixes={"203.0.113.0/24"},
        local_pref_override=250,
    )
    exported_prefixes = [f"{path.prefix}/{path.prefix_len}" for path in exported]
    assert exported_prefixes == ["198.51.100.0/24"], (
        f"Expected only ['198.51.100.0/24'] after filtering 203.0.113.0/24 but got {exported_prefixes}; "
        "apply_export_policy must remove paths whose prefix matches denied_prefixes"
    )
    assert exported[0].local_pref == 250, (
        f"Expected local_pref=250 after override but got {exported[0].local_pref}; "
        "apply_export_policy must replace local_pref with local_pref_override when it is not None"
    )

    reflected = route_reflect(
        learned={"C1": ["10.0.0.0/24"], "C2": [], "C3": []},
        source_client="C1",
    )
    assert reflected == {"C2": ["10.0.0.0/24"], "C3": ["10.0.0.0/24"]}, (
        f"Expected C2 and C3 to receive C1's prefixes but got {reflected}; "
        "route_reflect must distribute source_client's routes to all other clients"
    )
    assert convergence_mark(before={"C2": "10.0.0.0/24"}, after={"C2": "10.0.0.0/24"}) is True
