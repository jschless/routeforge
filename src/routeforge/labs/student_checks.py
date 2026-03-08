"""Helpers for staged student test execution."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys


@dataclass(frozen=True)
class StudentCheckFailure:
    test_name: str
    message: str


@dataclass(frozen=True)
class StudentCheckRun:
    returncode: int
    passed: int
    total: int
    failures: tuple[StudentCheckFailure, ...]
    raw_output: str


_FAILED_LINE_RE = re.compile(r"^FAILED\s+(\S+)\s+-\s+(.*)$")


def _parse_counts(output: str) -> tuple[int, int]:
    passed = 0
    failed = 0
    for line in output.splitlines():
        if " passed" in line:
            match = re.search(r"(\d+)\s+passed", line)
            if match is not None:
                passed = int(match.group(1))
        if " failed" in line:
            match = re.search(r"(\d+)\s+failed", line)
            if match is not None:
                failed = int(match.group(1))
    return passed, failed


def _parse_failures(output: str) -> tuple[StudentCheckFailure, ...]:
    failures: list[StudentCheckFailure] = []
    for line in output.splitlines():
        match = _FAILED_LINE_RE.match(line.strip())
        if match is None:
            continue
        test_name, message = match.groups()
        trimmed = message.removeprefix("AssertionError:").strip()
        failures.append(StudentCheckFailure(test_name=test_name, message=trimmed))
    return tuple(failures)


def run_staged_student_checks(*, stage_max: int, repo_root: Path) -> StudentCheckRun:
    command = [sys.executable, "-m", "pytest", "-q", "tests/student", "--stage-max", str(stage_max)]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
    passed, failed = _parse_counts(output)
    return StudentCheckRun(
        returncode=completed.returncode,
        passed=passed,
        total=passed + failed,
        failures=_parse_failures(output),
        raw_output=output,
    )
