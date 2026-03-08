from __future__ import annotations

from routeforge.labs.conformance import load_conformance_matrix
from routeforge.labs.exercises import LAB_RUNNERS, run_lab


def _feature_checkpoints_for_lab(lab_id: str) -> set[str]:
    matrix = load_conformance_matrix()
    coverage = matrix.coverage_for_lab(lab_id)
    assert coverage is not None, f"No conformance coverage entry for {lab_id}"
    checkpoints: set[str] = set()
    for feature_id in coverage.must:
        checkpoints.update(matrix.features_by_id[feature_id].checkpoints)
    return checkpoints


def _skip_if_not_implemented(lab_id: str) -> None:
    import pytest

    if lab_id not in LAB_RUNNERS:
        pytest.skip(f"{lab_id} scenario not yet implemented")


def test_lab28_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab28_dhcp_snooping_and_dai")
    required = _feature_checkpoints_for_lab("lab28_dhcp_snooping_and_dai")
    result = run_lab("lab28_dhcp_snooping_and_dai")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab28: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab28_dhcp_snooping_and_dai.md for the checkpoint guide."
    )


def test_lab29_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab29_port_security_and_ip_source_guard")
    required = _feature_checkpoints_for_lab("lab29_port_security_and_ip_source_guard")
    result = run_lab("lab29_port_security_and_ip_source_guard")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab29: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab29_port_security_and_ip_source_guard.md for the checkpoint guide."
    )


def test_lab30_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab30_qos_policing_and_shaping")
    required = _feature_checkpoints_for_lab("lab30_qos_policing_and_shaping")
    result = run_lab("lab30_qos_policing_and_shaping")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab30: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab30_qos_policing_and_shaping.md for the checkpoint guide."
    )


def test_lab31_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab31_qos_congestion_avoidance_wred")
    required = _feature_checkpoints_for_lab("lab31_qos_congestion_avoidance_wred")
    result = run_lab("lab31_qos_congestion_avoidance_wred")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab31: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab31_qos_congestion_avoidance_wred.md for the checkpoint guide."
    )


def test_lab32_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab32_route_redistribution_and_loop_prevention")
    required = _feature_checkpoints_for_lab("lab32_route_redistribution_and_loop_prevention")
    result = run_lab("lab32_route_redistribution_and_loop_prevention")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab32: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab32_route_redistribution_and_loop_prevention.md for the checkpoint guide."
    )


def test_lab33_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab33_fhrp_tracking_and_failover")
    required = _feature_checkpoints_for_lab("lab33_fhrp_tracking_and_failover")
    result = run_lab("lab33_fhrp_tracking_and_failover")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab33: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab33_fhrp_tracking_and_failover.md for the checkpoint guide."
    )


def test_lab34_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab34_ipv6_nd_slaac_and_ra_guard")
    required = _feature_checkpoints_for_lab("lab34_ipv6_nd_slaac_and_ra_guard")
    result = run_lab("lab34_ipv6_nd_slaac_and_ra_guard")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab34: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab34_ipv6_nd_slaac_and_ra_guard.md for the checkpoint guide."
    )


def test_lab35_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab35_ospfv3_adjacency_and_lsdb")
    required = _feature_checkpoints_for_lab("lab35_ospfv3_adjacency_and_lsdb")
    result = run_lab("lab35_ospfv3_adjacency_and_lsdb")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab35: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab35_ospfv3_adjacency_and_lsdb.md for the checkpoint guide."
    )


def test_lab36_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab36_mpbgp_ipv6_unicast")
    required = _feature_checkpoints_for_lab("lab36_mpbgp_ipv6_unicast")
    result = run_lab("lab36_mpbgp_ipv6_unicast")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab36: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab36_mpbgp_ipv6_unicast.md for the checkpoint guide."
    )


def test_lab37_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab37_mpls_ldp_label_forwarding")
    required = _feature_checkpoints_for_lab("lab37_mpls_ldp_label_forwarding")
    result = run_lab("lab37_mpls_ldp_label_forwarding")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab37: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab37_mpls_ldp_label_forwarding.md for the checkpoint guide."
    )


def test_lab38_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab38_l3vpn_vrf_and_route_targets")
    required = _feature_checkpoints_for_lab("lab38_l3vpn_vrf_and_route_targets")
    result = run_lab("lab38_l3vpn_vrf_and_route_targets")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab38: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab38_l3vpn_vrf_and_route_targets.md for the checkpoint guide."
    )


def test_lab39_meets_must_checkpoints() -> None:
    _skip_if_not_implemented("lab39_bgp_evpn_vxlan_basics")
    required = _feature_checkpoints_for_lab("lab39_bgp_evpn_vxlan_basics")
    result = run_lab("lab39_bgp_evpn_vxlan_basics")
    missing = required - set(result.checkpoints)
    assert not missing, (
        f"Lab lab39: required checkpoints not reached: {sorted(missing)}. "
        "See docs/tutorial/lab39_bgp_evpn_vxlan_basics.md for the checkpoint guide."
    )
