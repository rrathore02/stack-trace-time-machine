"""Optional web dashboard for stt.

Read-only viewer over the SQLite history. Requires the [web] extra:

    pip install -e ".[web]"

Then:

    stt web                        # http://127.0.0.1:8765
    stt web --port 9000 --host 0.0.0.0
"""

from .app import create_app, run

__all__ = ["create_app", "run"]
