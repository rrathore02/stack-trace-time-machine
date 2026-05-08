"""Abstract base for test runners."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    passed: bool
    output: str
    duration_seconds: float
    exit_code: int


class TestRunner(ABC):
    """Run a single test and report whether it passed.

    Implementations should run only the specified test (not the full suite)
    so that bisect iterations stay fast — that is the single biggest lever
    for end-to-end bisect time.
    """

    name: str = "base"

    @abstractmethod
    def run(self, repo: str | Path, test_id: str) -> TestResult:
        """Run `test_id` inside `repo` and return the result."""
