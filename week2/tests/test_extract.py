"""
Unit tests for heuristic and LLM-powered action-item extraction.

Generated with AI assistance for Exercise 2.
Uses unittest.mock.patch to mock ollama.chat so tests are fast, isolated, and
deterministic — no live Ollama instance required.
"""
import json
import os
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


# ── Helpers ──────────────────────────────────────────────────────────────────

def _mock_ollama_response(items: list[str]) -> MagicMock:
    """Build a mock return value that mimics an ollama.chat response."""
    mock_resp = MagicMock()
    mock_resp.message.content = json.dumps({"items": items})
    return mock_resp


# ═══════════════════════════════════════════════════════════════════════════
#  Heuristic extraction tests (original function)
# ═══════════════════════════════════════════════════════════════════════════


def test_extract_bullets_and_checkboxes():
    """Bullet lists and checkboxes are correctly extracted."""
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_extract_keyword_prefixes():
    """Lines starting with TODO:/ACTION:/NEXT: are extracted."""
    text = "TODO: Deploy staging\nACTION: Review PR\nNEXT: Write docs"
    items = extract_action_items(text)
    assert len(items) == 3


def test_extract_empty_input():
    """Empty string yields no action items."""
    assert extract_action_items("") == []


def test_extract_whitespace_only():
    """Whitespace-only input yields no action items."""
    assert extract_action_items("   \n\n  \t  ") == []


# ═══════════════════════════════════════════════════════════════════════════
#  LLM-powered extraction tests (mocked)
# ═══════════════════════════════════════════════════════════════════════════


@patch("week2.app.services.extract.chat")
def test_llm_bullet_list(mock_chat):
    """LLM correctly returns items from a bullet list input."""
    expected = ["Set up database", "Implement API endpoint", "Write tests"]
    mock_chat.return_value = _mock_ollama_response(expected)

    result = extract_action_items_llm("- Set up database\n- Implement API endpoint\n- Write tests")
    assert result == expected


@patch("week2.app.services.extract.chat")
def test_llm_keyword_prefix(mock_chat):
    """LLM correctly returns items from keyword-prefixed lines."""
    expected = ["Deploy staging", "Review PR"]
    mock_chat.return_value = _mock_ollama_response(expected)

    result = extract_action_items_llm("TODO: Deploy staging\nACTION: Review PR")
    assert result == expected


def test_llm_empty_input():
    """Empty string short-circuits without calling Ollama."""
    result = extract_action_items_llm("")
    assert result == []


def test_llm_whitespace_only():
    """Whitespace-only input short-circuits without calling Ollama."""
    result = extract_action_items_llm("   \n\t  ")
    assert result == []


@patch("week2.app.services.extract.chat")
def test_llm_prose_input(mock_chat):
    """LLM extracts action items from unstructured prose."""
    expected = ["Schedule follow-up meeting", "Send report to client"]
    mock_chat.return_value = _mock_ollama_response(expected)

    result = extract_action_items_llm(
        "We discussed the project timeline. Need to schedule a follow-up meeting "
        "and send the report to the client by Friday."
    )
    assert result == expected


@patch("week2.app.services.extract.chat")
def test_llm_no_items_found(mock_chat):
    """LLM returns empty list when no action items are found."""
    mock_chat.return_value = _mock_ollama_response([])

    result = extract_action_items_llm("The weather was nice today.")
    assert result == []


@patch("week2.app.services.extract.chat")
def test_llm_single_item(mock_chat):
    """LLM handles a single action item correctly."""
    expected = ["Buy groceries"]
    mock_chat.return_value = _mock_ollama_response(expected)

    result = extract_action_items_llm("Remember to buy groceries.")
    assert result == expected


@patch("week2.app.services.extract.chat")
def test_llm_system_message_sent(mock_chat):
    """Verify that a system message is included in the ollama.chat call."""
    mock_chat.return_value = _mock_ollama_response(["Test"])

    extract_action_items_llm("Some notes")

    call_args = mock_chat.call_args
    messages = call_args.kwargs.get("messages") or call_args[1].get("messages")
    system_msgs = [m for m in messages if m["role"] == "system"]
    assert len(system_msgs) == 1, "Expected exactly one system message"
    assert "action" in system_msgs[0]["content"].lower()


@patch("week2.app.services.extract.chat")
def test_llm_user_message_sent(mock_chat):
    """Verify that the user's text is forwarded as a user message."""
    mock_chat.return_value = _mock_ollama_response(["Test"])
    user_text = "Please review the pull request and deploy to staging."

    extract_action_items_llm(user_text)

    call_args = mock_chat.call_args
    messages = call_args.kwargs.get("messages") or call_args[1].get("messages")
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) == 1, "Expected exactly one user message"
    assert user_msgs[0]["content"] == user_text


@patch("week2.app.services.extract.chat")
def test_llm_structured_format_passed(mock_chat):
    """Verify that the Pydantic JSON schema is passed as format= to ollama.chat."""
    mock_chat.return_value = _mock_ollama_response([])

    extract_action_items_llm("Some text")

    call_args = mock_chat.call_args
    fmt = call_args.kwargs.get("format") or call_args[1].get("format")
    assert fmt is not None, "format= should be set"
    assert "items" in str(fmt), "Schema should reference 'items' key"
