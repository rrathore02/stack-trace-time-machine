"""Test runner abstraction.

Each runner knows how to invoke a specific test framework and return a
normalized TestResult. New frameworks plug in by subclassing TestRunner.
"""

from .base import TestResult, TestRunner
from .pytest_runner import PytestRunner

__all__ = ["TestResult", "TestRunner", "PytestRunner"]
