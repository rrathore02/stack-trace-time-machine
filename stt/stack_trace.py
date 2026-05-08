"""Parse failing-test output to extract source file paths.

The bisect optimization that matters most in practice is: only test commits
that touched a file appearing in the stack trace. To do that we need to pull
file paths out of the failure output of various test runners.

We start with Python tracebacks (pytest output). Other languages can be added
by implementing additional extractors and registering them in EXTRACTORS.
"""

from __future__ import annotations

import re
from pathlib import PurePosixPath, PureWindowsPath


_PY_TRACEBACK_LINE = re.compile(r'\s*File "([^"]+)", line (\d+)')
_PYTEST_LOCATION = re.compile(r"^([^\s:]+\.py):(\d+):", re.MULTILINE)


# File path fragments we always ignore — these are never the regression site.
_IGNORE_FRAGMENTS = (
    "site-packages",
    "/dist-packages/",
    "<frozen ",
    "<string>",
    "<stdin>",
    "_pytest/",
    "pluggy/",
)


def _normalize(path: str) -> str:
    """Normalize OS-specific path separators to forward slashes."""
    if "\\" in path:
        return str(PureWindowsPath(path).as_posix())
    return str(PurePosixPath(path))


def _keep(path: str) -> bool:
    return not any(frag in path for frag in _IGNORE_FRAGMENTS)


def extract_python_files(text: str) -> list[str]:
    """Pull source file paths out of a Python traceback or pytest output.

    Returns paths in the order they first appear, deduplicated. Stdlib and
    site-packages frames are dropped since they are never the regression.
    """
    candidates: list[str] = []
    for match in _PY_TRACEBACK_LINE.finditer(text):
        candidates.append(match.group(1))
    for match in _PYTEST_LOCATION.finditer(text):
        candidates.append(match.group(1))

    seen: set[str] = set()
    out: list[str] = []
    for raw in candidates:
        if not _keep(raw):
            continue
        norm = _normalize(raw)
        if norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
    return out


# Future: register more extractors keyed by runner name.
EXTRACTORS = {
    "pytest": extract_python_files,
    "python": extract_python_files,
}
