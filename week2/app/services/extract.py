"""Service layer for action-item extraction.

Contains both heuristic-based and LLM-powered extraction functions.
Generated / modified with AI assistance (Exercises 1 & 3).
"""
from __future__ import annotations

import os
import re
from typing import Any, List

from ollama import chat
from dotenv import load_dotenv

from ..schemas import ActionItemsResponse

load_dotenv()

# ── Constants ────────────────────────────────────────────────────────────────

# Default Ollama model – override via OLLAMA_MODEL env var
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")

BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters


# ── LLM-powered extraction (Exercise 1) ─────────────────────────────────────

def extract_action_items_llm(text: str) -> List[str]:
    """Extract action items from *text* using an Ollama LLM with structured outputs.

    The model is instructed to return a JSON object matching
    :class:`ActionItemsResponse` so the output is always parseable.

    Returns an empty list when *text* is blank or whitespace-only (short-circuit
    to avoid unnecessary LLM calls – defensive programming).
    """
    # Short-circuit: empty / whitespace-only input → no action items
    if not text or not text.strip():
        return []

    response = chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that extracts actionable to-do items "
                    "from the user's notes. Return ONLY a JSON object with an 'items' "
                    "key containing a list of concise action-item strings. "
                    "If there are no action items, return {\"items\": []}."
                ),
            },
            {
                "role": "user",
                "content": text,
            },
        ],
        format=ActionItemsResponse.model_json_schema(),
    )

    # Parse structured output via Pydantic for safety
    parsed = ActionItemsResponse.model_validate_json(response.message.content)
    return parsed.items
