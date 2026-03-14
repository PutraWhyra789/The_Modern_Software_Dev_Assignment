from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Tag
from ..schemas import (
    ExtractionResult,
    NoteCreate,
    NotePatch,
    NoteReadWithTags,
    TagCreate,
    TagRead,
)
from ..services.extract import extract_all

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteReadWithTags])
def list_notes(
    db: Session = Depends(get_db),
    q: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort: str = Query("-created_at", description="Sort by field, prefix with - for desc"),
) -> list[NoteReadWithTags]:
    stmt = select(Note)
    if q:
        stmt = stmt.where((Note.title.contains(q)) | (Note.content.contains(q)))

    sort_field = sort.lstrip("-")
    order_fn = desc if sort.startswith("-") else asc
    if hasattr(Note, sort_field):
        stmt = stmt.order_by(order_fn(getattr(Note, sort_field)))
    else:
        stmt = stmt.order_by(desc(Note.created_at))

    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [NoteReadWithTags.model_validate(row) for row in rows]


@router.post("/", response_model=NoteReadWithTags, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteReadWithTags:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteReadWithTags.model_validate(note)


@router.get("/{note_id}", response_model=NoteReadWithTags)
def get_note(
    note_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
) -> NoteReadWithTags:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteReadWithTags.model_validate(note)


@router.patch("/{note_id}", response_model=NoteReadWithTags)
def patch_note(
    payload: NotePatch,
    note_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
) -> NoteReadWithTags:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    if payload.title is not None:
        note.title = payload.title
    if payload.content is not None:
        note.content = payload.content
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteReadWithTags.model_validate(note)


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
) -> None:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.flush()


# ---------------------------------------------------------------------------
# Extraction endpoint — analyse a note's content
# ---------------------------------------------------------------------------
@router.post("/{note_id}/extract", response_model=ExtractionResult)
def extract_note(
    note_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
) -> ExtractionResult:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    result = extract_all(note.content)
    return ExtractionResult(**result)


# ---------------------------------------------------------------------------
# Tag management for notes
# ---------------------------------------------------------------------------
@router.post("/{note_id}/tags", response_model=NoteReadWithTags, status_code=201)
def add_tag_to_note(
    payload: TagCreate,
    note_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
) -> NoteReadWithTags:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Re-use existing tag or create a new one
    tag = db.execute(select(Tag).where(Tag.name == payload.name)).scalar_one_or_none()
    if tag is None:
        tag = Tag(name=payload.name)
        db.add(tag)
        db.flush()

    if tag not in note.tags:
        note.tags.append(tag)
        db.flush()
    db.refresh(note)
    return NoteReadWithTags.model_validate(note)


@router.delete("/{note_id}/tags/{tag_id}", status_code=204)
def remove_tag_from_note(
    note_id: int = Path(..., gt=0),
    tag_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
) -> None:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    if tag in note.tags:
        note.tags.remove(tag)
        db.flush()


# ---------------------------------------------------------------------------
# Standalone tag endpoints
# ---------------------------------------------------------------------------
@router.get("/tags/all", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)) -> list[TagRead]:
    rows = db.execute(select(Tag).order_by(Tag.name)).scalars().all()
    return [TagRead.model_validate(row) for row in rows]
