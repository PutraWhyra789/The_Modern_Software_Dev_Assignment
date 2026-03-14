# Week 6 Write-up

## Submission Details

Name: **Putra Whyra Pratama Setiawan** \
SUNet ID: **TODO** \
Citations: Semgrep rule docs: https://sg.run/KxApY, https://sg.run/yP1O, https://sg.run/vYrY, https://sg.run/J92w

This assignment took me about **2** hours to do.


## Brief findings overview

Semgrep scanned 20 files (10 Python, 1 JS, 1 YAML) using 256 rules and found **4 blocking SAST findings** across 2 files: `backend/app/main.py` and `backend/app/routers/notes.py`. No secrets or SCA findings were detected. All 4 findings represent genuine vulnerabilities — no false positives were identified. The issues fell into three categories: insecure network policy (wildcard CORS), insecure cryptography (MD5), and unsafe system calls (SQL injection via raw text, subprocess with shell=True).


## Fix #1

a. File and line(s)
> `week6/backend/app/main.py`, line 24

b. Rule/category Semgrep flagged
> `python.fastapi.security.wildcard-cors.wildcard-cors` — SAST

c. Brief risk description
> Setting `allow_origins=["*"]` permits any website or domain to make cross-origin requests to this API. This enables CSRF-style attacks and data exfiltration from authenticated user sessions, as the browser will not block requests from malicious third-party sites.

d. Your change (short code diff or explanation, AI coding tool usage)
> Changed using OpenCode as AI coding tool.
>
> **Before:**
> ```python
> app.add_middleware(
>     CORSMiddleware,
>     allow_origins=["*"],
> )
> ```
> **After:**
> ```python
> app.add_middleware(
>     CORSMiddleware,
>     allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
>     allow_methods=["GET", "POST", "PUT", "DELETE"],
>     allow_headers=["Content-Type", "Authorization"],
> )
> ```

e. Why this mitigates the issue
> Restricting `allow_origins` to an explicit allowlist of trusted domains ensures the browser enforces the Same-Origin Policy. Only requests originating from `localhost:8000` are permitted, blocking all unauthorized cross-origin requests from external domains.


## Fix #2

a. File and line(s)
> `week6/backend/app/routers/notes.py`, lines 71–79

b. Rule/category Semgrep flagged
> `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text` — SAST

c. Brief risk description
> Using `sqlalchemy.text()` with an f-string directly interpolates the user-supplied `q` parameter into raw SQL without any sanitization. An attacker can inject SQL metacharacters (e.g., `' OR '1'='1`) to manipulate the query, potentially exposing, modifying, or deleting all data in the database.

d. Your change (short code diff or explanation, AI coding tool usage)
> Changed using OpenCode as AI coding tool.
>
> **Before:**
> ```python
> sql = text(
>     f"""
>     SELECT id, title, content, created_at, updated_at
>     FROM notes
>     WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
>     ORDER BY created_at DESC
>     LIMIT 50
>     """
> )
> rows = db.execute(sql).all()
> ```
> **After:**
> ```python
> results = (
>     db.query(Note)
>     .filter(
>         or_(
>             Note.title.ilike(f"%{q}%"),
>             Note.content.ilike(f"%{q}%"),
>         )
>     )
>     .order_by(Note.created_at.desc())
>     .limit(50)
>     .all()
> )
> ```

e. Why this mitigates the issue
> SQLAlchemy ORM operators (`or_()`, `ilike()`) automatically parameterize all user inputs before passing them to the database driver. The `q` value is never interpolated directly into SQL string — it is passed as a bound parameter, making SQL injection structurally impossible regardless of input content.


## Fix #3

a. File and line(s)
> `week6/backend/app/routers/notes.py`, line 99 (`/debug/hash-md5` endpoint) and line 112 (`/debug/run` endpoint)

b. Rule/category Semgrep flagged
> Fix #3a: `python.lang.security.insecure-hash-algorithms-md5.insecure-hash-algorithm-md5` — SAST  
> Fix #3b: `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true` — SAST

c. Brief risk description
> **MD5:** MD5 is cryptographically broken — collision attacks are computationally feasible, making it unsuitable for any security-sensitive hashing such as integrity checks or fingerprinting.  
> **subprocess shell=True:** Spawning a subprocess with `shell=True` passes the command string through a shell interpreter (`/bin/sh` or `cmd.exe`). If any part of `cmd` contains user-supplied input, shell metacharacters (`; | && $(...)`) can be used to execute arbitrary system commands (command injection).

d. Your change (short code diff or explanation, AI coding tool usage)
> Changed using OpenCode as AI coding tool.
>
> **Before (MD5):**
> ```python
> return {"algo": "md5", "hex": hashlib.md5(q.encode()).hexdigest()}
> ```
> **After (MD5):**
> ```python
> return {"algo": "sha256", "hex": hashlib.sha256(q.encode()).hexdigest()}
> ```
>
> **Before (subprocess):**
> ```python
> completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
> ```
> **After (subprocess):**
> ```python
> import shlex
> completed = subprocess.run(shlex.split(cmd), shell=False, capture_output=True, text=True)
> ```

e. Why this mitigates the issue
> **MD5 → SHA256:** SHA-256 is collision-resistant under current computational limits and meets NIST cryptographic standards, making hash-based integrity checks reliable.  
> **shell=False + shlex.split():** With `shell=False`, the OS executes the binary directly without invoking a shell interpreter, so metacharacters in input have no special meaning. `shlex.split()` correctly tokenizes the command string into a safe argument list, preventing injection entirely.
