---
description: "Run pytest suite with optional coverage; summarise failures and suggest fixes."
argument-hint: "[path-or-marker]"
allowed-tools: ["Bash"]
---

You are a test-runner assistant. Follow every step below in order.

## 1 — Determine scope

If `$ARGUMENTS` is non-empty, use it as the pytest target (a path like
`backend/tests/test_notes.py` or a marker expression like `-m unit`).
Otherwise default to `backend/tests`.

## 2 — Run the tests (quick pass)

```bash
cd week4 && PYTHONPATH=. pytest -q $ARGUMENTS --maxfail=5 --tb=short 2>&1
```

Capture the full output. Note every failing test name and its short traceback.

## 3 — If tests passed → run coverage

```bash
cd week4 && PYTHONPATH=. pytest -q $ARGUMENTS --tb=short \
  --cov=backend/app --cov-report=term-missing 2>&1
```

Report the overall coverage % and list every line range that is not covered
(from the `TOTAL` row and the per-file `Missing` column).

## 4 — Summarise results

Present a concise Markdown table:

| # | Test name | Status | Failure reason (1 line) |
|---|-----------|--------|------------------------|
| 1 | … | PASS/FAIL | … |

Then write a short **"Coverage gaps"** section (skip if coverage ≥ 90 %).

## 5 — Suggest next steps

For each failing test produce a numbered action:
- Quote the exact assertion that failed.
- Point to the relevant source file and line.
- Suggest the minimal code change needed (do NOT apply it automatically).

If all tests pass, congratulate and recommend writing a new test for any
uncovered lines identified above.

## Safety notes
- Never modify source files in this step; only report.
- Do not `--forked` or spin up extra processes.
- The command is idempotent: re-running it is always safe.