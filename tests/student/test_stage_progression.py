from __future__ import annotations

import pytest

from routeforge.labs.conformance import load_conformance_matrix
from routeforge.labs.exercises import run_lab
from routeforge.model.packet import ETHERTYPE_IPV4, EthernetFrame, IPv4Header, is_valid_mac


def _required_checkpoints_for_lab(lab_id: str) -> set[str]:
    matrix = load_conformance_matrix()
    coverage = matrix.coverage_for_lab(lab_id)
    assert coverage is not None
    required: set[str] = set()
    for feature_id in coverage.must:
        required.update(matrix.features_by_id[feature_id].checkpoints)
    return required


def _assert_stage_lab(lab_id: str) -> None:
    result = run_lab(lab_id)
    assert result.passed is True
    assert _required_checkpoints_for_lab(lab_id) <= set(result.checkpoints)


@pytest.mark.stage(1)
def test_stage01_edge_mac_and_ipv4_validation() -> None:
    assert is_valid_mac("aa:bb:cc:dd:ee:ff") is True
    assert is_valid_mac("AA:BB:CC:DD:EE:FF") is True
    assert is_valid_mac("zz:bb:cc:dd:ee:ff") is False

    valid = EthernetFrame(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.1", dst_ip="192.0.2.2", ttl=64),
    )
    assert valid.validate() == []

    invalid = EthernetFrame(
        src_mac="00:11:22:33:44:55",
        dst_mac="00:11:22:33:44:66",
        ethertype=ETHERTYPE_IPV4,
        payload=IPv4Header(src_ip="192.0.2.1", dst_ip="999.0.2.2", ttl=0),
    )
    errors = invalid.validate()
    assert "L3_INVALID_DST_IP" in errors
    assert "L3_INVALID_TTL" in errors


@pytest.mark.stage(1)
def test_stage01_lab01() -> None:
    _assert_stage_lab("lab01_frame_and_headers")


@pytest.mark.stage(2)
def test_stage02_lab02() -> None:
    _assert_stage_lab("lab02_mac_learning_switch")


@pytest.mark.stage(3)
def test_stage03_lab03() -> None:
    _assert_stage_lab("lab03_vlan_and_trunks")


@pytest.mark.stage(4)
def test_stage04_lab04() -> None:
    _assert_stage_lab("lab04_stp")


@pytest.mark.stage(5)
def test_stage05_lab05() -> None:
    _assert_stage_lab("lab05_stp_convergence_and_protection")


@pytest.mark.stage(6)
def test_stage06_lab06() -> None:
    _assert_stage_lab("lab06_arp_and_adjacency")


@pytest.mark.stage(7)
def test_stage07_lab07() -> None:
    _assert_stage_lab("lab07_ipv4_subnet_and_rib")


@pytest.mark.stage(8)
def test_stage08_lab08() -> None:
    _assert_stage_lab("lab08_fib_forwarding_pipeline")


@pytest.mark.stage(9)
def test_stage09_lab09() -> None:
    _assert_stage_lab("lab09_icmp_and_control_responses")


@pytest.mark.stage(10)
def test_stage10_lab10() -> None:
    _assert_stage_lab("lab10_ipv4_control_plane_diagnostics")


@pytest.mark.stage(11)
def test_stage11_lab11() -> None:
    _assert_stage_lab("lab11_ospf_adjacency_fsm")


@pytest.mark.stage(12)
def test_stage12_lab12() -> None:
    _assert_stage_lab("lab12_ospf_network_types_and_dr_bdr")


@pytest.mark.stage(13)
def test_stage13_lab13() -> None:
    _assert_stage_lab("lab13_ospf_lsa_flooding_and_lsdb")


@pytest.mark.stage(14)
def test_stage14_lab14() -> None:
    _assert_stage_lab("lab14_ospf_spf_and_route_install")


@pytest.mark.stage(15)
def test_stage15_lab15() -> None:
    _assert_stage_lab("lab15_ospf_multi_area_abr")


@pytest.mark.stage(16)
def test_stage16_lab16() -> None:
    _assert_stage_lab("lab16_udp_tcp_fundamentals")


@pytest.mark.stage(17)
def test_stage17_lab17() -> None:
    _assert_stage_lab("lab17_bfd_for_liveness")


@pytest.mark.stage(18)
def test_stage18_lab18() -> None:
    _assert_stage_lab("lab18_acl_pipeline")


@pytest.mark.stage(19)
def test_stage19_lab19() -> None:
    _assert_stage_lab("lab19_nat44_stateful_translation")


@pytest.mark.stage(20)
def test_stage20_lab20() -> None:
    _assert_stage_lab("lab20_qos_marking_and_queueing")


@pytest.mark.stage(21)
def test_stage21_lab21() -> None:
    _assert_stage_lab("lab21_bgp_session_fsm_and_transport")


@pytest.mark.stage(22)
def test_stage22_lab22() -> None:
    _assert_stage_lab("lab22_bgp_attributes_and_bestpath")


@pytest.mark.stage(23)
def test_stage23_lab23() -> None:
    _assert_stage_lab("lab23_bgp_policy_and_filters")


@pytest.mark.stage(24)
def test_stage24_lab24() -> None:
    _assert_stage_lab("lab24_bgp_scaling_patterns")


@pytest.mark.stage(25)
def test_stage25_lab25() -> None:
    _assert_stage_lab("lab25_tunnels_and_ipsec")


@pytest.mark.stage(26)
def test_stage26_lab26() -> None:
    _assert_stage_lab("lab26_observability_and_ops")


@pytest.mark.stage(27)
def test_stage27_lab27() -> None:
    _assert_stage_lab("lab27_capstone_incident_drill")
