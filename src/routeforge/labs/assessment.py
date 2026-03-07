"""Assessment rubric loading and learner scoring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from routeforge.labs.manifest import LABS
from routeforge.labs.progress import ProgressState

DEFAULT_RUBRIC_PATH = Path(__file__).resolve().parents[3] / "labs" / "assessment_rubric.yaml"


@dataclass(frozen=True)
class AssessmentBand:
    name: str
    min_score: float


@dataclass(frozen=True)
class LabRubric:
    lab_id: str
    weight: int
    category: str


@dataclass(frozen=True)
class AssessmentRubric:
    version: int
    profile: str
    as_of: str
    bands: tuple[AssessmentBand, ...]
    labs: dict[str, LabRubric]


@dataclass(frozen=True)
class LabAssessment:
    lab_id: str
    weight: int
    category: str
    mastery: float
    weighted_score: float
    run_count: int
    pass_count: int
    completed: bool


@dataclass(frozen=True)
class AssessmentResult:
    overall_score: float
    band: str
    total_weight: int
    weighted_earned: float
    lab_results: dict[str, LabAssessment]
    at_risk_labs: tuple[str, ...]


def _as_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping")
    return value


def load_assessment_rubric(path: Path | None = None) -> AssessmentRubric:
    rubric_path = path or DEFAULT_RUBRIC_PATH
    with rubric_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    root = _as_mapping(raw, "rubric")

    version = root.get("version")
    profile = root.get("profile")
    as_of = root.get("as_of")
    if not isinstance(version, int):
        raise ValueError("rubric.version must be an int")
    if not isinstance(profile, str):
        raise ValueError("rubric.profile must be a string")
    if not isinstance(as_of, str):
        raise ValueError("rubric.as_of must be a string")

    bands_raw = root.get("bands", [])
    if not isinstance(bands_raw, list) or not bands_raw:
        raise ValueError("rubric.bands must be a non-empty list")
    bands: list[AssessmentBand] = []
    for index, item in enumerate(bands_raw):
        band = _as_mapping(item, f"rubric.bands[{index}]")
        name = band.get("name")
        min_score = band.get("min_score")
        if not isinstance(name, str):
            raise ValueError(f"rubric.bands[{index}].name must be a string")
        if not isinstance(min_score, (int, float)):
            raise ValueError(f"rubric.bands[{index}].min_score must be numeric")
        bands.append(AssessmentBand(name=name, min_score=float(min_score)))
    ordered_bands = tuple(sorted(bands, key=lambda band: band.min_score))

    labs_raw = _as_mapping(root.get("labs", {}), "rubric.labs")
    labs: dict[str, LabRubric] = {}
    for lab_id, item in labs_raw.items():
        if not isinstance(lab_id, str):
            raise ValueError("rubric.labs keys must be strings")
        lab_map = _as_mapping(item, f"rubric.labs[{lab_id}]")
        weight = lab_map.get("weight")
        category = lab_map.get("category")
        if not isinstance(weight, int) or weight <= 0:
            raise ValueError(f"rubric.labs[{lab_id}].weight must be a positive int")
        if not isinstance(category, str):
            raise ValueError(f"rubric.labs[{lab_id}].category must be a string")
        labs[lab_id] = LabRubric(lab_id=lab_id, weight=weight, category=category)

    expected_labs = {entry["id"] for entry in LABS}
    missing = sorted(expected_labs - set(labs))
    if missing:
        raise ValueError(f"rubric missing labs: {', '.join(missing)}")

    return AssessmentRubric(
        version=version,
        profile=profile,
        as_of=as_of,
        bands=ordered_bands,
        labs=labs,
    )


def _band_for_score(score: float, *, bands: tuple[AssessmentBand, ...]) -> str:
    selected = "BELOW_PASS"
    for band in bands:
        if score >= band.min_score:
            selected = band.name
    return selected


def evaluate_assessment(state: ProgressState, rubric: AssessmentRubric) -> AssessmentResult:
    completed = set(state.completed)
    lab_results: dict[str, LabAssessment] = {}
    weighted_earned = 0.0
    total_weight = 0

    for entry in LABS:
        lab_id = entry["id"]
        lab_rubric = rubric.labs[lab_id]
        run_count = state.run_counts.get(lab_id, 0)
        pass_count = state.pass_counts.get(lab_id, 0)
        completed_flag = lab_id in completed
        if completed_flag:
            mastery = 1.0
        elif run_count > 0:
            mastery = pass_count / run_count
        else:
            mastery = 0.0

        weighted_score = lab_rubric.weight * mastery
        total_weight += lab_rubric.weight
        weighted_earned += weighted_score
        lab_results[lab_id] = LabAssessment(
            lab_id=lab_id,
            weight=lab_rubric.weight,
            category=lab_rubric.category,
            mastery=mastery,
            weighted_score=weighted_score,
            run_count=run_count,
            pass_count=pass_count,
            completed=completed_flag,
        )

    overall_score = 0.0 if total_weight == 0 else (100.0 * weighted_earned / total_weight)
    at_risk = sorted(
        (
            result
            for result in lab_results.values()
            if not result.completed and result.run_count > 0 and result.mastery < 0.7
        ),
        key=lambda result: (result.mastery, result.lab_id),
    )
    at_risk_labs = tuple(result.lab_id for result in at_risk[:5])

    return AssessmentResult(
        overall_score=overall_score,
        band=_band_for_score(overall_score, bands=rubric.bands),
        total_weight=total_weight,
        weighted_earned=weighted_earned,
        lab_results=lab_results,
        at_risk_labs=at_risk_labs,
    )
