from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------
class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Note title")
    content: str = Field(..., min_length=1, description="Note body text")


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime


class NotePatch(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = Field(None, min_length=1)


# ---------------------------------------------------------------------------
# Action Items
# ---------------------------------------------------------------------------
class ActionItemCreate(BaseModel):
    description: str = Field(..., min_length=1, description="Action item description")


class ActionItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime


class ActionItemPatch(BaseModel):
    description: str | None = Field(None, min_length=1)
    completed: bool | None = None


# ---------------------------------------------------------------------------
# Tags
# ---------------------------------------------------------------------------
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tag name")


class TagRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime


class NoteReadWithTags(NoteRead):
    """Note response that includes associated tags."""

    tags: list[TagRead] = []


# ---------------------------------------------------------------------------
# Extraction responses
# ---------------------------------------------------------------------------
class ExtractionResult(BaseModel):
    action_items: list[str]
    tags: list[str]
    priorities: list[str]
    deadlines: list[str]
