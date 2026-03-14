# API Reference

Base URL: `http://localhost:8000`

---

## Notes

### `GET /notes/`
List notes with optional search, pagination, and sorting.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `q` | string | — | Search title and content |
| `skip` | int (>= 0) | 0 | Offset for pagination |
| `limit` | int (1–200) | 50 | Page size |
| `sort` | string | `-created_at` | Sort field; prefix `-` for descending |

**Response:** `200` — `NoteReadWithTags[]`

### `POST /notes/`
Create a new note.

| Field | Type | Constraints |
|-------|------|-------------|
| `title` | string | 1–200 chars, required |
| `content` | string | >= 1 char, required |

**Response:** `201` — `NoteReadWithTags`

### `GET /notes/{note_id}`
Get a single note by ID.

**Response:** `200` — `NoteReadWithTags` | `404`

### `PATCH /notes/{note_id}`
Partially update a note.

| Field | Type | Constraints |
|-------|------|-------------|
| `title` | string or null | 1–200 chars if provided |
| `content` | string or null | >= 1 char if provided |

**Response:** `200` — `NoteReadWithTags` | `404`

### `DELETE /notes/{note_id}`
Delete a note.

**Response:** `204` | `404`

### `POST /notes/{note_id}/extract`
Run extraction analysis on the note's content. Returns action items, tags, priorities, and deadlines.

**Response:** `200` — `ExtractionResult` | `404`

```json
{
  "action_items": ["TODO: fix tests"],
  "tags": ["backend"],
  "priorities": ["P1"],
  "deadlines": ["2025-06-01"]
}
```

---

## Tags

### `POST /notes/{note_id}/tags`
Add a tag to a note (creates the tag if it doesn't exist).

| Field | Type | Constraints |
|-------|------|-------------|
| `name` | string | 1–100 chars, required |

**Response:** `201` — `NoteReadWithTags` | `404`

### `DELETE /notes/{note_id}/tags/{tag_id}`
Remove a tag from a note.

**Response:** `204` | `404`

### `GET /notes/tags/all`
List all tags.

**Response:** `200` — `TagRead[]`

---

## Action Items

### `GET /action-items/`
List action items with optional filters, pagination, and sorting.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `completed` | bool | — | Filter by completion status |
| `skip` | int (>= 0) | 0 | Offset for pagination |
| `limit` | int (1–200) | 50 | Page size |
| `sort` | string | `-created_at` | Sort field; prefix `-` for descending |

**Response:** `200` — `ActionItemRead[]`

### `POST /action-items/`
Create a new action item.

| Field | Type | Constraints |
|-------|------|-------------|
| `description` | string | >= 1 char, required |

**Response:** `201` — `ActionItemRead`

### `GET /action-items/{item_id}`
Get a single action item by ID.

**Response:** `200` — `ActionItemRead` | `404`

### `PUT /action-items/{item_id}/complete`
Mark an action item as completed.

**Response:** `200` — `ActionItemRead` | `404`

### `PATCH /action-items/{item_id}`
Partially update an action item.

| Field | Type | Constraints |
|-------|------|-------------|
| `description` | string or null | >= 1 char if provided |
| `completed` | bool or null | — |

**Response:** `200` — `ActionItemRead` | `404`

### `DELETE /action-items/{item_id}`
Delete an action item.

**Response:** `204` | `404`

---

## Schemas

### NoteReadWithTags
```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z",
  "tags": [{"id": 1, "name": "string", "created_at": "2025-01-01T00:00:00Z"}]
}
```

### ActionItemRead
```json
{
  "id": 1,
  "description": "string",
  "completed": false,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### TagRead
```json
{
  "id": 1,
  "name": "string",
  "created_at": "2025-01-01T00:00:00Z"
}
```
