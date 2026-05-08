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

Optional `candidate_filter` enables stack-trace-aware bisect: the caller can
restrict the search to commits that touched files appearing in the failing
trace. This is a *heuristic* — a regression can in principle be caused by a
commit that doesn't touch any traced file (e.g. a config change). When in
doubt, run without a filter.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from . import git_utils


# A predicate that returns True when the test passes at a given SHA.
TestPredicate = Callable[[str], bool]

# Optional callback invoked after each step (sha, passed, iteration_index).
StepCallback = Callable[[str, bool, int], None]

# Predicate: True if this commit *could* be the regression (worth testing).
CandidateFilter = Callable[[str], bool]


@dataclass
class BisectResult:
    bad_commit: Optional[str]
    iterations: int
    log: list[tuple[str, bool]] = field(default_factory=list)
    skipped: int = 0
    total_candidates: int = 0


def bisect(
    repo: str,
    good: str,
    bad: str,
    test_fn: TestPredicate,
    candidate_filter: CandidateFilter | None = None,
    on_step: StepCallback | None = None,
) -> BisectResult:
    """Binary-search `good..bad` for the first commit where `test_fn` returns False.

    `candidate_filter`, if given, prunes commits that cannot plausibly contain
    the regression (heuristic). Pruned commits are not tested, which is the
    main lever for cutting bisect wall time on large ranges.
    """
    all_commits = git_utils.commits_between(repo, good, bad)
    if not all_commits:
        return BisectResult(bad_commit=bad, iterations=0)

    skipped = 0
    if candidate_filter is not None:
        filtered = [c for c in all_commits if candidate_filter(c)]
        skipped = len(all_commits) - len(filtered)
        if not filtered:
            return BisectResult(
                bad_commit=None,
                iterations=0,
                skipped=skipped,
                total_candidates=len(all_commits),
            )
        candidates = filtered
    else:
        candidates = all_commits

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

    return BisectResult(
        bad_commit=first_bad,
        iterations=iterations,
        log=log,
        skipped=skipped,
        total_candidates=len(all_commits),
    )


def make_stack_trace_filter(repo: str, files_in_trace: list[str]) -> CandidateFilter:
    """Build a filter that keeps commits touching any file from the stack trace.

    Path matching is suffix-based: a trace path of ``app/foo.py`` matches a
    changed path of ``src/app/foo.py`` and vice versa. This handles repos
    where pytest reports paths relative to a non-root testroot.
    """
    targets = [_normalize_for_match(f) for f in files_in_trace]

    def _filter(sha: str) -> bool:
        changed = [_normalize_for_match(p) for p in git_utils.files_changed(repo, sha)]
        for c in changed:
            for t in targets:
                if c == t or c.endswith("/" + t) or t.endswith("/" + c):
                    return True
        return False

    return _filter


def _normalize_for_match(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")
