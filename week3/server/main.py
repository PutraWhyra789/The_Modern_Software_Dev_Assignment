"""
GitHub MCP Server — wraps the GitHub REST API using FastMCP.

Exposes five tools, two resources, and two prompts for use by MCP clients
such as Claude Desktop.  Authentication is optional: set the GITHUB_TOKEN
environment variable for higher rate limits and write operations; without it
the server falls back to unauthenticated read-only access (60 req/h).

Transport: STDIO (default).  Run with:
    uv run python week3/server/main.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Load .env from the week3 directory (one level up from this file).
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN: Optional[str] = os.environ.get("GITHUB_TOKEN")
RATE_LIMIT_WARNING_THRESHOLD = 20

mcp = FastMCP(
    "GitHub MCP Server",
    instructions="An MCP server that exposes GitHub REST API functionality.",
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _headers() -> dict[str, str]:
    """Return common request headers, including auth if a token is available."""
    h: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h


def _check_rate_limit(response: httpx.Response) -> None:
    """Emit a warning to stderr when the remaining rate‑limit budget is low."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    if remaining is not None:
        try:
            if int(remaining) < RATE_LIMIT_WARNING_THRESHOLD:
                print(
                    f"[WARNING] GitHub API rate‑limit nearly exhausted — "
                    f"{remaining} requests remaining.",
                    file=sys.stderr,
                )
        except ValueError:
            pass


def _error_text(response: httpx.Response, context: str) -> str:
    """Return a human‑readable error string for a failed HTTP response."""
    return f"{context} ({response.status_code}). GitHub says: {response.text}"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def search_repos(query: str, max_results: int = 5) -> str:
    """Search GitHub repositories by keyword.

    Args:
        query: Search keywords (same syntax as the GitHub search bar).
        max_results: Maximum number of results to return (1‑100, default 5).
    """
    max_results = max(1, min(max_results, 100))
    try:
        with httpx.Client() as client:
            resp = client.get(
                f"{GITHUB_API}/search/repositories",
                headers=_headers(),
                params={"q": query, "per_page": max_results},
                timeout=15,
            )
            _check_rate_limit(resp)
            if resp.status_code != 200:
                return _error_text(resp, f"Repository search failed for '{query}'")
            data = resp.json()
            items = data.get("items", [])
            if not items:
                return f"No repositories found for query '{query}'."
            lines: list[str] = [f"Found {data['total_count']} repositories (showing top {len(items)}):\n"]
            for repo in items:
                stars = repo.get("stargazers_count", 0)
                desc = repo.get("description") or "No description"
                lines.append(f"- **{repo['full_name']}** ⭐ {stars}\n  {desc}\n  {repo['html_url']}")
            return "\n".join(lines)
    except httpx.TimeoutException:
        return f"Request timed out while searching for '{query}'. Please try again."
    except httpx.HTTPError as exc:
        return f"HTTP error during search: {exc}"


@mcp.tool()
def get_repo(owner: str, repo: str) -> str:
    """Get detailed information about a specific GitHub repository.

    Args:
        owner: Repository owner (user or organisation).
        repo: Repository name.
    """
    try:
        with httpx.Client() as client:
            resp = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}",
                headers=_headers(),
                timeout=15,
            )
            _check_rate_limit(resp)
            if resp.status_code == 404:
                return f"Repository '{owner}/{repo}' not found (404). Check the owner/repo name."
            if resp.status_code != 200:
                return _error_text(resp, f"Failed to fetch repository '{owner}/{repo}'")
            r = resp.json()
            parts = [
                f"# {r['full_name']}",
                f"**Description:** {r.get('description') or 'N/A'}",
                f"**Language:** {r.get('language') or 'N/A'}",
                f"**Stars:** {r.get('stargazers_count', 0)} | **Forks:** {r.get('forks_count', 0)} | **Open issues:** {r.get('open_issues_count', 0)}",
                f"**Created:** {r.get('created_at', 'N/A')} | **Updated:** {r.get('updated_at', 'N/A')}",
                f"**Default branch:** {r.get('default_branch', 'N/A')}",
                f"**License:** {r.get('license', {}).get('spdx_id', 'N/A') if r.get('license') else 'N/A'}",
                f"**URL:** {r['html_url']}",
            ]
            return "\n".join(parts)
    except httpx.TimeoutException:
        return f"Request timed out while fetching '{owner}/{repo}'."
    except httpx.HTTPError as exc:
        return f"HTTP error fetching repository: {exc}"


@mcp.tool()
def list_issues(owner: str, repo: str, state: str = "open", max_results: int = 10) -> str:
    """List issues for a GitHub repository.

    Args:
        owner: Repository owner.
        repo: Repository name.
        state: Issue state filter — 'open', 'closed', or 'all' (default 'open').
        max_results: Maximum number of issues to return (1‑100, default 10).
    """
    if state not in ("open", "closed", "all"):
        state = "open"
    max_results = max(1, min(max_results, 100))
    try:
        with httpx.Client() as client:
            resp = client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/issues",
                headers=_headers(),
                params={"state": state, "per_page": max_results},
                timeout=15,
            )
            _check_rate_limit(resp)
            if resp.status_code == 404:
                return f"Repository '{owner}/{repo}' not found (404). Check the owner/repo name."
            if resp.status_code != 200:
                return _error_text(resp, f"Failed to list issues for '{owner}/{repo}'")
            issues = resp.json()
            if not issues:
                return f"No {state} issues found in {owner}/{repo}."
            lines: list[str] = [f"**{state.capitalize()} issues in {owner}/{repo}** (showing {len(issues)}):\n"]
            for issue in issues:
                labels = ", ".join(l["name"] for l in issue.get("labels", []))
                label_str = f" [{labels}]" if labels else ""
                lines.append(
                    f"- #{issue['number']} {issue['title']}{label_str}\n"
                    f"  State: {issue['state']} | Author: {issue['user']['login']} | "
                    f"Comments: {issue.get('comments', 0)}\n"
                    f"  {issue['html_url']}"
                )
            return "\n".join(lines)
    except httpx.TimeoutException:
        return f"Request timed out while listing issues for '{owner}/{repo}'."
    except httpx.HTTPError as exc:
        return f"HTTP error listing issues: {exc}"


