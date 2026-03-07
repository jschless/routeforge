from __future__ import annotations

from routeforge.labs.conformance import load_conformance_matrix


def test_matrix_loads_and_exposes_features() -> None:
    matrix = load_conformance_matrix()
    feature = matrix.features_by_id["L2_FRAME_VALIDATION"]

    assert matrix.version == 1
    assert matrix.profile == "ccnp_v1"
    assert feature.level == "MUST"
    assert "lab01_frame_and_headers" in feature.labs


def test_matrix_coverage_lookup_for_lab() -> None:
    matrix = load_conformance_matrix()
    coverage = matrix.coverage_for_lab("lab02_mac_learning_switch")

    assert coverage is not None
    assert coverage.must == ("L2_MAC_LEARN_FWD",)
    assert coverage.out == ("IPV6_STACK",)
