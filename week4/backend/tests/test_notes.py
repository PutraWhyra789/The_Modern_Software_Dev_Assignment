# Tests for /notes endpoints


# ── helpers ──────────────────────────────────────────────────────────────────


def _create(client, title="My Note", content="Hello world!"):
    r = client.post("/notes/", json={"title": title, "content": content})
    assert r.status_code == 201, r.text
    return r.json()


# ── CREATE / LIST ─────────────────────────────────────────────────────────────


def test_create_note_returns_created(client):
    data = _create(client)
    assert data["title"] == "My Note"
    assert data["content"] == "Hello world!"
    assert "id" in data


def test_list_notes_includes_created(client):
    _create(client, title="Note A")
    _create(client, title="Note B")

    r = client.get("/notes/")
    assert r.status_code == 200
    titles = [n["title"] for n in r.json()]
    assert "Note A" in titles
    assert "Note B" in titles


def test_get_single_note(client):
    created = _create(client, title="Single")
    r = client.get(f"/notes/{created['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Single"


def test_get_note_not_found(client):
    r = client.get("/notes/99999")
    assert r.status_code == 404


# ── VALIDATION ────────────────────────────────────────────────────────────────


def test_create_note_empty_title_rejected(client):
    r = client.post("/notes/", json={"title": "", "content": "Some content"})
    assert r.status_code == 422


def test_create_note_empty_content_rejected(client):
    r = client.post("/notes/", json={"title": "Title", "content": ""})
    assert r.status_code == 422


def test_create_note_missing_fields_rejected(client):
    r = client.post("/notes/", json={"title": "Only title"})
    assert r.status_code == 422


# ── SEARCH ────────────────────────────────────────────────────────────────────


def test_search_no_query_returns_all(client):
    _create(client, title="Alpha")
    _create(client, title="Beta")

    r = client.get("/notes/search/")
    assert r.status_code == 200
    assert len(r.json()) >= 2


def test_search_by_title(client):
    _create(client, title="Unique Title XYZ", content="irrelevant")
    _create(client, title="Other", content="different")

    r = client.get("/notes/search/", params={"q": "XYZ"})
    assert r.status_code == 200
    results = r.json()
    assert len(results) >= 1
    assert all("XYZ" in n["title"] or "XYZ" in n["content"] for n in results)


def test_search_by_content(client):
    _create(client, title="Plain", content="contains the needle here")
    _create(client, title="Other", content="completely different")

    r = client.get("/notes/search/", params={"q": "needle"})
    assert r.status_code == 200
    results = r.json()
    assert any("needle" in n["content"] for n in results)


def test_search_case_insensitive(client):
    _create(client, title="Case Test", content="Hello World")

    r = client.get("/notes/search/", params={"q": "hello"})
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_search_no_match_returns_empty(client):
    _create(client, title="Some Note", content="Some content")

    r = client.get("/notes/search/", params={"q": "ZZZNOMATCH"})
    assert r.status_code == 200
    assert r.json() == []


# ── UPDATE (PUT) ──────────────────────────────────────────────────────────────


def test_update_note_title(client):
    note = _create(client, title="Old Title", content="Keep this")
    r = client.put(f"/notes/{note['id']}", json={"title": "New Title"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "New Title"
    assert data["content"] == "Keep this"


def test_update_note_content(client):
    note = _create(client, title="Keep Title", content="Old content")
    r = client.put(f"/notes/{note['id']}", json={"content": "Fresh content"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Keep Title"
    assert data["content"] == "Fresh content"


def test_update_note_both_fields(client):
    note = _create(client)
    r = client.put(f"/notes/{note['id']}", json={"title": "T2", "content": "C2"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "T2"
    assert data["content"] == "C2"


def test_update_note_empty_body_is_noop(client):
    note = _create(client, title="Stable", content="Unchanged")
    r = client.put(f"/notes/{note['id']}", json={})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Stable"
    assert data["content"] == "Unchanged"


def test_update_note_not_found(client):
    r = client.put("/notes/99999", json={"title": "Ghost"})
    assert r.status_code == 404


def test_update_note_empty_title_rejected(client):
    note = _create(client)
    r = client.put(f"/notes/{note['id']}", json={"title": ""})
    assert r.status_code == 422


def test_update_note_empty_content_rejected(client):
    note = _create(client)
    r = client.put(f"/notes/{note['id']}", json={"content": ""})
    assert r.status_code == 422


# ── DELETE ────────────────────────────────────────────────────────────────────


def test_delete_note_returns_204(client):
    note = _create(client)
    r = client.delete(f"/notes/{note['id']}")
    assert r.status_code == 204


def test_deleted_note_no_longer_found(client):
    note = _create(client)
    client.delete(f"/notes/{note['id']}")
    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 404


def test_deleted_note_not_in_list(client):
    note = _create(client, title="Gone Soon")
    _create(client, title="Stays")

    client.delete(f"/notes/{note['id']}")

    r = client.get("/notes/")
    ids = [n["id"] for n in r.json()]
    assert note["id"] not in ids


def test_delete_note_not_found(client):
    r = client.delete("/notes/99999")
    assert r.status_code == 404


# ── EXTRACT ───────────────────────────────────────────────────────────────────


def test_extract_action_items_from_note(client):
    note = _create(
        client,
        title="Meeting notes",
        content="General discussion.\n- TODO: follow up with team\n- Ship the release!",
    )
    r = client.post(f"/notes/{note['id']}/extract")
    assert r.status_code == 201
    data = r.json()
    assert "action_items" in data
    assert "tags" in data
    assert any("follow up" in item for item in data["action_items"])
    assert any("release" in item for item in data["action_items"])


def test_extract_tags_from_note(client):
    note = _create(
        client,
        title="Tagged note",
        content="Working on #backend and #testing today. Also #backend again.",
    )
    r = client.post(f"/notes/{note['id']}/extract")
    assert r.status_code == 201
    data = r.json()
    assert "backend" in data["tags"]
    assert "testing" in data["tags"]
    assert data["tags"].count("backend") == 1


def test_extract_empty_note_returns_empty_lists(client):
    note = _create(client, title="Blank", content="Just ordinary prose here.")
    r = client.post(f"/notes/{note['id']}/extract")
    assert r.status_code == 201
    data = r.json()
    assert data["action_items"] == []
    assert data["tags"] == []


def test_extract_save_items_creates_action_items(client):
    note = _create(
        client,
        title="Tasks",
        content="- TODO: write tests\n- Deploy it!",
    )
    before_count = len(client.get("/action-items/").json())

    r = client.post(f"/notes/{note['id']}/extract", params={"save_items": "true"})
    assert r.status_code == 201
    extracted = r.json()["action_items"]

    after_count = len(client.get("/action-items/").json())
    assert after_count == before_count + len(extracted)


def test_extract_without_save_does_not_create_action_items(client):
    note = _create(
        client,
        title="Dry run",
        content="- TODO: should not be saved\n- Not saved either!",
    )
    before_count = len(client.get("/action-items/").json())

    client.post(f"/notes/{note['id']}/extract")

    after_count = len(client.get("/action-items/").json())
    assert after_count == before_count


def test_extract_note_not_found(client):
    r = client.post("/notes/99999/extract")
    assert r.status_code == 404
