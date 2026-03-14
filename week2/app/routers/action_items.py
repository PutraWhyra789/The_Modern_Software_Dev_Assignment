"""Action-item router.

Refactored with AI assistance (Exercise 3 & 4):
- Replaced raw Dict payloads with Pydantic schemas.
- Added response_model= to every endpoint.
- Added POST /extract-llm endpoint (Exercise 4).
- Improved error handling: 503 when LLM fails.
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ActionItemDetail,
    ActionItemOut,
    ExtractLLMRequest,
    ExtractRequest,
    ExtractResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


# ── Heuristic extraction ────────────────────────────────────────────────────

@router.post("/extract", response_model=ExtractResponse)
def extract(payload: ExtractRequest) -> ExtractResponse:
    """Extract action items using heuristic rules."""
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(text)

    items = extract_action_items(text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemOut(id=i, text=t) for i, t in zip(ids, items)],
    )


# ── LLM-powered extraction (Exercise 4) ────────────────────────────────────

@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(payload: ExtractLLMRequest) -> ExtractResponse:
    """Extract action items using an Ollama LLM."""
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="text is required")

    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(text)

    try:
        items = extract_action_items_llm(text)
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"LLM extraction failed: {exc}",
        ) from exc

    ids = db.insert_action_items(items, note_id=note_id)
    return ExtractResponse(
        note_id=note_id,
        items=[ActionItemOut(id=i, text=t) for i, t in zip(ids, items)],
    )


# ── List action items ───────────────────────────────────────────────────────

@router.get("", response_model=List[ActionItemDetail])
def list_all(note_id: Optional[int] = None) -> List[ActionItemDetail]:
    """Return all action items, optionally filtered by note_id."""
    rows = db.list_action_items(note_id=note_id)
    return [
        ActionItemDetail(
            id=r["id"],
            note_id=r["note_id"],
            text=r["text"],
            done=bool(r["done"]),
            created_at=r["created_at"],
        )
        for r in rows
    ]


# ── Mark done ───────────────────────────────────────────────────────────────

@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, payload: MarkDoneRequest) -> MarkDoneResponse:
    """Toggle the done state of an action item."""
    db.mark_action_item_done(action_item_id, payload.done)
    return MarkDoneResponse(id=action_item_id, done=payload.done)

