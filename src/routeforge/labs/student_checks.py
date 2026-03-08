"""Helpers for staged student test execution."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from xml.etree import ElementTree


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


def _format_test_name(class_name: str, test_name: str) -> str:
    if class_name.startswith("tests."):
        return f"{class_name.replace('.', '/')}.py::{test_name}"
    return f"{class_name}::{test_name}" if class_name else test_name


def _parse_failure_message(element: ElementTree.Element) -> str:
    message = (element.get("message") or "").strip()
    if not message:
        text = (element.text or "").strip()
        if text:
            message = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return message.removeprefix("AssertionError:").strip()


def _parse_junit_report(path: Path) -> tuple[int, int, tuple[StudentCheckFailure, ...]]:
    if not path.exists():
        return 0, 0, ()

    root = ElementTree.parse(path).getroot()
    cases = list(root.iter("testcase"))
    total = 0
    failed = 0
    failures: list[StudentCheckFailure] = []

    for case in cases:
        if case.find("skipped") is not None:
            continue

        total += 1
        failure = case.find("failure")
        error = case.find("error")
        if failure is None and error is None:
            continue

        failed += 1
        detail = failure if failure is not None else error
        assert detail is not None
        failures.append(
            StudentCheckFailure(
                test_name=_format_test_name(case.get("classname", ""), case.get("name", "")),
                message=_parse_failure_message(detail),
            )
        )

    passed = max(0, total - failed)
    return passed, total, tuple(failures)


def run_staged_student_checks(*, stage_max: int, repo_root: Path) -> StudentCheckRun:
    with tempfile.TemporaryDirectory(prefix="routeforge-student-checks-") as tmpdir:
        junit_path = Path(tmpdir) / "student-checks.xml"
        env = os.environ.copy()
        env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/student",
            "--stage-max",
            str(stage_max),
            "--junitxml",
            str(junit_path),
        ]
        completed = subprocess.run(
            command,
            cwd=repo_root,
            check=False,
            capture_output=True,
            env=env,
            text=True,
        )
        output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
        passed, total, failures = _parse_junit_report(junit_path)

    if total == 0:
        passed, failed = _parse_counts(output)
        total = passed + failed
        failures = _parse_failures(output)

    return StudentCheckRun(
        returncode=completed.returncode,
        passed=passed,
        total=total,
        failures=failures,
        raw_output=output,
    )
