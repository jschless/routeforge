from __future__ import annotations

import pytest

from routeforge.runtime.bgp import BgpPath, apply_export_policy, bgp_session_transition, select_best_path
from routeforge.runtime.capstone import ScenarioState, apply_step
from routeforge.runtime.l3 import ForwardingDecision, RibTable, RouteEntry, explain_drop
from routeforge.runtime.nat44 import Nat44Table
from routeforge.runtime.observability import emit_telemetry
from routeforge.runtime.ospf import DrCandidate, LsaRecord, Lsdb, failover_dr_bdr, next_hop_for_destination, run_spf
from routeforge.runtime.qos import QosEngine
from routeforge.runtime.stp import bpdu_guard_decision, compute_stp
from routeforge.runtime.tunnel_ipsec import evaluate_ipsec_policy


def test_explain_drop_reports_forward_and_drop_paths() -> None:
    forward = ForwardingDecision(action="FORWARD", reason="FIB_HIT", ttl_after=63, out_if="eth0", next_hop="192.0.2.1")
    drop = ForwardingDecision(action="DROP", reason="NO_ROUTE", ttl_after=None, out_if=None, next_hop=None)
    assert explain_drop(forward) == "forward path healthy"
    assert explain_drop(drop) == "drop_reason=NO_ROUTE"


def test_rib_lookup_uses_next_hop_as_final_tiebreaker() -> None:
    rib = RibTable()
    rib.install(
        RouteEntry(
            prefix="10.1.0.0",
            prefix_len=16,
            next_hop="192.0.2.20",
            out_if="eth1",
            protocol="ospf",
            admin_distance=110,
            metric=10,
        )
    )
    rib.install(
        RouteEntry(
            prefix="10.1.0.0",
            prefix_len=16,
            next_hop="192.0.2.10",
            out_if="eth2",
            protocol="ospf",
            admin_distance=110,
            metric=10,
        )
    )

    selected = rib.lookup("10.1.2.3")
    assert selected is not None
    assert selected.next_hop == "192.0.2.10"


def test_compute_stp_rejects_empty_topology() -> None:
    with pytest.raises(ValueError, match="bridges must not be empty"):
        compute_stp([], [])


def test_bpdu_guard_allows_non_edge_ports() -> None:
    decision = bpdu_guard_decision(port=("S1", "Gi0/10"), edge_port=False, bpdu_received=True)
    assert decision.action == "FORWARD"
    assert decision.reason == "STP_GUARD_CLEAR"


def test_ospf_failover_requires_active_candidates() -> None:
    candidates = [DrCandidate(router_id="1.1.1.1", priority=100)]
    with pytest.raises(ValueError, match="at least one candidate is required"):
        failover_dr_bdr(candidates, active_router_ids=set())


def test_ospf_spf_tie_breaks_on_parent_router_id() -> None:
    graph = {
        "R1": [("R2", 10), ("R3", 10)],
        "R2": [("R4", 10)],
        "R3": [("R4", 10)],
        "R4": [],
    }
    spf = run_spf(graph, root_router_id="R1")
    assert spf.cost_by_router["R4"] == 20
    assert next_hop_for_destination(spf, destination_router_id="R4") == "R2"


def test_ospf_age_tick_keeps_nonexpired_records() -> None:
    lsdb = Lsdb(max_age=10)
    lsdb.install(LsaRecord(lsa_id="10.0.0.0/24", advertising_router="1.1.1.1", sequence=1, age=9, payload={}))
    lsdb.install(LsaRecord(lsa_id="10.1.0.0/24", advertising_router="2.2.2.2", sequence=1, age=1, payload={}))

    expired = lsdb.age_tick(seconds=2)
    assert ("10.0.0.0/24", "1.1.1.1") in expired
    assert ("10.1.0.0/24", "2.2.2.2") not in expired
    assert ("10.1.0.0/24", "2.2.2.2") in lsdb.records


def test_bgp_best_path_uses_full_tiebreak_chain() -> None:
    paths = [
        BgpPath(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.10",
            neighbor_id="2.2.2.2",
            local_pref=200,
            as_path=(65010, 65100),
            med=50,
            origin="igp",
        ),
        BgpPath(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.11",
            neighbor_id="1.1.1.1",
            local_pref=200,
            as_path=(65010, 65100),
            med=50,
            origin="igp",
        ),
        BgpPath(
            prefix="203.0.113.0",
            prefix_len=24,
            next_hop="192.0.2.12",
            neighbor_id="3.3.3.3",
            local_pref=200,
            as_path=(65010, 65100),
            med=30,
            origin="igp",
        ),
    ]

    best = select_best_path(paths)
    assert best.next_hop == "192.0.2.12"


def test_bgp_export_policy_preserves_local_pref_when_no_override() -> None:
    input_path = BgpPath(
        prefix="198.51.100.0",
        prefix_len=24,
        next_hop="192.0.2.20",
        neighbor_id="9.9.9.9",
        local_pref=150,
        as_path=(65100,),
        med=10,
        origin="igp",
    )
    exported = apply_export_policy(paths=[input_path], denied_prefixes=set(), local_pref_override=None)
    assert len(exported) == 1
    assert exported[0].local_pref == 150


def test_bgp_unknown_event_does_not_change_state() -> None:
    assert bgp_session_transition(current_state="ESTABLISHED", event="SOMETHING_ELSE") == "ESTABLISHED"


def test_nat_inbound_miss_and_fresh_sessions_not_expired() -> None:
    nat = Nat44Table(public_ip="203.0.113.254")
    assert nat.inbound_translate(outside_port=65000, protocol="tcp", now=0) is None

    created = nat.outbound_translate(inside_ip="10.0.0.1", inside_port=1111, protocol="tcp", now=10)
    assert created is not None
    assert nat.expire(now=20, timeout=30) == []


def test_qos_dequeue_falls_back_to_default_queue() -> None:
    qos = QosEngine()
    qos.enqueue(packet_id="pkt-default", dscp=0)
    packet, queue = qos.dequeue()
    assert (packet, queue) == ("pkt-default", "default")


def test_observability_and_capstone_outputs_are_deterministic() -> None:
    telemetry = emit_telemetry(component="edge-r1", counters={"z": 1, "a": 2}, timestamp_s=42)
    assert list(telemetry["counters"].keys()) == ["a", "z"]

    baseline = ScenarioState(label="base", routes={"203.0.113.0/24": "bgp"}, alarms=("WARN_Z",))
    updated = apply_step(
        baseline,
        label="incident",
        route_updates={"203.0.113.0/24": "ospf"},
        raise_alarms=("WARN_A",),
        clear_alarms=("WARN_Z",),
    )
    assert updated.routes["203.0.113.0/24"] == "ospf"
    assert updated.alarms == ("WARN_A",)


def test_tunnel_policy_bypass_for_nonprotected_prefix() -> None:
    action = evaluate_ipsec_policy(destination_ip="198.51.100.1", protected_prefixes=("10.0.0.0/8",))
    assert action == "BYPASS"
