"""Notes router.

Refactored with AI assistance (Exercise 3 & 4):
- Replaced raw Dict payloads with Pydantic schemas.
- Added response_model= to every endpoint.
- Added GET /notes endpoint to list all notes (Exercise 4).
- Improved error handling: 404 when note not found.
"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import NoteCreate, NoteOut


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteOut)
def create_note(payload: NoteCreate) -> NoteOut:
    """Create a new note."""
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    note_id = db.insert_note(content)
    note = db.get_note(note_id)
    return NoteOut(id=note["id"], content=note["content"], created_at=note["created_at"])


# ── List all notes (Exercise 4) ─────────────────────────────────────────────

@router.get("", response_model=List[NoteOut])
def list_notes() -> List[NoteOut]:
    """Return all notes ordered by most recent first."""
    rows = db.list_notes()
    return [
        NoteOut(id=r["id"], content=r["content"], created_at=r["created_at"])
        for r in rows
    ]


@router.get("/{note_id}", response_model=NoteOut)
def get_single_note(note_id: int) -> NoteOut:
    """Retrieve a single note by ID."""
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return NoteOut(id=row["id"], content=row["content"], created_at=row["created_at"])

