"""SQLite-backed history of test runs.

We record every (repo, test_id, sha) → pass/fail so that the next bisect
can default the `--good` endpoint to the most recent commit where the test
was known to pass. Without this, the user has to remember or guess.

The DB lives at ~/.stt/history.db by default. It is intentionally local —
this is a developer tool, not a service.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional


DEFAULT_DB_PATH = Path.home() / ".stt" / "history.db"


_SCHEMA = """
CREATE TABLE IF NOT EXISTS test_runs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    repo      TEXT    NOT NULL,
    test_id   TEXT    NOT NULL,
    sha       TEXT    NOT NULL,
    passed    INTEGER NOT NULL,
    timestamp TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_runs_lookup
    ON test_runs(repo, test_id, timestamp DESC);
"""


class Storage:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(_SCHEMA)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def record(self, repo: str, test_id: str, sha: str, passed: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO test_runs (repo, test_id, sha, passed, timestamp) "
                "VALUES (?, ?, ?, ?, ?)",
                (repo, test_id, sha, int(passed), datetime.now(timezone.utc).isoformat()),
            )

    def last_passing_sha(self, repo: str, test_id: str) -> Optional[str]:
        """Most recent SHA where this test was recorded as passing."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT sha FROM test_runs "
                "WHERE repo = ? AND test_id = ? AND passed = 1 "
                "ORDER BY timestamp DESC LIMIT 1",
                (repo, test_id),
            ).fetchone()
            return row[0] if row else None

    def history(self, repo: str, test_id: str, limit: int = 20) -> list[tuple[str, bool, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT sha, passed, timestamp FROM test_runs "
                "WHERE repo = ? AND test_id = ? "
                "ORDER BY timestamp DESC LIMIT ?",
                (repo, test_id, limit),
            ).fetchall()
        return [(sha, bool(passed), ts) for sha, passed, ts in rows]

    # ----- queries used by the web dashboard -----

    def recent_runs(self, limit: int = 50) -> list[RunRow]:
        """Most recent runs across all repos and tests."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT repo, test_id, sha, passed, timestamp FROM test_runs "
                "ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            RunRow(repo=r, test_id=t, sha=s, passed=bool(p), timestamp=ts)
            for r, t, s, p, ts in rows
        ]

    def tests_seen(self) -> list[TestSummary]:
        """One row per (repo, test_id) ever recorded, with summary stats."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    repo,
                    test_id,
                    COUNT(*)                        AS runs,
                    SUM(passed)                     AS passes,
                    MAX(timestamp)                  AS last_run_at,
                    -- last_passed_at: the most recent timestamp where passed=1
                    MAX(CASE WHEN passed = 1 THEN timestamp END) AS last_passed_at,
                    MAX(CASE WHEN passed = 0 THEN timestamp END) AS last_failed_at
                FROM test_runs
                GROUP BY repo, test_id
                ORDER BY last_run_at DESC
                """
            ).fetchall()
        return [
            TestSummary(
                repo=repo,
                test_id=test_id,
                runs=runs,
                passes=passes or 0,
                last_run_at=last_run_at,
                last_passed_at=last_passed_at,
                last_failed_at=last_failed_at,
            )
            for repo, test_id, runs, passes, last_run_at, last_passed_at, last_failed_at in rows
        ]


@dataclass
class RunRow:
    repo: str
    test_id: str
    sha: str
    passed: bool
    timestamp: str


@dataclass
class TestSummary:
    repo: str
    test_id: str
    runs: int
    passes: int
    last_run_at: str
    last_passed_at: Optional[str]
    last_failed_at: Optional[str]

    @property
    def fail_rate(self) -> float:
        if self.runs == 0:
            return 0.0
        return 1.0 - (self.passes / self.runs)

    @property
    def currently_red(self) -> bool:
        """True if the most recent run was a failure."""
        if self.last_failed_at is None:
            return False
        if self.last_passed_at is None:
            return True
        return self.last_failed_at > self.last_passed_at
