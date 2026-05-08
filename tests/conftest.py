"""Shared fixtures."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True,
    )
    return proc.stdout.strip()


@pytest.fixture
def tiny_repo(tmp_path: Path) -> Path:
    """A throwaway git repo with a linear history of 5 commits.

    Commit C2 introduces a "bug" (writes 'BAD' to bug.txt). Commits C0, C1
    are clean; C3, C4 do not touch bug.txt and therefore inherit the bug.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "config", "commit.gpgsign", "false")

    files = {
        0: ("README.md", "hello\n"),
        1: ("a.py", "def a(): return 1\n"),
        2: ("bug.txt", "BAD\n"),
        3: ("b.py", "def b(): return 2\n"),
        4: ("c.py", "def c(): return 3\n"),
    }
    shas: dict[int, str] = {}
    for i in range(5):
        name, content = files[i]
        (repo / name).write_text(content)
        _git(repo, "add", name)
        _git(repo, "commit", "-m", f"commit {i}")
        shas[i] = _git(repo, "rev-parse", "HEAD")

    # Stash the SHA list on the repo path for tests to read.
    (repo / ".shas").write_text("\n".join(shas[i] for i in range(5)))
    return repo


@pytest.fixture
def tiny_repo_shas(tiny_repo: Path) -> list[str]:
    return (tiny_repo / ".shas").read_text().splitlines()
