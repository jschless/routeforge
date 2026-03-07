from __future__ import annotations

import pytest

from routeforge.labs.conformance import load_conformance_matrix
from routeforge.labs.exercises import run_lab
from routeforge.labs.manifest import LABS
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


@pytest.mark.parametrize(
    ("stage", "lab_id"),
    [
        pytest.param(index, entry["id"], marks=pytest.mark.stage(index), id=f"stage{index:02d}_{entry['id']}")
        for index, entry in enumerate(LABS, start=1)
    ],
)
def test_stage_lab(stage: int, lab_id: str) -> None:
    _assert_stage_lab(lab_id)
