---
description: "Sync docs/API.md with the live OpenAPI spec and list route deltas"
allowed-tools: ["bash", "read", "edit", "write"]
---

# Docs Sync

Synchronise `week4/docs/API.md` so it accurately reflects the current FastAPI OpenAPI spec.

## Arguments

Optional: `$ARGUMENTS` — base URL of the running server (default: `http://localhost:8000`).

## Steps

1. **Fetch the live OpenAPI JSON**

   Run the following to get the spec (use the provided base URL or fall back to the default):

   ```bash
   BASE_URL="${ARGUMENTS:-http://localhost:8000}"
   curl -sf "$BASE_URL/openapi.json" -o /tmp/openapi_current.json \
     || (echo "Server not running – falling back to static inspection" && \
         cd week4 && PYTHONPATH=. python - <<'EOF'
import json
from backend.app.main import app
print(json.dumps(app.openapi(), indent=2))
EOF
     ) > /tmp/openapi_current.json
   cat /tmp/openapi_current.json
   ```

2. **Read the current `docs/API.md`** (if it exists) and note every route it documents.

3. **Compare routes**

   From the OpenAPI JSON, extract every `(METHOD, path)` pair from `.paths`.
   Compare them against whatever is documented in `week4/docs/API.md`.
   Produce a **diff-like summary**:

   - `+ ADDED`   — routes in the spec but not in the docs
   - `- REMOVED` — routes in the docs but not in the spec
   - `~ CHANGED` — routes whose request body or response schema differs

4. **Rewrite `week4/docs/API.md`**

   Overwrite the file with a clean, up-to-date reference document that includes:

   - A brief intro paragraph.
   - One section per tag (e.g. `## Notes`, `## Action Items`).
   - For each endpoint:
     - HTTP method + path (e.g. `### GET /notes/`)
     - One-line description (from `summary` or `description` in the spec)
     - **Request** block – query params and/or JSON body schema (field, type, required/optional)
     - **Response** block – HTTP status codes and their JSON shape
     - A minimal `curl` example

5. **Output a summary** like:

   ```
   ✅ docs/API.md updated
   + ADDED:   POST /notes/{note_id}/extract
   ~ CHANGED: GET  /notes/search/ (new `tag` query param)
   TODOs:
   - Verify curl examples against real responses
   ```

6. If **no server is reachable** and the Python fallback also fails, read
   `week4/backend/app/routers/*.py` directly to infer routes, then proceed
   with steps 3-5 using that information instead.

> **Safety note:** this command only reads source files and writes to
> `week4/docs/API.md`. It does not modify any Python source or test files.
> Re-running is fully idempotent – it is safe to run at any time.