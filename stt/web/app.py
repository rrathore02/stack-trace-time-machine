"""FastAPI app for the stt web dashboard.

The app is constructed by `create_app(db_path)` so it's trivially testable —
hand it any path and you have a working ASGI app. `run(...)` is a thin
convenience that boots uvicorn for the CLI.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from ..storage import DEFAULT_DB_PATH, Storage


_HERE = Path(__file__).resolve().parent
_TEMPLATES_DIR = _HERE / "templates"


def create_app(db_path: str | Path | None = None) -> FastAPI:
    """Build a FastAPI app backed by the storage at `db_path`.

    Pass an explicit path in tests; production uses the default
    ~/.stt/history.db so the dashboard sees the same data the CLI writes.
    """
    storage = Storage(db_path or DEFAULT_DB_PATH)
    templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

    app = FastAPI(
        title="stt dashboard",
        description="Read-only viewer over the stt bisect history.",
        version="0.1.0",
    )

    # ---- HTML pages ----

    @app.get("/", response_class=HTMLResponse)
    async def dashboard(request: Request) -> Any:
        recent = storage.recent_runs(limit=50)
        tests = storage.tests_seen()
        red_count = sum(1 for t in tests if t.currently_red)
        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "recent": recent,
                "tests": tests,
                "red_count": red_count,
            },
        )

    @app.get("/test", response_class=HTMLResponse)
    async def test_history(
        request: Request,
        repo: str = Query(..., description="Repo path"),
        test: str = Query(..., description="Test id"),
    ) -> Any:
        history = storage.history(repo, test, limit=200)
        if not history:
            raise HTTPException(status_code=404, detail="No runs recorded for that test")
        last_pass = storage.last_passing_sha(repo, test)
        return templates.TemplateResponse(
            request,
            "test.html",
            {
                "repo": repo,
                "test": test,
                "history": history,
                "last_pass": last_pass,
            },
        )

    # ---- JSON API ----

    @app.get("/api/runs")
    async def api_runs(limit: int = 50) -> JSONResponse:
        runs = storage.recent_runs(limit=limit)
        return JSONResponse([asdict(r) for r in runs])

    @app.get("/api/tests")
    async def api_tests() -> JSONResponse:
        tests = storage.tests_seen()
        out = []
        for t in tests:
            row = asdict(t)
            row["fail_rate"] = t.fail_rate
            row["currently_red"] = t.currently_red
            out.append(row)
        return JSONResponse(out)

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def run(
    host: str = "127.0.0.1",
    port: int = 8765,
    db_path: str | Path | None = None,
) -> None:
    """Boot uvicorn with the dashboard app. Blocks until interrupted."""
    import uvicorn

    app = create_app(db_path)
    uvicorn.run(app, host=host, port=port, log_level="info")
