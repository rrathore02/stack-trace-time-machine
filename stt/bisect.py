"""Core bisect loop.

Given a known-good commit (test passes) and a known-bad commit (test fails),
binary-search the linear range between them to find the first commit where
the test starts failing. We assume:

  * `good` strictly precedes `bad` in history.
  * `good` passes and `bad` fails — callers should verify these endpoints
    before calling, otherwise the result is meaningless.

The standard `git bisect` invariant holds: the result is the *first bad*
commit, i.e. the smallest-index commit in `good..bad` for which the test
fails.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from . import git_utils


# A predicate that returns True when the test passes at a given SHA.
TestPredicate = Callable[[str], bool]

# Optional callback invoked after each step (sha, passed, iteration_index).
StepCallback = Callable[[str, bool, int], None]


@dataclass
class BisectResult:
    bad_commit: Optional[str]
    iterations: int
    log: list[tuple[str, bool]] = field(default_factory=list)
    skipped: int = 0


def bisect(
    repo: str,
    good: str,
    bad: str,
    test_fn: TestPredicate,
    on_step: StepCallback | None = None,
) -> BisectResult:
    """Binary-search `good..bad` for the first commit where `test_fn` returns False.

    `test_fn` is called with each candidate SHA after that SHA is checked out;
    it should run the test and return True iff it passes.

    Returns a BisectResult whose `bad_commit` is the first failing commit, or
    None if every commit in the range passed (i.e. the regression is older
    than `good` or the inputs are wrong).
    """
    candidates = git_utils.commits_between(repo, good, bad)
    if not candidates:
        # No commits strictly between good and bad: bad itself is the change.
        return BisectResult(bad_commit=bad, iterations=0)

    log: list[tuple[str, bool]] = []
    iterations = 0
    lo, hi = 0, len(candidates) - 1
    first_bad: Optional[str] = None

    while lo <= hi:
        mid = (lo + hi) // 2
        sha = candidates[mid]
        iterations += 1

        git_utils.checkout(repo, sha)
        passed = test_fn(sha)
        log.append((sha, passed))
        if on_step is not None:
            on_step(sha, passed, iterations)

        if passed:
            lo = mid + 1
        else:
            first_bad = sha
            hi = mid - 1

    return BisectResult(bad_commit=first_bad, iterations=iterations, log=log)