@mcp.tool()
def create_issue(owner: str, repo: str, title: str, body: str = "", labels: str = "") -> str:
    """Create a new issue in a GitHub repository (requires GITHUB_TOKEN).

    Args:
        owner: Repository owner.
        repo: Repository name.
        title: Issue title.
        body: Issue body / description (Markdown supported).
        labels: Comma‑separated label names to apply.
    """
    if not GITHUB_TOKEN:
        return (
            "Cannot create issue: GITHUB_TOKEN environment variable is not set. "
            "A Personal Access Token with 'repo' scope is required for write operations."
        )
    payload: dict = {"title": title}
    if body:
        payload["body"] = body
    if labels:
        payload["labels"] = [l.strip() for l in labels.split(",") if l.strip()]
    try:
        with httpx.Client() as client:
            resp = client.post(
                f"{GITHUB_API}/repos/{owner}/{repo}/issues",
                headers=_headers(),
                json=payload,
                timeout=15,
            )
            _check_rate_limit(resp)
            if resp.status_code == 404:
                return f"Repository '{owner}/{repo}' not found (404). Check the owner/repo name."
            if resp.status_code == 403:
                return f"Permission denied (403). Your token may lack the 'repo' scope."
            if resp.status_code not in (200, 201):
                return _error_text(resp, f"Failed to create issue in '{owner}/{repo}'")
            issue = resp.json()
            return (
                f"Issue created successfully!\n"
                f"- **#{issue['number']}** {issue['title']}\n"
                f"- URL: {issue['html_url']}"
            )
    except httpx.TimeoutException:
        return f"Request timed out while creating issue in '{owner}/{repo}'."
    except httpx.HTTPError as exc:
        return f"HTTP error creating issue: {exc}"


@mcp.tool()
def get_user(username: str) -> str:
    """Get public profile information for a GitHub user.

    Args:
        username: GitHub username.
    """
    try:
        with httpx.Client() as client:
            resp = client.get(
                f"{GITHUB_API}/users/{username}",
                headers=_headers(),
                timeout=15,
            )
            _check_rate_limit(resp)
            if resp.status_code == 404:
                return f"User '{username}' not found (404). Check the username."
            if resp.status_code != 200:
                return _error_text(resp, f"Failed to fetch user '{username}'")
            u = resp.json()
            parts = [
                f"# {u.get('name') or u['login']}",
                f"**Username:** {u['login']}",
                f"**Bio:** {u.get('bio') or 'N/A'}",
                f"**Company:** {u.get('company') or 'N/A'}",
                f"**Location:** {u.get('location') or 'N/A'}",
                f"**Public repos:** {u.get('public_repos', 0)} | **Followers:** {u.get('followers', 0)} | **Following:** {u.get('following', 0)}",
                f"**Profile:** {u['html_url']}",
            ]
            return "\n".join(parts)
    except httpx.TimeoutException:
        return f"Request timed out while fetching user '{username}'."
    except httpx.HTTPError as exc:
        return f"HTTP error fetching user: {exc}"


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------


@mcp.resource("github://repo/{owner}/{repo}")
def repo_resource(owner: str, repo: str) -> str:
    """Retrieve repository information as a resource."""
    return get_repo(owner, repo)


@mcp.resource("github://user/{username}")
def user_resource(username: str) -> str:
    """Retrieve GitHub user profile as a resource."""
    return get_user(username)


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------


@mcp.prompt()
def triage_issues(owner: str, repo: str) -> str:
    """Guide an AI model to categorise and prioritise open issues for a repository.

    Args:
        owner: Repository owner.
        repo: Repository name.
    """
    return (
        f"Please triage the open issues in the GitHub repository **{owner}/{repo}**.\n\n"
        "For each issue:\n"
        "1. Read the title, body, and any labels.\n"
        "2. Assign a **category** (bug, feature request, documentation, question, chore).\n"
        "3. Assign a **priority** (critical, high, medium, low).\n"
        "4. Write a one‑sentence **rationale** for the priority.\n\n"
        "Start by calling the `list_issues` tool to fetch the current open issues, "
        "then present your triage as a structured list."
    )


@mcp.prompt()
def repo_health_summary(owner: str, repo: str) -> str:
    """Generate a health report for a GitHub repository.

    Args:
        owner: Repository owner.
        repo: Repository name.
    """
    return (
        f"Please produce a health summary for the GitHub repository **{owner}/{repo}**.\n\n"
        "Include the following sections:\n"
        "1. **Overview** — stars, forks, language, licence, last update.\n"
        "2. **Issue health** — open vs. closed ratio, stale issues (>90 days without activity).\n"
        "3. **Community signals** — contributor count, recent commit activity.\n"
        "4. **Recommendations** — actionable suggestions to improve project health.\n\n"
        "Use the `get_repo` and `list_issues` tools to gather the data you need."
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Log startup info to stderr (stdout is reserved for JSON‑RPC over STDIO).
    auth_status = "authenticated" if GITHUB_TOKEN else "unauthenticated (60 req/h limit)"
    print(f"[INFO] Starting GitHub MCP Server ({auth_status})", file=sys.stderr)
    mcp.run(transport="stdio")
