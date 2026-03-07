"""Student coding target map loader."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_TARGETS_PATH = Path(__file__).resolve().parents[3] / "labs" / "student_targets.yaml"


@dataclass(frozen=True)
class StudentTarget:
    lab_id: str
    stage: int
    path: str
    symbols: tuple[str, ...]
    summary: str


def _as_symbol_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    symbols: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} entries must be strings")
        normalized = item.strip()
        if not normalized:
            raise ValueError(f"{field_name} entries must not be empty")
        symbols.append(normalized)
    return tuple(symbols)


def load_student_targets(path: Path | None = None) -> dict[str, StudentTarget]:
    targets_path = path or DEFAULT_TARGETS_PATH
    with targets_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    if not isinstance(raw, dict):
        raise ValueError("student targets root must be a mapping")

    raw_targets = raw.get("targets", [])
    if not isinstance(raw_targets, list):
        raise ValueError("targets must be a list")

    targets_by_lab: dict[str, StudentTarget] = {}
    for item in raw_targets:
        if not isinstance(item, dict):
            raise ValueError("target entries must be mappings")
        lab_id = item.get("lab_id")
        stage = item.get("stage")
        source_path = item.get("path")
        summary = item.get("summary")
        if not isinstance(lab_id, str) or not lab_id:
            raise ValueError("target.lab_id must be a non-empty string")
        if not isinstance(stage, int) or stage <= 0:
            raise ValueError(f"target[{lab_id}].stage must be a positive int")
        if not isinstance(source_path, str) or not source_path:
            raise ValueError(f"target[{lab_id}].path must be a non-empty string")
        if not isinstance(summary, str) or not summary:
            raise ValueError(f"target[{lab_id}].summary must be a non-empty string")
        if lab_id in targets_by_lab:
            raise ValueError(f"duplicate target lab_id: {lab_id}")

        targets_by_lab[lab_id] = StudentTarget(
            lab_id=lab_id,
            stage=stage,
            path=source_path,
            symbols=_as_symbol_tuple(item.get("symbols"), f"target[{lab_id}].symbols"),
            summary=summary,
        )

    return targets_by_lab


def student_target_for_lab(lab_id: str, path: Path | None = None) -> StudentTarget | None:
    return load_student_targets(path).get(lab_id)
