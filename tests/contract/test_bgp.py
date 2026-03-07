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
    assert state == "ESTABLISHED"
    assert bgp_session_transition(current_state=state, event="HOLD_TIMER_EXPIRE") == "IDLE"


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
    assert best.neighbor_id == "2.2.2.2"

    exported = apply_export_policy(
        paths=paths,
        denied_prefixes={"203.0.113.0/24"},
        local_pref_override=250,
    )
    assert [f"{path.prefix}/{path.prefix_len}" for path in exported] == ["198.51.100.0/24"]
    assert exported[0].local_pref == 250

    reflected = route_reflect(
        learned={"C1": ["10.0.0.0/24"], "C2": [], "C3": []},
        source_client="C1",
    )
    assert reflected == {"C2": ["10.0.0.0/24"], "C3": ["10.0.0.0/24"]}
    assert convergence_mark(before={"C2": "10.0.0.0/24"}, after={"C2": "10.0.0.0/24"}) is True
