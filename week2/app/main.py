"""FastAPI application entry-point.

Refactored with AI assistance (Exercise 3):
- Replaced import-time init_db() with @asynccontextmanager lifespan handler.
- Centralised configuration.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .routers import action_items, notes


# ── Lifespan (Exercise 3 refactor) ──────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: initialise the database on startup."""
    init_db()
    yield


app = FastAPI(title="Action Item Extractor", lifespan=lifespan)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def index() -> str:
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    return html_path.read_text(encoding="utf-8")


app.include_router(notes.router)
app.include_router(action_items.router)


# ── Static files ────────────────────────────────────────────────────────────

static_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
