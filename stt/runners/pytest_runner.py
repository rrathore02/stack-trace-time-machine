"""pytest runner.

Runs a single test by id (e.g. ``tests/test_foo.py::test_bar``) and reports
pass/fail. We pass ``-x`` and ``--no-header -q`` to keep output tight, and
only the targeted test runs — collection of the full suite is skipped via
the explicit test id.
"""

from __future__ import annotations

import shlex
import subprocess
import sys
import time
from pathlib import Path

from .base import TestResult, TestRunner


class PytestRunner(TestRunner):
    name = "pytest"

    def __init__(self, python: str | None = None, extra_args: list[str] | None = None) -> None:
        self.python = python or sys.executable
        self.extra_args = list(extra_args or [])

    def run(self, repo: str | Path, test_id: str) -> TestResult:
        cmd = [
            self.python,
            "-m",
            "pytest",
            test_id,
            "-x",
            "--no-header",
            "-q",
            "--tb=short",
            *self.extra_args,
        ]
        start = time.monotonic()
        proc = subprocess.run(
            cmd,
            cwd=str(repo),
            capture_output=True,
            text=True,
            check=False,
        )
        duration = time.monotonic() - start
        return TestResult(
            passed=proc.returncode == 0,
            output=(proc.stdout or "") + (proc.stderr or ""),
            duration_seconds=duration,
            exit_code=proc.returncode,
        )

    def describe(self) -> str:
        return f"pytest ({shlex.join(self.extra_args) or 'no extra args'})"
