from __future__ import annotations

from routeforge.runtime.capstone import ScenarioState, apply_step, convergence_assert
from routeforge.runtime.observability import emit_telemetry, readiness_check
from routeforge.runtime.tunnel_ipsec import decapsulate, encapsulate, evaluate_ipsec_policy, lookup_sa


def test_tunnel_and_ipsec_helpers() -> None:
    packet = encapsulate(
        payload_id="pkt-1",
        inner_src="10.1.0.1",
        inner_dst="10.2.0.1",
        tunnel_src="192.0.2.1",
        tunnel_dst="192.0.2.2",
    )
    assert (packet.outer_src, packet.outer_dst) == ("192.0.2.1", "192.0.2.2")
    assert decapsulate(packet) == ("pkt-1", "10.1.0.1", "10.2.0.1")
    assert evaluate_ipsec_policy(destination_ip="10.2.0.1", protected_prefixes=("10.2.0.0/16",)) == "PROTECT"
    assert lookup_sa(sa_db={"192.0.2.2": 1001}, peer_ip="192.0.2.2") == 1001


def test_observability_and_capstone_helpers() -> None:
    readiness = readiness_check(checks={"bgp_up": True, "ospf_full": False})
    assert readiness.ready is False
    assert readiness.failed_checks == ("ospf_full",)

    telemetry = emit_telemetry(component="edge-r1", counters={"drops": 1, "fwd": 10}, timestamp_s=100)
    assert telemetry["counters"] == {"drops": 1, "fwd": 10}

    baseline = ScenarioState(label="baseline", routes={"203.0.113.0/24": "bgp"}, alarms=())
    failure = apply_step(
        baseline,
        label="incident",
        route_updates={"203.0.113.0/24": "ospf"},
        raise_alarms=("BFD_DOWN",),
    )
    recovered = apply_step(
        failure,
        label="recovered",
        route_updates={"203.0.113.0/24": "bgp"},
        clear_alarms=("BFD_DOWN",),
    )
    assert convergence_assert(
        state=recovered,
        expected_routes={"203.0.113.0/24": "bgp"},
        expected_alarms=(),
    )
