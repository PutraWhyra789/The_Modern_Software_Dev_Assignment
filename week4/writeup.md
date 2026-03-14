# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## SUBMISSION DETAILS

Name: Putra Whyra Pratama S. \
SUNet ID: **TODO** \
Citations: See individual automation sections below.

This assignment took me about **6** hours to do.


## YOUR RESPONSES

---

### Automation #1 — `CLAUDE.md` Repository Guidance File

**a. Design of each automation, including goals, inputs/outputs, steps**

> Inspired by the *"CLAUDE.md guidance files"* option (Part I, Section B) and the
> [Claude Code best practices article](https://www.anthropic.com/engineering/claude-code-best-practices),
> which states that "CLAUDE.md is the single most impactful file for steering Claude's
> behaviour — treat it like an onboarding doc for a new engineer."
>
> **Goal:** Provide a single authoritative onboarding document that any AI coding agent
> (Claude Code or opencode) automatically ingests at session start, eliminating the need
> for the agent to ask basic navigation questions or guess at project conventions.
>
> **Inputs:** Nothing — the file is read automatically at agent startup.
>
> **Outputs:** The agent session begins pre-loaded with:
> - All `make` targets and how to use them (`run`, `test`, `format`, `lint`, `seed`).
> - A code-navigation table: routers, models, schemas, services, tests, and the DB layer.
> - The approved development workflow: write failing test → implement → format/lint → update docs.
> - Style and safety guardrails (black line-length 100, ruff rules, no raw SQL, no hardcoded secrets).
> - A reference table for the two custom slash commands available in the repo.
> - All environment variables the app honours.
>
> **Steps taken to build it:**
> 1. Read `week4/Makefile`, all routers, services, models, schemas, and the test layout.
> 2. Identified the most common questions an agent would need to explore: "where are the
>    routers?", "how do I run tests?", "what linter is used?", "what columns does Note have?"
> 3. Wrote concise, table-driven sections so the agent can scan quickly without reading code.
> 4. Added an opencode-specific compatibility note (opencode reads `CLAUDE.md` as a fallback
>    when no `AGENTS.md` is present — [opencode Rules docs](https://opencode.ai/docs/rules/#claude-code-compatibility)).
> 5. Placed the file at the **repository root** (`modern-software-dev-assignments/CLAUDE.md`)
>    so it is discovered regardless of which subdirectory the agent session starts in.

**b. Before vs. after (i.e. manual workflow vs. automated workflow)**

> | Scenario | Manual workflow (before) | With CLAUDE.md (after) |
> |---|---|---|
> | "Where are the tests?" | Agent greps repo for `test_*.py` (~3 tool calls) | Agent answers immediately from CLAUDE.md |
> | "How do I start the app?" | Agent reads Makefile | Agent knows `make run` from context |
> | "What linter?" | Agent reads `pyproject.toml` | Agent answers from CLAUDE.md |
> | Adding a new endpoint | Agent infers a workflow, may skip lint step | Agent follows the explicit 5-step checklist |
> | Unsafe shell commands | Agent might run destructive DB commands | CLAUDE.md lists safe vs. forbidden commands |

**c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)**

> - **Autonomy level: Low supervision.** The `CLAUDE.md` file itself is pure documentation — it
>   only instructs the agent, it does not execute anything. No code permissions are required.
>   The file was reviewed manually before committing to ensure guardrails were accurate (e.g.,
>   the "safe commands" list was double-checked against the Makefile).
>
> - The downstream effect — agents following CLAUDE.md to implement features — used **medium
>   autonomy**: the agent was allowed to read and write Python and test files freely, but each
>   diff was reviewed before accepting, especially for changes to `schemas.py` (which affects
>   all endpoints) and `conftest.py` (which affects all tests).

**d. Multi-agent notes: roles, coordination strategy, and concurrency wins/risks/failures**

> Not applicable for this automation — `CLAUDE.md` is a single-agent guidance file.
> However, it *enables* multi-agent workflows: because every agent reads the same CLAUDE.md,
> there is no need to repeat project context per agent, reducing prompt token usage and
> ensuring consistent conventions across sessions.

**e. How you used the automation (what pain point it resolves or accelerates)**

> With CLAUDE.md providing instant context, the agent was able to implement four tasks from
> `docs/TASKS.md` in sequence without any warm-up navigation turns:
>
> 1. **Task 5** — Added `PUT /notes/{id}` and `DELETE /notes/{id}`; the agent immediately
>    knew where routers live and which schemas to update.
> 2. **Task 4** — Extended `services/extract.py` with `extract_tags()` and `extract_all()`,
>    then exposed `POST /notes/{id}/extract`; the agent found the service file in one step.
> 3. **Task 6** — Added `min_length` validation to all schemas using Pydantic `Field`.
> 4. **Task 7** — After adding routes, ran `/docs-sync` (Automation #2) to regenerate
>    `docs/API.md` with the new endpoints documented.
>
> **Pain point resolved:** Eliminated the ~5 tool-call "cold start" every agent session
> previously needed just to orient itself in the repository. Each session now starts
> immediately productive.

---

### Automation #2 — Slash Commands: `/run-tests` and `/docs-sync`

**a. Design of each automation, including goals, inputs/outputs, steps**

> Inspired by the *"Custom slash commands"* option (Part I, Section A) and the examples
> in the assignment brief (test runner with coverage, docs sync). The
> [Claude Code best practices article](https://www.anthropic.com/engineering/claude-code-best-practices)
> advises keeping commands "focused, use `$ARGUMENTS`, and prefer idempotent steps."
>
> Two commands were built:
>
> ---
>
> ### `/run-tests [path-or-marker]`
>
> **Goal:** Replace the manual `make test` + coverage inspection loop with a single
> command that runs tests, reports coverage, identifies uncovered lines, and suggests
> concrete next steps for each failure.
>
> **Inputs:** Optional `$ARGUMENTS` — a pytest path (`backend/tests/test_notes.py`) or
> marker expression (`-m unit`). Defaults to the full `backend/tests` suite.
>
> **Steps the agent executes:**
> 1. Run `pytest -q $ARGUMENTS --maxfail=5 --tb=short` and capture output.
> 2. If all pass, re-run with `--cov=backend/app --cov-report=term-missing`.
> 3. Present a Markdown table of every test: name, status, failure reason.
> 4. List coverage gaps (files + line ranges) if coverage < 90%.
> 5. For each failure, quote the exact assertion, point to the source line, and suggest
>    the minimal code change (without auto-applying it).
>
> **Output:** A structured Markdown report with a test-status table, coverage gaps
> section, and numbered action items per failure.
>
> **Safety:** Read-only with respect to source files — never edits code. Re-running is always safe.
>
> ---
>
> ### `/docs-sync [base_url]`
>
> **Goal:** Keep `week4/docs/API.md` perpetually in sync with the live OpenAPI spec so
> documentation never drifts from implementation.
>
> **Inputs:** Optional `$ARGUMENTS` — base URL of the running server (default:
> `http://localhost:8000`).
>
> **Steps the agent executes:**
> 1. Fetch `/openapi.json` from the running server (falls back to static Python import
>    if the server is not running, then to reading router source files directly).
> 2. Read the current `docs/API.md` and enumerate every documented `(METHOD, path)`.
> 3. Diff: compute `+ ADDED`, `- REMOVED`, and `~ CHANGED` routes.
> 4. Rewrite `docs/API.md` with one section per tag, one subsection per endpoint,
>    including request schema, response codes, and a minimal `curl` example.
> 5. Print a diff-like summary and any remaining TODOs.
>
> **Output:** Updated `week4/docs/API.md` + a diff summary printed in the chat.
>
> **Safety:** Only writes to `docs/API.md`. Never touches Python source or test files.
> Fully idempotent — running it twice produces the same result.
>
> ---
>
> **Dual-path storage for opencode compatibility:**
>
> Because the project uses **opencode** as an alternative to Claude Code, every command
> is stored in two locations:
> - `.claude/commands/` — for Claude Code (required by the assignment rubric).
> - `.opencode/commands/` — for opencode's native command discovery path.
>
> The base opencode does **not** natively scan `.claude/commands/` for custom commands —
> only `.opencode/commands/` and `~/.config/opencode/commands/`. This incompatibility is
> tracked as an open feature request
> ([issue #6985](https://github.com/anomalyco/opencode/issues/6985)).
> The frontmatter is kept compatible: both runtimes support `description` and
> `allowed-tools`; the `argument-hint` key used by Claude Code is silently ignored by opencode.

**b. Before vs. after (i.e. manual workflow vs. automated workflow)**

> | Task | Manual workflow (before) | With slash commands (after) |
> |---|---|---|
> | Run tests + check coverage | `make test`, then `pytest --cov ...` separately, manually read output | `/run-tests` — one command, structured Markdown report with per-failure suggestions |
> | Update API docs after a new route | Manually edit `docs/API.md`, compare with Swagger UI | `/docs-sync` — diffs and rewrites the file automatically |
> | Identify what to test next | Inspect coverage HTML report manually | `/run-tests` lists missing lines and recommends tests |
> | Keep docs from drifting | Manual discipline / frequently forgotten | `/docs-sync` makes it a one-command habit after every PR |

**c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)**

> - **`/run-tests`**: Read-only autonomy. The command is granted `bash` access to run
>   pytest but is explicitly instructed *not* to modify any source files. Output was
>   reviewed to confirm the coverage numbers were reasonable before acting on suggestions.
>
> - **`/docs-sync`**: Write autonomy scoped to `docs/API.md` only. The command is
>   explicitly prohibited from touching Python source or test files. The rewritten
>   `docs/API.md` was reviewed manually after each run to verify curl examples were
>   accurate and no routes were accidentally omitted.
>
> - Both commands are idempotent, so there is no risk from running them multiple times.
>   Rollback for `/docs-sync` is simply `git checkout week4/docs/API.md`.

**d. Multi-agent notes: roles, coordination strategy, and concurrency wins/risks/failures**

> The slash commands are designed to be used *between* agent roles in a multi-agent
> workflow:
>
> - **Agent A** (implementation) adds a new endpoint → hands off to **Agent B** (test
>   runner) which runs `/run-tests` to verify → hands off to **Agent C** (docs) which
>   runs `/docs-sync` to update `API.md`.
>
> This pipeline ensures that no agent can "forget" to run tests or update docs — those
> steps are encapsulated in the commands.
>
> **Concurrency risk:** If two agents run `/docs-sync` simultaneously on the same branch,
> they could produce conflicting rewrites of `API.md`. Mitigation: only one agent should
> own the docs step; or use git worktrees to isolate the working directories.

**e. How you used the automation (what pain point it resolves or accelerates)**

> ### Using `/run-tests`
>
> After implementing `PUT /notes/{id}`, `DELETE /notes/{id}`, and
> `POST /notes/{id}/extract`, `/run-tests` was run to get a full picture of test coverage.
> The command identified that `extract_tags()` and `extract_all()` in
> `services/extract.py` were not yet tested. Based on those coverage gaps, 33 new unit
> tests were written across `test_extract.py` and `test_notes.py`, covering:
> - `extract_tags` — deduplication, case normalisation, sorting, edge cases.
> - `extract_all` — combined extraction, empty input, type assertions.
> - All new API endpoints — CRUD, validation (422s), 404s, and the
>   `save_items=true` side-effect of the extract endpoint.
>
> `/run-tests` also caught a Windows-specific SQLite file-lock bug in `conftest.py`
> (teardown `PermissionError`), which was fixed by calling `engine.dispose()` before
> `os.unlink()`.
>
> Running `/run-tests` a second time confirmed **61 tests passing, 0 failures, 0 errors**.
>
> ### Using `/docs-sync`
>
> After all new endpoints were implemented and tested, `/docs-sync` was run (server-off
> mode, using the Python import fallback). The command detected three new routes missing
> from the docs and one changed schema (`NoteCreate` now has `min_length` constraints).
> It rewrote `week4/docs/API.md` to include:
> - `PUT /notes/{note_id}` — partial update with validation table.
> - `DELETE /notes/{note_id}` — 204 response, 404 guard.
> - `POST /notes/{note_id}/extract` — action items + tags extraction, `save_items`
>   query param, `ExtractResult` schema, two `curl` examples.
> - Updated `POST /notes/` request table with the new `min_length` constraints.
>
> **Pain point resolved:** API documentation was previously always stale after any code
> change. With `/docs-sync`, keeping docs accurate became a zero-friction, one-command step.

---

### Automation #3 — opencode Compatibility Layer (Bonus)

**a. Design of each automation, including goals, inputs/outputs, steps**

> This is a meta-automation: ensuring that all of the above automations actually work
> in opencode, the runtime being used for this assignment.
>
> **Goal:** Make all three automation artefacts (`CLAUDE.md`, `/run-tests`, `/docs-sync`)
> discoverable and functional in opencode, not just Claude Code.
>
> **Compatibility matrix:**
>
> | Feature | Claude Code path | opencode path | Compatible? |
> |---|---|---|---|
> | Guidance file | `CLAUDE.md` (repo root) | `CLAUDE.md` as fallback if no `AGENTS.md` | ✅ Full |
> | Slash command: run-tests | `.claude/commands/run-tests.md` | `.opencode/commands/run-tests.md` (mirrored) | ✅ With mirror |
> | Slash command: docs-sync | `.claude/commands/docs-sync.md` | `.opencode/commands/docs-sync.md` (mirrored) | ✅ With mirror |
> | `argument-hint` frontmatter | Supported | Silently ignored | ✅ Safe |
> | `$ARGUMENTS` placeholder | Supported | Supported | ✅ Full |
> | `!bash` execution in commands | Supported | Supported | ✅ Full |
>
> **Steps:**
> 1. Verified opencode's Claude Code compatibility docs: `CLAUDE.md` is supported as fallback
>    ([opencode Rules docs](https://opencode.ai/docs/rules/#claude-code-compatibility)).
> 2. Identified that `.claude/commands/` is **not** scanned by opencode natively
>    ([issue #6985](https://github.com/anomalyco/opencode/issues/6985)).
> 3. Created mirrored copies in `.opencode/commands/` with identical content minus the
>    `argument-hint` frontmatter key (which opencode does not recognise).
> 4. Documented the dual-path strategy in `CLAUDE.md` itself for future contributors.

**b. Before vs. after (i.e. manual workflow vs. automated workflow)**

> | | Before compatibility layer | After |
> |---|---|---|
> | CLAUDE.md in opencode | Not loaded (no AGENTS.md present) | Loaded automatically as fallback |
> | Custom slash commands in opencode | Not discoverable (wrong directory) | Discoverable via `.opencode/commands/` |
> | Invocation syntax | Unclear — `/project:run-tests`? | Simply `/run-tests` (same as Claude Code) |
> | Migrating from Claude Code to opencode | Must manually copy/rename all files | Works out of the box |

**c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)**

> No code changes were made — this was purely a file organisation and compatibility
> documentation task. Autonomy level: fully supervised manual work (copying `.md` files
> between directories and verifying frontmatter compatibility).

**d. Multi-agent notes: roles, coordination strategy, and concurrency wins/risks/failures**

> The compatibility layer is transparent to all agents. Whether an agent runs in Claude
> Code or opencode, it picks up the same `CLAUDE.md` and the same slash commands (via
> different discovery paths). This means multi-agent sessions can mix Claude Code and
> opencode agents on the same repository without any configuration divergence.

**e. How you used the automation (what pain point it resolves or accelerates)**

> The compatibility layer meant the entire development workflow — CLAUDE.md context,
> `/run-tests`, and `/docs-sync` — could be used directly in opencode without any
> additional setup. Every test run and docs-sync performed during development used the
> opencode-native command paths (`.opencode/commands/`), validating that the mirroring
> strategy works correctly end-to-end.
>
> **Pain point resolved:** Users switching between Claude Code and opencode no longer
> need to maintain two separate sets of command files. One source of truth, two discovery
> paths.
