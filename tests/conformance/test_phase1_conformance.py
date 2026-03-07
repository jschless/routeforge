from __future__ import annotations

from routeforge.labs.conformance import load_conformance_matrix
from routeforge.labs.exercises import run_lab


def _feature_checkpoints_for_lab(lab_id: str) -> set[str]:
    matrix = load_conformance_matrix()
    coverage = matrix.coverage_for_lab(lab_id)
    assert coverage is not None
    checkpoints: set[str] = set()
    for feature_id in coverage.must:
        checkpoints.update(matrix.features_by_id[feature_id].checkpoints)
    return checkpoints


def test_lab01_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab01_frame_and_headers")
    result = run_lab("lab01_frame_and_headers")
    assert required <= set(result.checkpoints)


def test_lab02_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab02_mac_learning_switch")
    result = run_lab("lab02_mac_learning_switch")
    assert required <= set(result.checkpoints)


def test_lab03_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab03_vlan_and_trunks")
    result = run_lab("lab03_vlan_and_trunks")
    assert required <= set(result.checkpoints)


def test_lab04_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab04_stp")
    result = run_lab("lab04_stp")
    assert required <= set(result.checkpoints)


def test_lab05_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab05_stp_convergence_and_protection")
    result = run_lab("lab05_stp_convergence_and_protection")
    assert required <= set(result.checkpoints)


def test_lab06_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab06_arp_and_adjacency")
    result = run_lab("lab06_arp_and_adjacency")
    assert required <= set(result.checkpoints)


def test_lab07_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab07_ipv4_subnet_and_rib")
    result = run_lab("lab07_ipv4_subnet_and_rib")
    assert required <= set(result.checkpoints)


def test_lab08_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab08_fib_forwarding_pipeline")
    result = run_lab("lab08_fib_forwarding_pipeline")
    assert required <= set(result.checkpoints)


def test_lab09_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab09_icmp_and_control_responses")
    result = run_lab("lab09_icmp_and_control_responses")
    assert required <= set(result.checkpoints)


def test_lab10_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab10_ipv4_control_plane_diagnostics")
    result = run_lab("lab10_ipv4_control_plane_diagnostics")
    assert required <= set(result.checkpoints)


def test_lab11_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab11_ospf_adjacency_fsm")
    result = run_lab("lab11_ospf_adjacency_fsm")
    assert required <= set(result.checkpoints)


def test_lab12_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab12_ospf_network_types_and_dr_bdr")
    result = run_lab("lab12_ospf_network_types_and_dr_bdr")
    assert required <= set(result.checkpoints)


def test_lab13_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab13_ospf_lsa_flooding_and_lsdb")
    result = run_lab("lab13_ospf_lsa_flooding_and_lsdb")
    assert required <= set(result.checkpoints)


def test_lab14_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab14_ospf_spf_and_route_install")
    result = run_lab("lab14_ospf_spf_and_route_install")
    assert required <= set(result.checkpoints)


def test_lab15_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab15_ospf_multi_area_abr")
    result = run_lab("lab15_ospf_multi_area_abr")
    assert required <= set(result.checkpoints)


def test_lab16_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab16_udp_tcp_fundamentals")
    result = run_lab("lab16_udp_tcp_fundamentals")
    assert required <= set(result.checkpoints)


def test_lab17_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab17_bfd_for_liveness")
    result = run_lab("lab17_bfd_for_liveness")
    assert required <= set(result.checkpoints)


def test_lab18_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab18_acl_pipeline")
    result = run_lab("lab18_acl_pipeline")
    assert required <= set(result.checkpoints)


def test_lab19_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab19_nat44_stateful_translation")
    result = run_lab("lab19_nat44_stateful_translation")
    assert required <= set(result.checkpoints)


def test_lab20_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab20_qos_marking_and_queueing")
    result = run_lab("lab20_qos_marking_and_queueing")
    assert required <= set(result.checkpoints)


def test_lab21_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab21_bgp_session_fsm_and_transport")
    result = run_lab("lab21_bgp_session_fsm_and_transport")
    assert required <= set(result.checkpoints)


def test_lab22_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab22_bgp_attributes_and_bestpath")
    result = run_lab("lab22_bgp_attributes_and_bestpath")
    assert required <= set(result.checkpoints)


def test_lab23_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab23_bgp_policy_and_filters")
    result = run_lab("lab23_bgp_policy_and_filters")
    assert required <= set(result.checkpoints)


def test_lab24_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab24_bgp_scaling_patterns")
    result = run_lab("lab24_bgp_scaling_patterns")
    assert required <= set(result.checkpoints)


def test_lab25_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab25_tunnels_and_ipsec")
    result = run_lab("lab25_tunnels_and_ipsec")
    assert required <= set(result.checkpoints)


def test_lab26_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab26_observability_and_ops")
    result = run_lab("lab26_observability_and_ops")
    assert required <= set(result.checkpoints)


def test_lab27_meets_must_checkpoints() -> None:
    required = _feature_checkpoints_for_lab("lab27_capstone_incident_drill")
    result = run_lab("lab27_capstone_incident_drill")
    assert required <= set(result.checkpoints)
