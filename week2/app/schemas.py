"""
Pydantic v2 schemas for request/response contracts.

Generated with AI assistance for Exercise 1 (LLM schema) and Exercise 3 (refactor).
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


# ── LLM Structured Output Schema (Exercise 1) ──────────────────────────────

class ActionItemsResponse(BaseModel):
    """Schema passed to Ollama `format=` so the model returns valid JSON."""

    items: List[str] = Field(
        default_factory=list,
        description="List of extracted action-item strings.",
    )


# ── Note Schemas (Exercise 3 refactor) ──────────────────────────────────────

class NoteCreate(BaseModel):
    """Payload for creating a new note."""

    content: str = Field(..., min_length=1, description="Raw note text.")


class NoteOut(BaseModel):
    """Response representation of a stored note."""

    id: int = Field(..., description="Primary key of the note.")
    content: str = Field(..., description="Raw note text.")
    created_at: str = Field(..., description="ISO-8601 creation timestamp.")


# ── Action-Item Schemas (Exercise 3 refactor) ───────────────────────────────

class ExtractRequest(BaseModel):
    """Payload for the heuristic extraction endpoint."""

    text: str = Field(..., min_length=1, description="Free-form notes to analyse.")
    save_note: bool = Field(default=True, description="Whether to persist the note.")


class ExtractLLMRequest(BaseModel):
    """Payload for the LLM-powered extraction endpoint."""

    text: str = Field(..., min_length=1, description="Free-form notes to analyse.")
    save_note: bool = Field(default=True, description="Whether to persist the note.")


class ActionItemOut(BaseModel):
    """Single action item returned to the client."""

    id: int = Field(..., description="Primary key of the action item.")
    text: str = Field(..., description="Action item description.")


class ExtractResponse(BaseModel):
    """Response after extracting action items."""

    note_id: Optional[int] = Field(None, description="ID of the saved note, if any.")
    items: List[ActionItemOut] = Field(
        default_factory=list, description="Extracted action items."
    )


class ActionItemDetail(BaseModel):
    """Full detail of an action item (used in list endpoints)."""

    id: int = Field(..., description="Primary key.")
    note_id: Optional[int] = Field(None, description="Associated note ID.")
    text: str = Field(..., description="Action item text.")
    done: bool = Field(False, description="Completion flag.")
    created_at: str = Field(..., description="ISO-8601 creation timestamp.")


class MarkDoneRequest(BaseModel):
    """Payload for toggling an action item's done state."""

    done: bool = Field(True, description="New completion state.")


class MarkDoneResponse(BaseModel):
    """Response after toggling done state."""

    id: int = Field(..., description="Action item ID.")
    done: bool = Field(..., description="Updated done state.")
