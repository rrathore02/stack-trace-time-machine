"""Flaky-test handling.

If we naively trust a single failure, a flaky test will make bisect blame
the wrong commit. The standard mitigation is to re-run any apparent failure
N times and require at least K of those runs to fail before declaring the
commit "bad".

This module provides a small wrapper that does exactly that. It is wired in
above the test predicate, so the rest of the bisect code stays oblivious.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class FlakyVerdict:
    runs: int
    failures: int
    confirmed_failure: bool


def confirm(
    test_fn: Callable[[], bool],
    runs: int = 3,
    fail_threshold: float = 0.6,
) -> FlakyVerdict:
    """Re-run a test up to `runs` times; declare failure if the failure rate
    meets `fail_threshold`.

    Short-circuits as soon as the verdict is unambiguous: enough failures to
    cross the threshold (or enough passes that the threshold cannot be reached
    even if every remaining run fails).
    """
    failures = 0
    for i in range(runs):
        if test_fn():
            # passed
            pass
        else:
            failures += 1
        attempted = i + 1
        remaining = runs - attempted
        # Best-case future failures = failures + remaining
        if (failures + remaining) / runs < fail_threshold:
            return FlakyVerdict(runs=attempted, failures=failures, confirmed_failure=False)
        if failures / runs >= fail_threshold:
            return FlakyVerdict(runs=attempted, failures=failures, confirmed_failure=True)

    return FlakyVerdict(
        runs=runs,
        failures=failures,
        confirmed_failure=(failures / runs) >= fail_threshold,
    )


def wrap_predicate(
    inner: Callable[[str], bool],
    runs: int = 3,
    fail_threshold: float = 0.6,
) -> Callable[[str], bool]:
    """Wrap a (sha)->passed predicate so apparent failures get re-confirmed.

    Apparent passes are trusted on the first run — flakiness manifests as
    intermittent *failures*, almost never as intermittent *passes*, so we
    only burn extra runs on the failure side.
    """
    if runs <= 1:
        return inner

    def _wrapped(sha: str) -> bool:
        if inner(sha):
            return True
        verdict = confirm(lambda: inner(sha), runs=runs, fail_threshold=fail_threshold)
        return not verdict.confirmed_failure

    return _wrapped
