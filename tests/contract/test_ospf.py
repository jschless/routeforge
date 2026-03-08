from __future__ import annotations

from routeforge.runtime.ospf import (
    AreaRoute,
    DrCandidate,
    LsaRecord,
    Lsdb,
    elect_dr_bdr,
    failover_dr_bdr,
    neighbor_hello_transition,
    next_hop_for_destination,
    originate_summaries,
    run_spf,
)


def test_neighbor_fsm_transitions_to_full_and_back_to_down() -> None:
    state = "DOWN"
    state = neighbor_hello_transition(current_state=state, hello_received=True, dead_timer_expired=False)
    state = neighbor_hello_transition(current_state=state, hello_received=True, dead_timer_expired=False)
    state = neighbor_hello_transition(current_state=state, hello_received=True, dead_timer_expired=False)
    assert state == "FULL", f"Expected FULL after 3 hellos but got {state!r}; neighbor_hello_transition must return 'FULL' when hello_received=True and dead_timer_expired=False"
    state = neighbor_hello_transition(current_state=state, hello_received=False, dead_timer_expired=True)
    assert state == "DOWN", f"Expected DOWN after dead_timer_expired=True but got {state!r}; dead_timer_expired always transitions to DOWN regardless of current state"


def test_dr_bdr_election_and_failover() -> None:
    candidates = [
        DrCandidate(router_id="1.1.1.1", priority=100),
        DrCandidate(router_id="2.2.2.2", priority=90),
        DrCandidate(router_id="3.3.3.3", priority=80),
    ]
    dr, bdr = elect_dr_bdr(candidates)
    assert (dr, bdr) == ("1.1.1.1", "2.2.2.2"), (
        f"Expected DR=1.1.1.1 BDR=2.2.2.2 but got DR={dr!r} BDR={bdr!r}; "
        "_election_order must sort by highest priority first, then highest router_id"
    )
    dr, bdr = failover_dr_bdr(candidates, active_router_ids={"2.2.2.2", "3.3.3.3"})
    assert (dr, bdr) == ("2.2.2.2", "3.3.3.3"), (
        f"Expected DR=2.2.2.2 BDR=3.3.3.3 after failover but got DR={dr!r} BDR={bdr!r}; "
        "failover_dr_bdr must filter to active_router_ids before electing"
    )


def test_lsdb_install_refresh_age_out() -> None:
    lsdb = Lsdb(max_age=3)
    key = ("10.0.0.0/24", "1.1.1.1")
    lsdb.install(LsaRecord(lsa_id=key[0], advertising_router=key[1], sequence=1, age=0, payload={}))
    refreshed = lsdb.refresh(key)
    assert refreshed.sequence == 2, f"Expected sequence=2 after refresh but got {refreshed.sequence}; refresh must increment sequence by 1"
    lsdb.age_tick(1)
    lsdb.age_tick(1)
    expired = lsdb.age_tick(1)
    assert key in expired, f"Expected {key} in expired list after 3 age_ticks with max_age=3; age_tick must remove records at or above max_age"
    assert key not in lsdb.records, f"Expected {key} to be removed from lsdb.records after aging out; age_tick must delete expired LSAs"


def test_spf_and_summary_helpers() -> None:
    graph = {
        "1.1.1.1": [("2.2.2.2", 10), ("3.3.3.3", 30)],
        "2.2.2.2": [("1.1.1.1", 10), ("3.3.3.3", 5)],
        "3.3.3.3": [("1.1.1.1", 30), ("2.2.2.2", 5)],
    }
    spf = run_spf(graph, root_router_id="1.1.1.1")
    assert spf.cost_by_router["3.3.3.3"] == 15, (
        f"Expected cost 15 to reach 3.3.3.3 (via 2.2.2.2: 10+5) but got {spf.cost_by_router.get('3.3.3.3')}; "
        "run_spf must find the shortest path, not the direct path (cost=30)"
    )
    assert next_hop_for_destination(spf, destination_router_id="3.3.3.3") == "2.2.2.2", (
        f"Expected next_hop 2.2.2.2 for 3.3.3.3 but got {next_hop_for_destination(spf, destination_router_id='3.3.3.3')!r}; "
        "next_hop_for_destination must walk parent_by_router back to the root's direct neighbor"
    )

    summaries = originate_summaries(
        [
            AreaRoute(area_id=1, prefix="10.10.1.0", prefix_len=24, cost=20),
            AreaRoute(area_id=1, prefix="10.10.2.0", prefix_len=24, cost=10),
            AreaRoute(area_id=2, prefix="10.20.1.0", prefix_len=24, cost=30),
        ]
    )
    summary_strings = [f"{s.prefix}/{s.prefix_len}" for s in summaries]
    assert summary_strings == ["10.10.0.0/16", "10.20.0.0/16"], (
        f"Expected ['10.10.0.0/16', '10.20.0.0/16'] but got {summary_strings}; "
        "originate_summaries must aggregate non-backbone routes to /16 per area_id, sorted by (area_id, prefix)"
    )
