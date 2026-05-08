"""Thin subprocess-based wrapper around the git CLI.

We deliberately avoid pygit2 / dulwich to keep installation friction zero —
git is already on every developer machine, and shelling out is plenty fast
for the volumes a bisect tool sees (tens of commits, not thousands).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable


class GitError(RuntimeError):
    """Raised when a git command exits non-zero."""


def _run(args: Iterable[str], cwd: str | Path, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if check and proc.returncode != 0:
        raise GitError(
            f"git {' '.join(args)} failed (exit {proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def current_sha(repo: str | Path) -> str:
    return _run(["rev-parse", "HEAD"], cwd=repo)


def resolve(repo: str | Path, ref: str) -> str:
    """Resolve a ref (branch name, short SHA, HEAD~3, etc.) to a full SHA."""
    return _run(["rev-parse", ref], cwd=repo)


def commits_between(repo: str | Path, good: str, bad: str) -> list[str]:
    """Return commits in `good..bad`, oldest first.

    The range is exclusive of `good` and inclusive of `bad` — matching the
    semantics of `git bisect` (good is assumed to be the last passing commit).
    """
    out = _run(["rev-list", "--reverse", f"{good}..{bad}"], cwd=repo)
    return out.splitlines() if out else []


def checkout(repo: str | Path, sha: str) -> None:
    _run(["checkout", "--quiet", "--detach", sha], cwd=repo)


def files_changed(repo: str | Path, sha: str) -> list[str]:
    """Files modified by a single commit."""
    out = _run(["show", "--name-only", "--pretty=format:", sha], cwd=repo)
    return [line for line in out.splitlines() if line.strip()]


def is_clean(repo: str | Path) -> bool:
    return _run(["status", "--porcelain"], cwd=repo) == ""
