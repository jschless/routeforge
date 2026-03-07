"""RouteForge CLI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from routeforge.debug.replay import explain_lines, load_trace, replay_lines
from routeforge.labs.assessment import evaluate_assessment, load_assessment_rubric
from routeforge.labs.conformance import load_conformance_matrix
from routeforge.labs.exercises import LAB_RUNNERS, run_lab
from routeforge.labs.manifest import LABS, get_lab, missing_prereqs
from routeforge.labs.student_checks import run_staged_student_checks
from routeforge.labs.student_targets import signatures_for_target, student_target_for_lab
from routeforge.labs.progress import (
    DEFAULT_PROGRESS_PATH,
    ProgressState,
    apply_run_result,
    clear_progress,
    load_progress,
    mark_completed,
    save_progress,
    unlocked_labs,
)
from routeforge.tdl.checks import run_tdl_checks
from routeforge.tdl.exercises import run_tdl_challenge
from routeforge.tdl.manifest import TDL_CHALLENGES, get_tdl_challenge, tdl_missing_prereqs
from routeforge.tdl.progress import (
    DEFAULT_TDL_PROGRESS_PATH,
    TdlProgressState,
    apply_tdl_run_result,
    clear_tdl_progress,
    load_tdl_progress,
    save_tdl_progress,
    unlocked_tdl_challenges,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="routeforge")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("labs", help="List ordered labs")

    show = sub.add_parser("show", help="Show one lab entry")
    show.add_argument("lab_id")

    run = sub.add_parser("run", help="Run one lab (with prerequisite gate)")
    run.add_argument("lab_id")
    run.add_argument(
        "--completed",
        action="append",
        default=[],
        help="Completed lab IDs. Repeat the flag or pass comma-separated values.",
    )
    run.add_argument("--trace-out", type=Path, default=None, help="Write JSONL trace output for the lab run")
    run.add_argument("--state-file", type=Path, default=None, help="Optional progress state file to update")

    check = sub.add_parser("check", help="Run staged student tests up to one lab or all labs")
    check.add_argument("target", help="Lab stage target (for example: lab01, lab01_frame_and_headers, or all)")

    progress = sub.add_parser("progress", help="Show and manage learner progress")
    progress_sub = progress.add_subparsers(dest="progress_command", required=True)

    progress_show = progress_sub.add_parser("show", help="Show progress summary")
    progress_show.add_argument("--state-file", type=Path, default=None)

    progress_mark = progress_sub.add_parser("mark", help="Mark one lab complete in progress state")
    progress_mark.add_argument("lab_id")
    progress_mark.add_argument("--state-file", type=Path, default=None)

    progress_reset = progress_sub.add_parser("reset", help="Reset progress state")
    progress_reset.add_argument("--state-file", type=Path, default=None)

    tdl = sub.add_parser("tdl", help="Run TDL side-quest challenges")
    tdl_sub = tdl.add_subparsers(dest="tdl_command", required=True)

    tdl_list = tdl_sub.add_parser("list", help="List TDL challenges and unlock status")
    tdl_list.add_argument("--state-file", type=Path, default=None)

    tdl_show = tdl_sub.add_parser("show", help="Show one TDL challenge")
    tdl_show.add_argument("challenge_id")

    tdl_check = tdl_sub.add_parser("check", help="Run TDL pytest checks for one challenge or all")
    tdl_check.add_argument("target", help="TDL challenge ID or 'all'")

    tdl_run = tdl_sub.add_parser("run", help="Run one TDL challenge scenario")
    tdl_run.add_argument("challenge_id")
    tdl_run.add_argument("--state-file", type=Path, default=None, help="Optional TDL progress state file to update")

    tdl_progress = tdl_sub.add_parser("progress", help="Show and manage TDL progress")
    tdl_progress_sub = tdl_progress.add_subparsers(dest="tdl_progress_command", required=True)

    tdl_progress_show = tdl_progress_sub.add_parser("show", help="Show TDL progress summary")
    tdl_progress_show.add_argument("--state-file", type=Path, default=None)

    tdl_progress_reset = tdl_progress_sub.add_parser("reset", help="Reset TDL progress state")
    tdl_progress_reset.add_argument("--state-file", type=Path, default=None)

    report = sub.add_parser("report", help="Generate learner readiness report")
    report.add_argument("--state-file", type=Path, default=None)
    report.add_argument("--rubric-file", type=Path, default=None, help="Optional assessment rubric YAML path")
    report.add_argument("--json-out", type=Path, default=None, help="Optional JSON report output path")

    debug = sub.add_parser("debug", help="Replay and explain trace files")
    debug_sub = debug.add_subparsers(dest="debug_command", required=True)

    replay = debug_sub.add_parser("replay", help="Replay trace records in sequence order")
    replay.add_argument("--trace", type=Path, required=True)

    explain = debug_sub.add_parser("explain", help="Explain one step or summarize full trace")
    explain.add_argument("--trace", type=Path, required=True)
    explain.add_argument("--step", default=None, help="Optional step name to explain")

    return parser


def _cmd_labs() -> int:
    for entry in LABS:
        print(f"{entry['id']}: {entry['title']}")
    return 0


def _cmd_show(lab_id: str) -> int:
    entry = get_lab(lab_id)
    if entry is not None:
        print(f"id: {entry['id']}")
        print(f"title: {entry['title']}")
        prereqs = ", ".join(entry["prereqs"]) if entry["prereqs"] else "none"
        print(f"prereqs: {prereqs}")
        matrix = load_conformance_matrix()
        coverage = matrix.coverage_for_lab(lab_id)
        if coverage is None:
            print("conformance.must: none")
            print("conformance.should: none")
            print("conformance.out: none")
        else:
            must = ", ".join(coverage.must) if coverage.must else "none"
            should = ", ".join(coverage.should) if coverage.should else "none"
            out = ", ".join(coverage.out) if coverage.out else "none"
            print(f"conformance.must: {must}")
            print(f"conformance.should: {should}")
            print(f"conformance.out: {out}")
        student_target = student_target_for_lab(lab_id)
        if student_target is None:
            print("student.target: none")
        else:
            symbols = ", ".join(student_target.symbols)
            signatures = " || ".join(signatures_for_target(student_target))
            print(f"student.stage: {student_target.stage}")
            print(f"student.target: {student_target.path}")
            print(f"student.symbols: {symbols}")
            print(f"student.signatures: {signatures}")
            print(f"student.summary: {student_target.summary}")
        return 0
    print(f"unknown lab: {lab_id}")
    return 1


def _parse_completed(values: list[str]) -> set[str]:
    completed: set[str] = set()
    for value in values:
        for item in value.split(","):
            normalized = item.strip()
            if normalized:
                completed.add(normalized)
    return completed


def _resolve_state_file(path: Path | None) -> Path:
    return path or DEFAULT_PROGRESS_PATH


def _cmd_run(lab_id: str, completed_values: list[str], trace_out: Path | None, state_file: Path | None) -> int:
    entry = get_lab(lab_id)
    if entry is None:
        print(f"unknown lab: {lab_id}")
        return 1

    state_path: Path | None = None
    progress_state: ProgressState | None = None
    if state_file is not None:
        state_path = _resolve_state_file(state_file)
        try:
            progress_state = load_progress(state_path)
        except (OSError, ValueError) as exc:
            print(f"failed to load progress: {exc}")
            return 1

    completed = _parse_completed(completed_values)
    if progress_state is not None:
        completed.update(progress_state.completed)
    unmet = missing_prereqs(lab_id, completed)
    if unmet:
        unmet_text = ", ".join(unmet)
        print(f"blocked: {lab_id} has unmet prerequisites: {unmet_text}")
        return 2

    if lab_id not in LAB_RUNNERS:
        implemented = ", ".join(sorted(LAB_RUNNERS))
        print(f"lab implementation not available yet: {lab_id}")
        print(f"currently implemented: {implemented}")
        return 3

    result = run_lab(lab_id)
    if trace_out is not None:
        trace_out.parent.mkdir(parents=True, exist_ok=True)
        with trace_out.open("w", encoding="utf-8") as handle:
            for record in result.trace_records:
                handle.write(json.dumps(record, sort_keys=True))
                handle.write("\n")
        print(f"trace written: {trace_out}")

    print(f"running lab: {lab_id}")
    for step in result.steps:
        status = "PASS" if step.passed else "FAIL"
        print(f"[{status}] {step.name}: {step.detail}")

    checkpoints = ", ".join(result.checkpoints) if result.checkpoints else "none"
    print(f"checkpoints: {checkpoints}")
    code = 0 if result.passed else 4

    if state_path is not None and progress_state is not None:
        try:
            updated = apply_run_result(progress_state, lab_id=lab_id, passed=result.passed)
            saved = save_progress(updated, state_path)
            print(f"progress updated: {saved}")
        except (OSError, ValueError) as exc:
            print(f"failed to update progress: {exc}")
            return 1

    return code


def _cmd_progress_show(state_file: Path | None) -> int:
    state_path = _resolve_state_file(state_file)
    try:
        state = load_progress(state_path)
    except (OSError, ValueError) as exc:
        print(f"failed to load progress: {exc}")
        return 1

    completed_count = len(state.completed)
    total_labs = len(LABS)
    unlocked = unlocked_labs(state)
    completed_text = ", ".join(state.completed) if state.completed else "none"
    unlocked_text = ", ".join(unlocked) if unlocked else "none"

    print(f"progress.file: {state_path}")
    print(f"labs.completed: {completed_count}/{total_labs}")
    print(f"labs.completed.list: {completed_text}")
    print(f"labs.unlocked: {unlocked_text}")
    return 0


def _cmd_progress_mark(lab_id: str, state_file: Path | None) -> int:
    if get_lab(lab_id) is None:
        print(f"unknown lab: {lab_id}")
        return 1

    state_path = _resolve_state_file(state_file)
    try:
        state = load_progress(state_path)
        updated = mark_completed(state, lab_id)
        save_progress(updated, state_path)
    except (OSError, ValueError) as exc:
        print(f"failed to update progress: {exc}")
        return 1

    print(f"marked complete: {lab_id}")
    print(f"progress updated: {state_path}")
    return 0


def _cmd_progress_reset(state_file: Path | None) -> int:
    state_path = _resolve_state_file(state_file)
    try:
        save_progress(clear_progress(), state_path)
    except OSError as exc:
        print(f"failed to reset progress: {exc}")
        return 1
    print(f"progress reset: {state_path}")
    return 0


def _resolve_tdl_state_file(path: Path | None) -> Path:
    return path or DEFAULT_TDL_PROGRESS_PATH


def _cmd_tdl_list(state_file: Path | None) -> int:
    state_path = _resolve_tdl_state_file(state_file)
    try:
        state = load_tdl_progress(state_path)
    except (OSError, ValueError) as exc:
        print(f"failed to load tdl progress: {exc}")
        return 1

    completed = set(state.completed)
    unlocked = set(unlocked_tdl_challenges(state))
    for entry in TDL_CHALLENGES:
        challenge_id = entry["id"]
        if challenge_id in completed:
            status = "DONE"
        elif challenge_id in unlocked:
            status = "UNLOCKED"
        else:
            status = "LOCKED"
        print(
            f"{challenge_id}: {entry['title']} "
            f"[{entry['domain']}/{entry['kind']}] status={status} xp={entry['xp']}"
        )
    return 0


def _cmd_tdl_show(challenge_id: str) -> int:
    entry = get_tdl_challenge(challenge_id)
    if entry is None:
        print(f"unknown tdl challenge: {challenge_id}")
        return 1
    prereqs = ", ".join(entry["prereqs"]) if entry["prereqs"] else "none"
    symbols = ", ".join(entry["symbols"])
    print(f"id: {entry['id']}")
    print(f"title: {entry['title']}")
    print(f"domain: {entry['domain']}")
    print(f"kind: {entry['kind']}")
    print(f"prereqs: {prereqs}")
    print(f"xp: {entry['xp']}")
    print(f"tdl.target: {entry['path']}")
    print(f"tdl.symbols: {symbols}")
    print(f"tdl.summary: {entry['summary']}")
    return 0


def _cmd_tdl_check(target: str) -> int:
    normalized = target.strip()
    if not normalized:
        print("unknown tdl check target: empty")
        print("valid examples: tdl_auto_01_yang_path_validation, all")
        return 1
    if normalized.lower() != "all" and get_tdl_challenge(normalized) is None:
        print(f"unknown tdl check target: {target}")
        print("valid examples: tdl_auto_01_yang_path_validation, all")
        return 1
    repo_root = Path(__file__).resolve().parents[2]
    print(f"running tdl checks: target={normalized}")
    return run_tdl_checks(target=normalized, repo_root=repo_root)


def _cmd_tdl_run(challenge_id: str, state_file: Path | None) -> int:
    entry = get_tdl_challenge(challenge_id)
    if entry is None:
        print(f"unknown tdl challenge: {challenge_id}")
        return 1

    state_path = _resolve_tdl_state_file(state_file)
    try:
        progress_state: TdlProgressState = load_tdl_progress(state_path)
    except (OSError, ValueError) as exc:
        print(f"failed to load tdl progress: {exc}")
        return 1

    completed = set(progress_state.completed)
    unmet = tdl_missing_prereqs(challenge_id, completed)
    if unmet:
        print(f"blocked: {challenge_id} has unmet prerequisites: {', '.join(unmet)}")
        return 2

    try:
        result = run_tdl_challenge(challenge_id)
    except NotImplementedError as exc:
        print(f"challenge implementation missing: {exc}")
        return 4
    print(f"running tdl challenge: {challenge_id}")
    for step in result.steps:
        status = "PASS" if step.passed else "FAIL"
        print(f"[{status}] {step.name}: {step.detail}")

    checkpoints = ", ".join(result.checkpoints) if result.checkpoints else "none"
    print(f"checkpoints: {checkpoints}")
    code = 0 if result.passed else 4

    try:
        updated = apply_tdl_run_result(progress_state, challenge_id=challenge_id, passed=result.passed)
        saved = save_tdl_progress(updated, state_path)
        print(f"tdl progress updated: {saved}")
    except (OSError, ValueError, KeyError) as exc:
        print(f"failed to update tdl progress: {exc}")
        return 1

    return code


def _cmd_tdl_progress_show(state_file: Path | None) -> int:
    state_path = _resolve_tdl_state_file(state_file)
    try:
        state = load_tdl_progress(state_path)
    except (OSError, ValueError) as exc:
        print(f"failed to load tdl progress: {exc}")
        return 1

    total = len(TDL_CHALLENGES)
    completed_count = len(state.completed)
    unlocked = unlocked_tdl_challenges(state)
    print(f"tdl.progress.file: {state_path}")
    print(f"tdl.completed: {completed_count}/{total}")
    print(f"tdl.xp: {state.total_xp}")
    print(f"tdl.badges: {', '.join(state.badges) if state.badges else 'none'}")
    print(f"tdl.unlocked: {', '.join(unlocked) if unlocked else 'none'}")
    return 0


def _cmd_tdl_progress_reset(state_file: Path | None) -> int:
    state_path = _resolve_tdl_state_file(state_file)
    try:
        save_tdl_progress(clear_tdl_progress(), state_path)
    except OSError as exc:
        print(f"failed to reset tdl progress: {exc}")
        return 1
    print(f"tdl progress reset: {state_path}")
    return 0


def _stage_for_target(target: str) -> tuple[int, str] | None:
    normalized = target.strip()
    if not normalized:
        return None
    if normalized.lower() == "all":
        return len(LABS), "all"

    short_match = re.fullmatch(r"lab(\d{2})", normalized.lower())
    if short_match is not None:
        stage = int(short_match.group(1))
        if 1 <= stage <= len(LABS):
            return stage, f"lab{stage:02d}"
        return None

    for index, entry in enumerate(LABS, start=1):
        if normalized == entry["id"]:
            return index, entry["id"]
    return None


def _cmd_check(target: str) -> int:
    stage_info = _stage_for_target(target)
    if stage_info is None:
        print(f"unknown check target: {target}")
        print("valid examples: lab01, lab01_frame_and_headers, all")
        return 1

    stage_max, label = stage_info
    repo_root = Path(__file__).resolve().parents[2]
    print(f"running staged checks: target={label} stage_max={stage_max}")
    return run_staged_student_checks(stage_max=stage_max, repo_root=repo_root)


def _feature_coverage_counts(completed: set[str], *, matrix: object, level: str) -> tuple[int, int]:
    # `ConformanceMatrix` type is imported lazily through loader; this keeps CLI module decoupled.
    features_by_id = getattr(matrix, "features_by_id")
    features = [feature for feature in features_by_id.values() if feature.level == level and feature.labs]
    covered = sum(1 for feature in features if any(lab_id in completed for lab_id in feature.labs))
    return covered, len(features)


def _remediation_paths(lab_ids: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(f"docs/tutorial/{lab_id}.md" for lab_id in lab_ids)


def _cmd_report(state_file: Path | None, rubric_file: Path | None, json_out: Path | None) -> int:
    state_path = _resolve_state_file(state_file)
    try:
        state = load_progress(state_path)
        matrix = load_conformance_matrix()
        rubric = load_assessment_rubric(rubric_file)
    except (OSError, ValueError) as exc:
        print(f"failed to build report: {exc}")
        return 1

    completed = set(state.completed)
    unlocked = unlocked_labs(state)
    must_covered, must_total = _feature_coverage_counts(completed, matrix=matrix, level="MUST")
    should_covered, should_total = _feature_coverage_counts(completed, matrix=matrix, level="SHOULD")
    capstone_ready = len(missing_prereqs("lab27_capstone_incident_drill", completed)) == 0
    assessment = evaluate_assessment(state, rubric)
    remediation = _remediation_paths(assessment.at_risk_labs)

    labs_unlocked = ", ".join(unlocked) if unlocked else "none"
    capstone_ready_text = "yes" if capstone_ready else "no"
    print(f"report.profile: {matrix.profile}")
    print(f"report.as_of: {matrix.as_of}")
    print(f"labs.completed: {len(completed)}/{len(LABS)}")
    print(f"labs.unlocked: {labs_unlocked}")
    print(f"conformance.must: {must_covered}/{must_total}")
    print(f"conformance.should: {should_covered}/{should_total}")
    print(f"assessment.score: {assessment.overall_score:.2f}")
    print(f"assessment.band: {assessment.band}")
    print(f"assessment.at_risk_labs: {', '.join(assessment.at_risk_labs) if assessment.at_risk_labs else 'none'}")
    print(f"assessment.remediation_docs: {', '.join(remediation) if remediation else 'none'}")
    print(f"capstone.ready: {capstone_ready_text}")

    if json_out is not None:
        payload = {
            "profile": matrix.profile,
            "as_of": matrix.as_of,
            "rubric": {
                "profile": rubric.profile,
                "as_of": rubric.as_of,
                "version": rubric.version,
            },
            "labs": {
                "completed": len(completed),
                "total": len(LABS),
                "completed_ids": sorted(completed),
                "unlocked_ids": list(unlocked),
            },
            "conformance": {
                "must_covered": must_covered,
                "must_total": must_total,
                "should_covered": should_covered,
                "should_total": should_total,
            },
            "assessment": {
                "overall_score": assessment.overall_score,
                "band": assessment.band,
                "total_weight": assessment.total_weight,
                "weighted_earned": assessment.weighted_earned,
                "at_risk_labs": list(assessment.at_risk_labs),
                "remediation_docs": list(remediation),
            },
            "capstone_ready": capstone_ready,
        }
        try:
            json_out.parent.mkdir(parents=True, exist_ok=True)
            with json_out.open("w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, sort_keys=True)
                handle.write("\n")
            print(f"report written: {json_out}")
        except OSError as exc:
            print(f"failed to write report: {exc}")
            return 1
    return 0


def _cmd_debug_replay(trace_path: Path) -> int:
    records = load_trace(trace_path)
    for line in replay_lines(records):
        print(line)
    return 0


def _cmd_debug_explain(trace_path: Path, step: str | None) -> int:
    records = load_trace(trace_path)
    lines = explain_lines(records, step=step)
    for line in lines:
        print(line)
    if step is not None and lines and lines[0].startswith("step not found:"):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "labs":
        return _cmd_labs()
    if args.command == "show":
        return _cmd_show(args.lab_id)
    if args.command == "run":
        return _cmd_run(args.lab_id, args.completed, args.trace_out, args.state_file)
    if args.command == "check":
        return _cmd_check(args.target)
    if args.command == "progress":
        if args.progress_command == "show":
            return _cmd_progress_show(args.state_file)
        if args.progress_command == "mark":
            return _cmd_progress_mark(args.lab_id, args.state_file)
        if args.progress_command == "reset":
            return _cmd_progress_reset(args.state_file)
        parser.print_help()
        return 1
    if args.command == "tdl":
        if args.tdl_command == "list":
            return _cmd_tdl_list(args.state_file)
        if args.tdl_command == "show":
            return _cmd_tdl_show(args.challenge_id)
        if args.tdl_command == "check":
            return _cmd_tdl_check(args.target)
        if args.tdl_command == "run":
            return _cmd_tdl_run(args.challenge_id, args.state_file)
        if args.tdl_command == "progress":
            if args.tdl_progress_command == "show":
                return _cmd_tdl_progress_show(args.state_file)
            if args.tdl_progress_command == "reset":
                return _cmd_tdl_progress_reset(args.state_file)
            parser.print_help()
            return 1
        parser.print_help()
        return 1
    if args.command == "report":
        return _cmd_report(args.state_file, args.rubric_file, args.json_out)
    if args.command == "debug":
        if args.debug_command == "replay":
            return _cmd_debug_replay(args.trace)
        if args.debug_command == "explain":
            return _cmd_debug_explain(args.trace, args.step)
        parser.print_help()
        return 1

    parser.print_help()
    return 1
