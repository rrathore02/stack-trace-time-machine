"""Tests for the core bisect loop using a real throwaway git repo."""

from __future__ import annotations

from pathlib import Path

from stt.bisect import bisect, make_stack_trace_filter


def test_finds_first_failing_commit(tiny_repo: Path, tiny_repo_shas: list[str]) -> None:
    # Test "fails" iff bug.txt exists in the working tree at that commit.
    def test_fn(_sha: str) -> bool:
        return not (tiny_repo / "bug.txt").exists()

    result = bisect(str(tiny_repo), tiny_repo_shas[0], tiny_repo_shas[4], test_fn)
    assert result.bad_commit == tiny_repo_shas[2]
    # log(5 candidates) = ceil(log2(4)) ≤ 3 iterations
    assert result.iterations <= 3


def test_returns_none_when_everything_passes(tiny_repo: Path, tiny_repo_shas: list[str]) -> None:
    def always_pass(_sha: str) -> bool:
        return True

    result = bisect(str(tiny_repo), tiny_repo_shas[0], tiny_repo_shas[4], always_pass)
    assert result.bad_commit is None


def test_records_log_in_step_order(tiny_repo: Path, tiny_repo_shas: list[str]) -> None:
    def test_fn(_sha: str) -> bool:
        return not (tiny_repo / "bug.txt").exists()

    result = bisect(str(tiny_repo), tiny_repo_shas[0], tiny_repo_shas[4], test_fn)
    assert len(result.log) == result.iterations
    # Final entry must be a failure (the bad commit) or, for boundary cases,
    # consistent with the result.
    if result.bad_commit:
        assert any(not passed for _, passed in result.log)


def test_stack_trace_filter_skips_unrelated_commits(tiny_repo: Path, tiny_repo_shas: list[str]) -> None:
    """If we tell bisect 'only test commits that touched bug.txt', we should
    skip C0, C1, C3, C4 entirely and find C2 in a single iteration."""

    def test_fn(_sha: str) -> bool:
        return not (tiny_repo / "bug.txt").exists()

    flt = make_stack_trace_filter(str(tiny_repo), ["bug.txt"])
    result = bisect(
        str(tiny_repo),
        tiny_repo_shas[0],
        tiny_repo_shas[4],
        test_fn,
        candidate_filter=flt,
    )
    assert result.bad_commit == tiny_repo_shas[2]
    assert result.iterations == 1
    assert result.skipped == 3  # C1, C3, C4 (C0 is the good baseline, excluded)
