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
    assert state == "FULL"
    state = neighbor_hello_transition(current_state=state, hello_received=False, dead_timer_expired=True)
    assert state == "DOWN"


def test_dr_bdr_election_and_failover() -> None:
    candidates = [
        DrCandidate(router_id="1.1.1.1", priority=100),
        DrCandidate(router_id="2.2.2.2", priority=90),
        DrCandidate(router_id="3.3.3.3", priority=80),
    ]
    dr, bdr = elect_dr_bdr(candidates)
    assert (dr, bdr) == ("1.1.1.1", "2.2.2.2")
    dr, bdr = failover_dr_bdr(candidates, active_router_ids={"2.2.2.2", "3.3.3.3"})
    assert (dr, bdr) == ("2.2.2.2", "3.3.3.3")


def test_lsdb_install_refresh_age_out() -> None:
    lsdb = Lsdb(max_age=3)
    key = ("10.0.0.0/24", "1.1.1.1")
    lsdb.install(LsaRecord(lsa_id=key[0], advertising_router=key[1], sequence=1, age=0, payload={}))
    refreshed = lsdb.refresh(key)
    assert refreshed.sequence == 2
    lsdb.age_tick(1)
    lsdb.age_tick(1)
    expired = lsdb.age_tick(1)
    assert key in expired
    assert key not in lsdb.records


def test_spf_and_summary_helpers() -> None:
    graph = {
        "1.1.1.1": [("2.2.2.2", 10), ("3.3.3.3", 30)],
        "2.2.2.2": [("1.1.1.1", 10), ("3.3.3.3", 5)],
        "3.3.3.3": [("1.1.1.1", 30), ("2.2.2.2", 5)],
    }
    spf = run_spf(graph, root_router_id="1.1.1.1")
    assert spf.cost_by_router["3.3.3.3"] == 15
    assert next_hop_for_destination(spf, destination_router_id="3.3.3.3") == "2.2.2.2"

    summaries = originate_summaries(
        [
            AreaRoute(area_id=1, prefix="10.10.1.0", prefix_len=24, cost=20),
            AreaRoute(area_id=1, prefix="10.10.2.0", prefix_len=24, cost=10),
            AreaRoute(area_id=2, prefix="10.20.1.0", prefix_len=24, cost=30),
        ]
    )
    assert [f"{summary.prefix}/{summary.prefix_len}" for summary in summaries] == ["10.10.0.0/16", "10.20.0.0/16"]
