"""Tests for storage queries used by the web dashboard."""

from __future__ import annotations

from pathlib import Path

import pytest

from stt.storage import Storage


def _seed(tmp_path: Path) -> Storage:
    db = Storage(tmp_path / "h.db")
    # repo A, test t1: 2 passes then 1 fail (currently red)
    db.record("/r/A", "t1", "sha1", True)
    db.record("/r/A", "t1", "sha2", True)
    db.record("/r/A", "t1", "sha3", False)
    # repo A, test t2: 1 fail then 1 pass (currently green)
    db.record("/r/A", "t2", "sha4", False)
    db.record("/r/A", "t2", "sha5", True)
    # repo B, test t3: 1 pass only
    db.record("/r/B", "t3", "sha6", True)
    return db


def test_recent_runs_orders_newest_first(tmp_path: Path) -> None:
    db = _seed(tmp_path)
    runs = db.recent_runs(limit=10)
    assert len(runs) == 6
    # Most recent insert wins; order is by timestamp desc, so last seeded first.
    assert runs[0].sha == "sha6"
    assert runs[-1].sha == "sha1"


def test_recent_runs_respects_limit(tmp_path: Path) -> None:
    db = _seed(tmp_path)
    runs = db.recent_runs(limit=2)
    assert len(runs) == 2


def test_tests_seen_groups_by_repo_and_test(tmp_path: Path) -> None:
    db = _seed(tmp_path)
    summaries = db.tests_seen()
    assert len(summaries) == 3  # (A,t1), (A,t2), (B,t3)

    by_test = {(s.repo, s.test_id): s for s in summaries}
    a_t1 = by_test[("/r/A", "t1")]
    assert a_t1.runs == 3
    assert a_t1.passes == 2
    assert a_t1.currently_red is True  # last run was a fail
    assert a_t1.fail_rate == pytest.approx(1 / 3)

    a_t2 = by_test[("/r/A", "t2")]
    assert a_t2.runs == 2
    assert a_t2.currently_red is False  # last run was a pass

    b_t3 = by_test[("/r/B", "t3")]
    assert b_t3.runs == 1
    assert b_t3.currently_red is False
    assert b_t3.last_failed_at is None


def test_tests_seen_orders_by_last_run_desc(tmp_path: Path) -> None:
    db = _seed(tmp_path)
    summaries = db.tests_seen()
    # Most recently active test first
    assert summaries[0].test_id == "t3"  # repo B, only test, was last seeded
