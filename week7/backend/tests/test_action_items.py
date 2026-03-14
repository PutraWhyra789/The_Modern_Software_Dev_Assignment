# ---------------------------------------------------------------------------
# Basic CRUD (existing coverage, expanded)
# ---------------------------------------------------------------------------
def test_create_complete_list_and_patch_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False
    assert "created_at" in item and "updated_at" in item

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/", params={"completed": True, "limit": 5, "sort": "-created_at"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.patch(f"/action-items/{item['id']}", json={"description": "Updated"})
    assert r.status_code == 200
    patched = r.json()
    assert patched["description"] == "Updated"


# ---------------------------------------------------------------------------
# GET single item
# ---------------------------------------------------------------------------
def test_get_single_action_item(client):
    r = client.post("/action-items/", json={"description": "Read me"})
    item = r.json()

    r = client.get(f"/action-items/{item['id']}")
    assert r.status_code == 200
    assert r.json()["description"] == "Read me"


def test_get_nonexistent_action_item_returns_404(client):
    r = client.get("/action-items/9999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------
def test_delete_action_item(client):
    r = client.post("/action-items/", json={"description": "delete me"})
    item_id = r.json()["id"]

    r = client.delete(f"/action-items/{item_id}")
    assert r.status_code == 204

    r = client.get(f"/action-items/{item_id}")
    assert r.status_code == 404


def test_delete_nonexistent_action_item_returns_404(client):
    r = client.delete("/action-items/9999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def test_create_action_item_empty_description_rejected(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422


def test_create_action_item_missing_description_rejected(client):
    r = client.post("/action-items/", json={})
    assert r.status_code == 422


def test_patch_action_item_empty_description_rejected(client):
    r = client.post("/action-items/", json={"description": "Good"})
    item_id = r.json()["id"]
    r = client.patch(f"/action-items/{item_id}", json={"description": ""})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Pagination
# ---------------------------------------------------------------------------
def _seed_items(client, count: int = 10) -> list[dict]:
    items = []
    for i in range(count):
        r = client.post("/action-items/", json={"description": f"Item {i}"})
        assert r.status_code == 201
        items.append(r.json())
    return items


def test_pagination_skip_and_limit(client):
    _seed_items(client, 10)

    r = client.get("/action-items/", params={"limit": 3, "skip": 0})
    assert r.status_code == 200
    page1 = r.json()
    assert len(page1) == 3

    r = client.get("/action-items/", params={"limit": 3, "skip": 3})
    assert r.status_code == 200
    page2 = r.json()
    assert len(page2) == 3

    ids1 = {i["id"] for i in page1}
    ids2 = {i["id"] for i in page2}
    assert ids1.isdisjoint(ids2)


def test_pagination_limit_upper_bound(client):
    r = client.get("/action-items/", params={"limit": 201})
    assert r.status_code == 422


def test_pagination_skip_negative_rejected(client):
    r = client.get("/action-items/", params={"skip": -1})
    assert r.status_code == 422


def test_pagination_limit_zero_rejected(client):
    r = client.get("/action-items/", params={"limit": 0})
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------
def test_sort_items_by_description_asc(client):
    client.post("/action-items/", json={"description": "Banana"})
    client.post("/action-items/", json={"description": "Apple"})
    client.post("/action-items/", json={"description": "Cherry"})

    r = client.get("/action-items/", params={"sort": "description"})
    assert r.status_code == 200
    descs = [i["description"] for i in r.json()]
    assert descs == sorted(descs)


def test_sort_items_by_description_desc(client):
    client.post("/action-items/", json={"description": "Banana"})
    client.post("/action-items/", json={"description": "Apple"})
    client.post("/action-items/", json={"description": "Cherry"})

    r = client.get("/action-items/", params={"sort": "-description"})
    assert r.status_code == 200
    descs = [i["description"] for i in r.json()]
    assert descs == sorted(descs, reverse=True)


def test_sort_items_by_created_at_desc_default(client):
    items = _seed_items(client, 5)
    r = client.get("/action-items/")
    assert r.status_code == 200
    ids = [i["id"] for i in r.json()]
    assert ids[0] == items[-1]["id"]


def test_sort_invalid_field_falls_back(client):
    _seed_items(client, 3)
    r = client.get("/action-items/", params={"sort": "nonexistent"})
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Filtering by completion status
# ---------------------------------------------------------------------------
def test_filter_completed_items(client):
    r1 = client.post("/action-items/", json={"description": "Done"})
    client.put(f"/action-items/{r1.json()['id']}/complete")
    client.post("/action-items/", json={"description": "Open"})

    r = client.get("/action-items/", params={"completed": True})
    assert r.status_code == 200
    assert all(i["completed"] for i in r.json())

    r = client.get("/action-items/", params={"completed": False})
    assert r.status_code == 200
    assert all(not i["completed"] for i in r.json())


def test_complete_nonexistent_item_returns_404(client):
    r = client.put("/action-items/9999/complete")
    assert r.status_code == 404


def test_patch_nonexistent_item_returns_404(client):
    r = client.patch("/action-items/9999", json={"description": "nope"})
    assert r.status_code == 404
