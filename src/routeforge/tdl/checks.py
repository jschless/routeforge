"""Helpers for running TDL pytest challenge checks."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys


def run_tdl_checks(*, target: str, repo_root: Path) -> int:
    command = [sys.executable, "-m", "pytest", "-q", "tests/tdl"]
    if target.lower() != "all":
        command.extend(["--tdl-target", target])
    env = os.environ.copy()
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    completed = subprocess.run(command, cwd=repo_root, check=False, env=env)
    return completed.returncode
