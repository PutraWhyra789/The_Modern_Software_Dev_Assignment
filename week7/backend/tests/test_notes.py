# ---------------------------------------------------------------------------
# Basic CRUD (existing coverage, expanded)
# ---------------------------------------------------------------------------
def test_create_list_and_patch_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"
    assert "created_at" in data and "updated_at" in data

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/", params={"q": "Hello", "limit": 10, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    note_id = data["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["title"] == "Updated"


# ---------------------------------------------------------------------------
# GET single note
# ---------------------------------------------------------------------------
def test_get_single_note(client):
    r = client.post("/notes/", json={"title": "Single", "content": "One"})
    note = r.json()

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Single"


def test_get_nonexistent_note_returns_404(client):
    r = client.get("/notes/9999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------
def test_delete_note(client):
    r = client.post("/notes/", json={"title": "Delete me", "content": "bye"})
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_nonexistent_note_returns_404(client):
    r = client.delete("/notes/9999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def test_create_note_empty_title_rejected(client):
    r = client.post("/notes/", json={"title": "", "content": "body"})
    assert r.status_code == 422


def test_create_note_empty_content_rejected(client):
    r = client.post("/notes/", json={"title": "ok", "content": ""})
    assert r.status_code == 422


def test_create_note_missing_fields_rejected(client):
    r = client.post("/notes/", json={})
    assert r.status_code == 422


def test_patch_note_empty_title_rejected(client):
    r = client.post("/notes/", json={"title": "Good", "content": "ok"})
    note_id = r.json()["id"]
    r = client.patch(f"/notes/{note_id}", json={"title": ""})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
def _seed_notes(client, count: int = 10) -> list[dict]:
    """Create *count* notes and return them in creation order."""
    notes = []
    for i in range(count):
        r = client.post("/notes/", json={"title": f"Note {i}", "content": f"Body {i}"})
        assert r.status_code == 201
        notes.append(r.json())
    return notes


def test_pagination_skip_and_limit(client):
    _seed_notes(client, 10)

    r = client.get("/notes/", params={"limit": 3, "skip": 0})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1) == 3

    r = client.get("/notes/", params={"limit": 3, "skip": 3})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) == 3

    # Pages should not overlap
    ids1 = {n["id"] for n in page1}
    ids2 = {n["id"] for n in page2}
    assert ids1.isdisjoint(ids2)


def test_pagination_limit_upper_bound(client):
    """Limit must be <= 200."""
    r = client.get("/notes/", params={"limit": 201})
    assert r.status_code == 422


def test_pagination_skip_negative_rejected(client):
    r = client.get("/notes/", params={"skip": -1})
    assert r.status_code == 422


def test_pagination_limit_zero_rejected(client):
    r = client.get("/notes/", params={"limit": 0})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------
def test_sort_notes_by_title_asc(client):
    client.post("/notes/", json={"title": "Banana", "content": "fruit"})
    client.post("/notes/", json={"title": "Apple", "content": "fruit"})
    client.post("/notes/", json={"title": "Cherry", "content": "fruit"})

    r = client.get("/notes/", params={"sort": "title"})
    assert r.status_code == 200
    titles = [n["title"] for n in r.json()]
    assert titles == sorted(titles)


def test_sort_notes_by_title_desc(client):
    client.post("/notes/", json={"title": "Banana", "content": "fruit"})
    client.post("/notes/", json={"title": "Apple", "content": "fruit"})
    client.post("/notes/", json={"title": "Cherry", "content": "fruit"})

    r = client.get("/notes/", params={"sort": "-title"})
    assert r.status_code == 200
    titles = [n["title"] for n in r.json()]
    assert titles == sorted(titles, reverse=True)


def test_sort_notes_by_created_at_desc_default(client):
    notes = _seed_notes(client, 5)
    r = client.get("/notes/")
    assert r.status_code == 200
    ids = [n["id"] for n in r.json()]
    # Default sort is -created_at → most recent first
    assert ids[0] == notes[-1]["id"]


def test_sort_invalid_field_falls_back_to_created_at(client):
    _seed_notes(client, 3)
    r = client.get("/notes/", params={"sort": "nonexistent_field"})
    assert r.status_code == 200  # should not error


# ---------------------------------------------------------------------------
# Search / filtering
# ---------------------------------------------------------------------------
def test_search_notes_by_query(client):
    client.post("/notes/", json={"title": "Alpha", "content": "unique_search_term"})
    client.post("/notes/", json={"title": "Beta", "content": "nothing here"})

    r = client.get("/notes/", params={"q": "unique_search_term"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) == 1
    assert results[0]["title"] == "Alpha"


def test_search_notes_no_match(client):
    client.post("/notes/", json={"title": "Something", "content": "Else"})
    r = client.get("/notes/", params={"q": "zzzzz_no_match"})
    assert r.status_code == 200
    assert r.json() == []


# ---------------------------------------------------------------------------
# Tags on notes (Task 3)
# ---------------------------------------------------------------------------
def test_add_tag_to_note(client):
    r = client.post("/notes/", json={"title": "Tagged", "content": "content"})
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/tags", json={"name": "backend"})
    assert r.status_code == 201
    data = r.json()
    assert len(data["tags"]) == 1
    assert data["tags"][0]["name"] == "backend"


def test_add_duplicate_tag_is_idempotent(client):
    r = client.post("/notes/", json={"title": "Dup", "content": "content"})
    note_id = r.json()["id"]

    client.post(f"/notes/{note_id}/tags", json={"name": "dup"})
    client.post(f"/notes/{note_id}/tags", json={"name": "dup"})
    r = client.get(f"/notes/{note_id}")
    assert len(r.json()["tags"]) == 1


def test_remove_tag_from_note(client):
    r = client.post("/notes/", json={"title": "Rem", "content": "content"})
    note_id = r.json()["id"]
    r = client.post(f"/notes/{note_id}/tags", json={"name": "removeme"})
    tag_id = r.json()["tags"][0]["id"]

    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.json()["tags"] == []


def test_list_all_tags(client):
    r = client.post("/notes/", json={"title": "T1", "content": "c"})
    nid = r.json()["id"]
    client.post(f"/notes/{nid}/tags", json={"name": "alpha"})
    client.post(f"/notes/{nid}/tags", json={"name": "beta"})

    r = client.get("/notes/tags/all")
    assert r.status_code == 200
    names = [t["name"] for t in r.json()]
    assert "alpha" in names
    assert "beta" in names


# ---------------------------------------------------------------------------
# Extract endpoint
# ---------------------------------------------------------------------------
def test_extract_from_note(client):
    content = "TODO: fix tests\n#backend P1 due 2025-06-01"
    r = client.post("/notes/", json={"title": "Extract", "content": content})
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200
    data = r.json()
    assert "TODO: fix tests" in data["action_items"]
    assert "backend" in data["tags"]
    assert "P1" in data["priorities"]
    assert "2025-06-01" in data["deadlines"]


def test_extract_nonexistent_note_returns_404(client):
    r = client.post("/notes/9999/extract")
    assert r.status_code == 404
