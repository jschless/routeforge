"""Helpers for staged student test execution."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def run_staged_student_checks(*, stage_max: int, repo_root: Path) -> int:
    command = [sys.executable, "-m", "pytest", "-q", "tests/student", "--stage-max", str(stage_max)]
    completed = subprocess.run(command, cwd=repo_root, check=False)
    return completed.returncode
