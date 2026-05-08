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
