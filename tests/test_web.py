"""Smoke tests for the web dashboard.

These tests are skipped if the [web] extra isn't installed, so the rest of
the suite still runs in lean environments.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from stt.storage import Storage  # noqa: E402
from stt.web.app import create_app  # noqa: E402


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    db = tmp_path / "history.db"
    storage = Storage(db)
    storage.record("/repo/A", "tests/test_x.py::test_a", "sha_aaaa", True)
    storage.record("/repo/A", "tests/test_x.py::test_a", "sha_bbbb", False)
    storage.record("/repo/A", "tests/test_x.py::test_b", "sha_cccc", True)
    app = create_app(db_path=db)
    return TestClient(app)


def test_health_endpoint(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_dashboard_renders(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.text
    # Header + at least one test row + the per-test link target
    assert "stt dashboard" in body
    assert "tests/test_x.py::test_a" in body
    assert "/test?repo=" in body


def test_dashboard_marks_currently_red(client: TestClient) -> None:
    resp = client.get("/")
    body = resp.text
    # test_a has the most recent run as a fail → red
    assert "red" in body
    # test_b had only a pass → green
    assert "green" in body


def test_test_history_page(client: TestClient) -> None:
    resp = client.get(
        "/test", params={"repo": "/repo/A", "test": "tests/test_x.py::test_a"}
    )
    assert resp.status_code == 200
    body = resp.text
    assert "sha_aaaa" in body
    assert "sha_bbbb" in body
    # The "last passing" SHA is sha_aaaa
    assert "Last passing commit" in body


def test_test_history_404_on_unknown(client: TestClient) -> None:
    resp = client.get("/test", params={"repo": "/nope", "test": "nope"})
    assert resp.status_code == 404


def test_api_runs_returns_json(client: TestClient) -> None:
    resp = client.get("/api/runs")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert {row["sha"] for row in data} == {"sha_aaaa", "sha_bbbb", "sha_cccc"}
    assert all({"repo", "test_id", "sha", "passed", "timestamp"} <= row.keys() for row in data)


def test_api_runs_respects_limit(client: TestClient) -> None:
    resp = client.get("/api/runs", params={"limit": 1})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_api_tests_includes_red_flag(client: TestClient) -> None:
    resp = client.get("/api/tests")
    assert resp.status_code == 200
    by_test = {row["test_id"]: row for row in resp.json()}
    assert by_test["tests/test_x.py::test_a"]["currently_red"] is True
    assert by_test["tests/test_x.py::test_b"]["currently_red"] is False
