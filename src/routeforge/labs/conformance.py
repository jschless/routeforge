"""Conformance matrix loader and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from routeforge.labs.manifest import LABS

DEFAULT_MATRIX_PATH = Path(__file__).resolve().parents[3] / "labs" / "conformance_matrix.yaml"
VALID_LEVELS = {"MUST", "SHOULD", "OUT"}
VALID_DOMAINS = {
    "L2",
    "L3",
    "L4",
    "OSPF",
    "BGP",
    "BFD",
    "POLICY",
    "SERVICE",
    "MGMT",
    "CAPSTONE",
    "GLOBAL",
    "SECURITY",
    "QOS",
    "ROUTING",
    "IPV6",
    "MPLS",
    "EVPN",
}


@dataclass(frozen=True)
class ConformanceFeature:
    id: str
    domain: str
    level: str
    description: str
    labs: tuple[str, ...]
    tests: tuple[str, ...]
    checkpoints: tuple[str, ...]


@dataclass(frozen=True)
class LabCoverage:
    must: tuple[str, ...]
    should: tuple[str, ...]
    out: tuple[str, ...]


@dataclass(frozen=True)
class ConformanceMatrix:
    version: int
    profile: str
    as_of: str
    features_by_id: dict[str, ConformanceFeature]
    lab_coverage: dict[str, LabCoverage]

    def coverage_for_lab(self, lab_id: str) -> LabCoverage | None:
        return self.lab_coverage.get(lab_id)


def _as_str_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} entries must be strings")
        normalized.append(item)
    return tuple(normalized)


def load_conformance_matrix(path: Path | None = None) -> ConformanceMatrix:
    matrix_path = path or DEFAULT_MATRIX_PATH
    with matrix_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, dict):
        raise ValueError("conformance matrix root must be a mapping")

    version = raw.get("version")
    profile = raw.get("profile")
    as_of = raw.get("as_of")

    if not isinstance(version, int):
        raise ValueError("version must be an int")
    if not isinstance(profile, str):
        raise ValueError("profile must be a string")
    if not isinstance(as_of, str):
        raise ValueError("as_of must be a string")

    features_raw = raw.get("features", [])
    if not isinstance(features_raw, list):
        raise ValueError("features must be a list")

    features_by_id: dict[str, ConformanceFeature] = {}
    for item in features_raw:
        if not isinstance(item, dict):
            raise ValueError("feature entries must be mappings")
        feature_id = item.get("id")
        if not isinstance(feature_id, str):
            raise ValueError("feature.id must be a string")
        if feature_id in features_by_id:
            raise ValueError(f"duplicate feature.id: {feature_id}")

        domain = item.get("domain")
        level = item.get("level")
        description = item.get("description")
        if not isinstance(domain, str) or domain not in VALID_DOMAINS:
            raise ValueError(f"feature[{feature_id}].domain must be one of: {', '.join(sorted(VALID_DOMAINS))}")
        if not isinstance(level, str) or level not in VALID_LEVELS:
            raise ValueError(f"feature[{feature_id}].level must be one of: {', '.join(sorted(VALID_LEVELS))}")
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f"feature[{feature_id}].description must be a non-empty string")

        feature = ConformanceFeature(
            id=feature_id,
            domain=domain,
            level=level,
            description=description.strip(),
            labs=_as_str_tuple(item.get("labs", []), f"feature[{feature_id}].labs"),
            tests=_as_str_tuple(item.get("tests", []), f"feature[{feature_id}].tests"),
            checkpoints=_as_str_tuple(item.get("checkpoints", []), f"feature[{feature_id}].checkpoints"),
        )
        unknown_labs = [lab_id for lab_id in feature.labs if lab_id not in {entry["id"] for entry in LABS}]
        if unknown_labs:
            unknown = ", ".join(sorted(unknown_labs))
            raise ValueError(f"feature[{feature_id}].labs includes unknown lab ids: {unknown}")
        features_by_id[feature.id] = feature

    lab_coverage_raw = raw.get("lab_coverage", {})
    if not isinstance(lab_coverage_raw, dict):
        raise ValueError("lab_coverage must be a mapping")

    lab_coverage: dict[str, LabCoverage] = {}
    for lab_id, coverage in lab_coverage_raw.items():
        if not isinstance(lab_id, str):
            raise ValueError("lab_coverage keys must be strings")
        if lab_id not in {entry["id"] for entry in LABS}:
            raise ValueError(f"lab_coverage includes unknown lab id: {lab_id}")
        if not isinstance(coverage, dict):
            raise ValueError(f"lab_coverage[{lab_id}] must be a mapping")
        must = _as_str_tuple(coverage.get("must", []), f"lab_coverage[{lab_id}].must")
        should = _as_str_tuple(coverage.get("should", []), f"lab_coverage[{lab_id}].should")
        out = _as_str_tuple(coverage.get("out", []), f"lab_coverage[{lab_id}].out")
        for feature_id in (*must, *should, *out):
            if feature_id not in features_by_id:
                raise ValueError(f"lab_coverage[{lab_id}] references unknown feature id: {feature_id}")
        lab_coverage[lab_id] = LabCoverage(must=must, should=should, out=out)

    missing_labs = sorted({entry["id"] for entry in LABS} - set(lab_coverage))
    if missing_labs:
        raise ValueError(f"lab_coverage missing labs: {', '.join(missing_labs)}")

    return ConformanceMatrix(
        version=version,
        profile=profile,
        as_of=as_of,
        features_by_id=features_by_id,
        lab_coverage=lab_coverage,
    )
