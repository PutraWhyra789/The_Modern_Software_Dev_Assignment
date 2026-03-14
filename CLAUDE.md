# CLAUDE.md — Repository Guidance

> This file is automatically read by Claude Code at session start.
> OpenCode users: this file is loaded as a fallback when no `AGENTS.md` is present.

---

## Project Overview

This is a multi-week course repository for **Modern Software Development (CS146S)**.
The active development area is **`week4/`**, which contains a minimal full-stack
"developer command center" built with:

- **Backend**: FastAPI + SQLAlchemy (SQLite)
- **Frontend**: Vanilla JS / HTML / CSS (no build step)
- **Tests**: pytest
- **Linting/Formatting**: black + ruff + pre-commit

---

## Quick Start (always run from `week4/`)

```bash
cd week4

# Run the development server
make run          # → http://localhost:8000 (UI) and /docs (Swagger)

# Run all tests
make test         # pytest -q backend/tests

# Format code (black + ruff --fix)
make format

# Lint only (no auto-fix)
make lint

# Re-seed the database (drops + recreates if DB is missing)
make seed
```

---

## Code Navigation

### Backend entry point
`week4/backend/app/main.py` — FastAPI app factory, mounts static files, registers routers, calls DB seed on startup.

### Routers (HTTP endpoints)
| File | Prefix | Description |
|------|--------|-------------|
| `week4/backend/app/routers/notes.py` | `/notes` | CRUD + search + extract for notes |
| `week4/backend/app/routers/action_items.py` | `/action-items` | CRUD + complete action items |

### Data layer
| File | Purpose |
|------|---------|
| `week4/backend/app/models.py` | SQLAlchemy ORM models (`Note`, `ActionItem`) |
| `week4/backend/app/schemas.py` | Pydantic request/response schemas |
| `week4/backend/app/db.py` | Engine, session factory, `apply_seed_if_needed()` |
| `week4/data/seed.sql` | SQL seed run once on first DB creation |

### Services
`week4/backend/app/services/extract.py` — `extract_action_items(text)`, `extract_tags(text)`, `extract_all(text)`.

### Tests
`week4/backend/tests/` — pytest test suite with a `client` fixture in `conftest.py` (uses a temp SQLite DB per test run).

### Frontend
`week4/frontend/index.html`, `app.js`, `styles.css` — static SPA served via FastAPI's `StaticFiles`.

### Docs
`week4/docs/TASKS.md` — outstanding feature tasks for agent-driven workflows.
`week4/docs/API.md` — living API reference (keep in sync with `/openapi.json`).

---

## Development Workflow

### When adding a new endpoint
1. Write a **failing test** in `backend/tests/test_<resource>.py`
2. Implement the endpoint in `backend/app/routers/<resource>.py`
3. Add/update Pydantic schemas in `backend/app/schemas.py`
4. Run `make test` — all tests must pass
5. Run `make format && make lint` — must be clean
6. Update `week4/docs/API.md` to reflect new routes

### When changing a model
1. Update `backend/app/models.py`
2. Update `backend/app/schemas.py` accordingly
3. Update `week4/data/seed.sql` if the schema change affects seed data
4. Delete `week4/data/app.db` to trigger a fresh seed on next `make run`
5. Run `make test` to verify nothing broke

### When running pre-commit
```bash
pre-commit run --all-files
```
Fix any black/ruff issues it flags before committing.

---

## Style & Safety Guardrails

- **Formatter**: `black` (line length 100). Never manually reformat; always run `make format`.
- **Linter**: `ruff` — follow all existing rule settings in `pyproject.toml`.
- **Type annotations**: required on all function signatures.
- **No raw SQL** in routers — use SQLAlchemy ORM or `select()` constructs.
- **No hardcoded secrets** — use environment variables via `python-dotenv`.
- **Safe commands to run freely**: `make test`, `make format`, `make lint`, `make run`, `make seed`.
- **Avoid**: dropping the production DB, running migrations on `week4/data/app.db` in CI, installing packages not in `pyproject.toml`.

---

## Custom Slash Commands (Claude Code / OpenCode)

| Command | Location | Purpose |
|---------|----------|---------|
| `/run-tests` | `.claude/commands/run-tests.md` | Run pytest with coverage; summarise failures |
| `/docs-sync` | `.claude/commands/docs-sync.md` | Sync `docs/API.md` with live OpenAPI spec |

> **OpenCode users**: commands are mirrored in `.opencode/commands/` for native discovery.
> Invoke them with the same syntax: `/run-tests` and `/docs-sync`.
> `CLAUDE.md` is read as a fallback when no `AGENTS.md` is present.

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_PATH` | `./data/app.db` | SQLite DB file path |
| `HOST` | `127.0.0.1` | Uvicorn bind host |
| `PORT` | `8000` | Uvicorn bind port |