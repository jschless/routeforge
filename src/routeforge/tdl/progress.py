"""Persistent progress helpers for TDL side-quest track."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

from routeforge.tdl.manifest import TDL_CHALLENGES, get_tdl_challenge, tdl_missing_prereqs

DEFAULT_TDL_PROGRESS_PATH = Path.home() / ".routeforge_tdl_progress.json"
LEGACY_TDL_PROGRESS_PATH = Path(".routeforge_tdl_progress.json")
CURRENT_VERSION = 1


@dataclass(frozen=True)
class TdlProgressState:
    version: int
    completed: tuple[str, ...]
    total_xp: int
    badges: tuple[str, ...]
    run_counts: dict[str, int]
    pass_counts: dict[str, int]
    last_result: dict[str, str]


def _empty_state() -> TdlProgressState:
    return TdlProgressState(
        version=CURRENT_VERSION,
        completed=(),
        total_xp=0,
        badges=(),
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


def _load_tdl_progress_state(raw: dict[str, Any]) -> TdlProgressState:
    return TdlProgressState(
        version=CURRENT_VERSION,
        completed=_to_str_tuple(raw.get("completed", []), field_name="tdl.completed"),
        total_xp=int(raw.get("total_xp", 0)),
        badges=_to_str_tuple(raw.get("badges", []), field_name="tdl.badges"),
        run_counts=_to_int_dict(raw.get("run_counts", {}), field_name="tdl.run_counts"),
        pass_counts=_to_int_dict(raw.get("pass_counts", {}), field_name="tdl.pass_counts"),
        last_result=_to_str_dict(raw.get("last_result", {}), field_name="tdl.last_result"),
    )


def load_tdl_progress(path: Path | None = None) -> TdlProgressState:
    progress_path = path or DEFAULT_TDL_PROGRESS_PATH
    if not progress_path.exists():
        return _empty_state()

    text = progress_path.read_text(encoding="utf-8")
    if not text.strip():
        return _empty_state()

    raw = json.loads(text)
    if not isinstance(raw, dict):
        raise ValueError("tdl progress root must be a mapping")

    version = raw.get("version")
    if version is None:
        print(
            "warning: tdl progress file has no version metadata; loaded legacy state and will "
            "upgrade it to the current format on next save. "
            "Run 'routeforge tdl progress migrate' to rewrite it now."
        )
        return _load_tdl_progress_state(raw)
    if not isinstance(version, int):
        raise ValueError("tdl progress.version must be an int")
    if version < CURRENT_VERSION:
        print(
            f"warning: tdl progress file version {version} is older than supported version {CURRENT_VERSION}; "
            "loaded legacy state and will upgrade it to the current format on next save. "
            "Run 'routeforge tdl progress migrate' to rewrite it now."
        )
        return _load_tdl_progress_state(raw)
    if version > CURRENT_VERSION:
        raise ValueError(
            f"tdl progress.version {version} is newer than this CLI supports ({CURRENT_VERSION})"
        )
    return _load_tdl_progress_state(raw)


def save_tdl_progress(state: TdlProgressState, path: Path | None = None) -> Path:
    progress_path = path or DEFAULT_TDL_PROGRESS_PATH
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": state.version,
        "completed": list(state.completed),
        "total_xp": state.total_xp,
        "badges": list(state.badges),
        "run_counts": state.run_counts,
        "pass_counts": state.pass_counts,
        "last_result": state.last_result,
    }
    with progress_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return progress_path


def clear_tdl_progress() -> TdlProgressState:
    return _empty_state()


def _ordered_completed(completed: set[str]) -> tuple[str, ...]:
    ordered: list[str] = []
    for entry in TDL_CHALLENGES:
        challenge_id = entry["id"]
        if challenge_id in completed:
            ordered.append(challenge_id)
    return tuple(ordered)


def _badge_set(completed: set[str]) -> tuple[str, ...]:
    missions_by_domain: dict[str, set[str]] = {}
    for entry in TDL_CHALLENGES:
        if entry["kind"] != "mission":
            continue
        domain = entry["domain"]
        missions_by_domain.setdefault(domain, set()).add(entry["id"])

    all_ids = {entry["id"] for entry in TDL_CHALLENGES}
    badges: list[str] = []
    for domain in sorted(missions_by_domain):
        mission_ids = missions_by_domain[domain]
        if mission_ids <= completed:
            badges.append(f"{domain.lower()}_complete")
    if all_ids <= completed:
        badges.append("tdl_master")
    return tuple(badges)


def _xp_total(completed: set[str]) -> int:
    return sum(entry["xp"] for entry in TDL_CHALLENGES if entry["id"] in completed)


def apply_tdl_run_result(state: TdlProgressState, *, challenge_id: str, passed: bool) -> TdlProgressState:
    if get_tdl_challenge(challenge_id) is None:
        raise KeyError(f"unknown tdl challenge: {challenge_id}")

    run_counts = dict(state.run_counts)
    run_counts[challenge_id] = run_counts.get(challenge_id, 0) + 1

    pass_counts = dict(state.pass_counts)
    if passed:
        pass_counts[challenge_id] = pass_counts.get(challenge_id, 0) + 1

    last_result = dict(state.last_result)
    last_result[challenge_id] = "PASS" if passed else "FAIL"

    completed = set(state.completed)
    if passed:
        completed.add(challenge_id)

    ordered_completed = _ordered_completed(completed)
    badges = _badge_set(completed)
    total_xp = _xp_total(completed)

    return TdlProgressState(
        version=state.version,
        completed=ordered_completed,
        total_xp=total_xp,
        badges=badges,
        run_counts=run_counts,
        pass_counts=pass_counts,
        last_result=last_result,
    )


def unlocked_tdl_challenges(state: TdlProgressState) -> tuple[str, ...]:
    completed = set(state.completed)
    unlocked: list[str] = []
    for entry in TDL_CHALLENGES:
        challenge_id = entry["id"]
        if challenge_id in completed:
            continue
        if not tdl_missing_prereqs(challenge_id, completed):
            unlocked.append(challenge_id)
    return tuple(unlocked)


def migrate_tdl_progress(path: Path | None = None) -> Path:
    progress_path = path or DEFAULT_TDL_PROGRESS_PATH
    if not progress_path.exists():
        return save_tdl_progress(_empty_state(), progress_path)

    text = progress_path.read_text(encoding="utf-8")
    if not text.strip():
        return save_tdl_progress(_empty_state(), progress_path)

    raw = json.loads(text)
    if not isinstance(raw, dict):
        raise ValueError("tdl progress root must be a mapping")
    if isinstance(raw.get("version"), int) and raw["version"] > CURRENT_VERSION:
        raise ValueError(
            f"tdl progress.version {raw['version']} is newer than this CLI supports ({CURRENT_VERSION})"
        )
    return save_tdl_progress(_load_tdl_progress_state(raw), progress_path)
