# Week 3 — GitHub MCP Server

A Model Context Protocol (MCP) server that wraps the GitHub REST API, built with Python and [FastMCP](https://github.com/jlowin/fastmcp). Designed for STDIO transport and tested with the MCP Inspector and Claude Desktop.

## Features

| Category   | Items |
|------------|-------|
| **Tools**  | `search_repos`, `get_repo`, `list_issues`, `create_issue`, `get_user` |
| **Resources** | `github://repo/{owner}/{repo}`, `github://user/{username}` |
| **Prompts** | `triage_issues`, `repo_health_summary` |

## Prerequisites

- Python ≥ 3.10
- [`uv`](https://docs.astral.sh/uv/) (used at the repo root for dependency management)
- [Node.js](https://nodejs.org/) (for the MCP Inspector dev tool)
- (Optional) A [GitHub Personal Access Token](https://github.com/settings/tokens) for higher rate limits and write operations

## Setup

From the **repository root**:

```bash
# Install dependencies (including fastmcp and httpx)
uv sync
```

### Environment variables

| Variable       | Required | Description |
|----------------|----------|-------------|
| `GITHUB_TOKEN` | No       | GitHub PAT. Without it the server runs in read-only mode (60 requests/hour). |

Create a `.env` file in the `week3/` directory:

```
GITHUB_TOKEN=ghp_your_token_here
```

The server automatically loads this file on startup via `python-dotenv`.

## Running the server

```bash
uv run python week3/server/main.py
```

The server starts on **STDIO transport**. All log/warning output goes to `stderr`; `stdout` is reserved for JSON-RPC communication.

## Configuring Claude Desktop

Add the following to your Claude Desktop MCP configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "github": {
      "command": "uv",
      "args": ["run", "python", "week3/server/main.py"],
      "cwd": "/path/to/repo/root",
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

## Tool reference

### `search_repos`
Search GitHub repositories by keyword.

**Parameters:**
- `query` (str, required) — Search keywords.
- `max_results` (int, optional, default 5) — Number of results (1–100).

**Example input:** `search_repos(query="fastmcp python", max_results=3)`

---

### `get_repo`
Get detailed information about a specific repository.

**Parameters:**
- `owner` (str, required) — Repository owner.
- `repo` (str, required) — Repository name.

**Example input:** `get_repo(owner="jlowin", repo="fastmcp")`

---

### `list_issues`
List issues for a repository.

**Parameters:**
- `owner` (str, required) — Repository owner.
- `repo` (str, required) — Repository name.
- `state` (str, optional, default `"open"`) — `"open"`, `"closed"`, or `"all"`.
- `max_results` (int, optional, default 10) — Number of results (1–100).

**Example input:** `list_issues(owner="python", repo="cpython", state="open", max_results=5)`

---

### `create_issue`
Create a new issue (requires `GITHUB_TOKEN` with `repo` scope).

**Parameters:**
- `owner` (str, required) — Repository owner.
- `repo` (str, required) — Repository name.
- `title` (str, required) — Issue title.
- `body` (str, optional) — Issue body (Markdown).
- `labels` (str, optional) — Comma-separated label names.

**Example input:** `create_issue(owner="myorg", repo="myproject", title="Bug: login fails", body="Steps to reproduce...", labels="bug, urgent")`

---

### `get_user`
Get public profile information for a GitHub user.

**Parameters:**
- `username` (str, required) — GitHub username.

**Example input:** `get_user(username="octocat")`

## Testing with MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) provides a web UI to interactively test your server's tools, resources, and prompts without needing Claude Desktop.

### Starting the Inspector

From the **repository root**:

```bash
npx @modelcontextprotocol/inspector uv run python week3/server/main.py
```

This starts two processes: the MCP server and the Inspector web UI. Open your browser at `http://localhost:6274`.

### Using the Inspector

**1. Tools tab**
- Select a tool from the sidebar (e.g. `search_repos`).
- Fill in the required parameters in the form (e.g. `query`: `"python mcp"`, `max_results`: `3`).
- Click **Run Tool** to execute and see the formatted response.
- Try each tool:
  - `search_repos` — search repositories by keyword.
  - `get_repo` — enter `owner` and `repo` to get detailed repo info.
  - `list_issues` — list open/closed issues for a repo.
  - `create_issue` — create a new issue (requires valid `GITHUB_TOKEN`).
  - `get_user` — enter a GitHub username to view their profile.

**2. Resources tab**
- Browse the available resource URI templates:
  - `github://repo/{owner}/{repo}` — returns repository details.
  - `github://user/{username}` — returns user profile information.
- Fill in the URI parameters and click **Read Resource** to fetch the data.

**3. Prompts tab**
- Select a prompt (`triage_issues` or `repo_health_summary`).
- Provide the `owner` and `repo` arguments.
- The Inspector shows the generated prompt text that an AI model would receive.

## Example invocation flow (Claude Desktop)

1. Start the server via Claude Desktop config (see above).
2. In Claude Desktop, type: *"Search for popular Python MCP libraries on GitHub"*
3. Claude will call `search_repos(query="python mcp library")` and present the results.
4. Follow up: *"Show me the issues for the top result"*
5. Claude calls `list_issues` on the repository and displays them.
6. Ask: *"Triage these issues by priority"* — this triggers the `triage_issues` prompt flow.

## Design decisions

- **Descriptive error messages** — tools return human-readable error strings instead of raising exceptions, so the AI agent can relay errors to the user.
- **Rate-limit monitoring** — every response checks `X-RateLimit-Remaining` and emits a warning to `stderr` when the budget drops below 20 requests.
- **stderr for logging** — all diagnostic output goes to `stderr` to avoid corrupting the JSON-RPC stream on `stdout`.
- **Optional auth** — the server degrades gracefully without a token, supporting read-only operations at the unauthenticated rate limit.
