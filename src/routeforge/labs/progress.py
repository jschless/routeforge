"""Persistent learner progress helpers."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from routeforge.labs.manifest import LABS, missing_prereqs

DEFAULT_PROGRESS_PATH = Path(".routeforge_progress.json")
CURRENT_VERSION = 1


@dataclass(frozen=True)
class ProgressState:
    version: int
    completed: tuple[str, ...]
    run_counts: dict[str, int]
    pass_counts: dict[str, int]
    last_result: dict[str, str]


def _empty_state() -> ProgressState:
    return ProgressState(
        version=CURRENT_VERSION,
        completed=(),
        run_counts={},
        pass_counts={},
        last_result={},
    )


def _to_str_tuple(value: Any, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list")
    out: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} entries must be strings")
        out.append(item)
    return tuple(out)


def _to_int_dict(value: Any, *, field_name: str) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping")
    out: dict[str, int] = {}
    for key, raw in value.items():
        if not isinstance(key, str):
            raise ValueError(f"{field_name} keys must be strings")
        if not isinstance(raw, int):
            raise ValueError(f"{field_name}[{key}] must be an int")
        out[key] = raw
    return out


def _to_str_dict(value: Any, *, field_name: str) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be a mapping")
    out: dict[str, str] = {}
    for key, raw in value.items():
        if not isinstance(key, str):
            raise ValueError(f"{field_name} keys must be strings")
        if not isinstance(raw, str):
            raise ValueError(f"{field_name}[{key}] must be a string")
        out[key] = raw
    return out


def load_progress(path: Path | None = None) -> ProgressState:
    progress_path = path or DEFAULT_PROGRESS_PATH
    if not progress_path.exists():
        return _empty_state()

    text = progress_path.read_text(encoding="utf-8")
    if not text.strip():
        return _empty_state()

    raw = json.loads(text)
    if not isinstance(raw, dict):
        raise ValueError("progress root must be a mapping")

    version = raw.get("version")
    if version is None:
        print(
            "warning: progress file has no version metadata; treating as legacy format. "
            "Run 'routeforge progress migrate' to upgrade."
        )
        return _empty_state()
    if not isinstance(version, int):
        raise ValueError("progress.version must be an int")
    if version < CURRENT_VERSION:
        print(
            f"warning: progress file version {version} is older than supported version {CURRENT_VERSION}. "
            "Run 'routeforge progress migrate' to attempt upgrade."
        )
        return _empty_state()
    if version > CURRENT_VERSION:
        raise ValueError(
            f"progress.version {version} is newer than this CLI supports ({CURRENT_VERSION})"
        )

    return ProgressState(
        version=version,
        completed=_to_str_tuple(raw.get("completed", []), field_name="progress.completed"),
        run_counts=_to_int_dict(raw.get("run_counts", {}), field_name="progress.run_counts"),
        pass_counts=_to_int_dict(raw.get("pass_counts", {}), field_name="progress.pass_counts"),
        last_result=_to_str_dict(raw.get("last_result", {}), field_name="progress.last_result"),
    )


def save_progress(state: ProgressState, path: Path | None = None) -> Path:
    progress_path = path or DEFAULT_PROGRESS_PATH
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": state.version,
        "completed": list(state.completed),
        "run_counts": state.run_counts,
        "pass_counts": state.pass_counts,
        "last_result": state.last_result,
    }
    with progress_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return progress_path


def _ordered_completed(completed: set[str]) -> tuple[str, ...]:
    ordered: list[str] = []
    for entry in LABS:
        if entry["id"] in completed:
            ordered.append(entry["id"])
    return tuple(ordered)


def mark_completed(state: ProgressState, lab_id: str) -> ProgressState:
    completed = set(state.completed)
    completed.add(lab_id)
    return ProgressState(
        version=state.version,
        completed=_ordered_completed(completed),
        run_counts=dict(state.run_counts),
        pass_counts=dict(state.pass_counts),
        last_result=dict(state.last_result),
    )


def clear_progress() -> ProgressState:
    return _empty_state()


def apply_run_result(state: ProgressState, *, lab_id: str, passed: bool) -> ProgressState:
    run_counts = dict(state.run_counts)
    run_counts[lab_id] = run_counts.get(lab_id, 0) + 1

    pass_counts = dict(state.pass_counts)
    if passed:
        pass_counts[lab_id] = pass_counts.get(lab_id, 0) + 1

    last_result = dict(state.last_result)
    last_result[lab_id] = "PASS" if passed else "FAIL"

    updated = ProgressState(
        version=state.version,
        completed=state.completed,
        run_counts=run_counts,
        pass_counts=pass_counts,
        last_result=last_result,
    )
    if passed:
        return mark_completed(updated, lab_id)
    return updated


def unlocked_labs(state: ProgressState) -> tuple[str, ...]:
    completed = set(state.completed)
    unlocked: list[str] = []
    for entry in LABS:
        lab_id = entry["id"]
        if lab_id in completed:
            continue
        if not missing_prereqs(lab_id, completed):
            unlocked.append(lab_id)
    return tuple(unlocked)


def migrate_progress(path: Path | None = None) -> Path:
    progress_path = path or DEFAULT_PROGRESS_PATH
    if not progress_path.exists():
        return save_progress(_empty_state(), progress_path)

    text = progress_path.read_text(encoding="utf-8")
    if not text.strip():
        return save_progress(_empty_state(), progress_path)

    raw = json.loads(text)
    if not isinstance(raw, dict):
        raise ValueError("progress root must be a mapping")

    migrated = ProgressState(
        version=CURRENT_VERSION,
        completed=_to_str_tuple(raw.get("completed", []), field_name="progress.completed"),
        run_counts=_to_int_dict(raw.get("run_counts", {}), field_name="progress.run_counts"),
        pass_counts=_to_int_dict(raw.get("pass_counts", {}), field_name="progress.pass_counts"),
        last_result=_to_str_dict(raw.get("last_result", {}), field_name="progress.last_result"),
    )
    return save_progress(migrated, progress_path)
