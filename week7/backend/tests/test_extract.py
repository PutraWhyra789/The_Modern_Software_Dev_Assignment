from backend.app.services.extract import (
    extract_action_items,
    extract_all,
    extract_deadlines,
    extract_priorities,
    extract_tags,
)


# ---------------------------------------------------------------------------
# extract_action_items
# ---------------------------------------------------------------------------
def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items


def test_extract_fixme_and_hack():
    text = "FIXME: broken layout\nHACK: temp workaround"
    items = extract_action_items(text)
    assert "FIXME: broken layout" in items
    assert "HACK: temp workaround" in items


def test_extract_checkbox_items():
    text = "[ ] unchecked task\n[x] done task"
    items = extract_action_items(text)
    assert "[ ] unchecked task" in items
    assert "[x] done task" in items


def test_extract_action_items_empty():
    assert extract_action_items("") == []


def test_extract_action_items_no_match():
    assert extract_action_items("Just a regular sentence.") == []


# ---------------------------------------------------------------------------
# extract_tags
# ---------------------------------------------------------------------------
def test_extract_tags_basic():
    text = "Fix #backend issue and improve #frontend"
    tags = extract_tags(text)
    assert "backend" in tags
    assert "frontend" in tags


def test_extract_tags_deduplication():
    text = "#backend #backend #backend"
    tags = extract_tags(text)
    assert tags == ["backend"]


def test_extract_tags_empty():
    assert extract_tags("no tags here") == []


def test_extract_tags_with_hyphens():
    text = "Related to #my-feature and #bug-fix"
    tags = extract_tags(text)
    assert "my-feature" in tags
    assert "bug-fix" in tags


# ---------------------------------------------------------------------------
# extract_priorities
# ---------------------------------------------------------------------------
def test_extract_priorities_pn():
    text = "This is P0 critical and also P2"
    prios = extract_priorities(text)
    assert "P0" in prios
    assert "P2" in prios


def test_extract_priorities_natural_language():
    text = "This is high priority and also urgent"
    prios = extract_priorities(text)
    assert "high priority" in prios
    assert "urgent" in prios


def test_extract_priorities_empty():
    assert extract_priorities("nothing special") == []


# ---------------------------------------------------------------------------
# extract_deadlines
# ---------------------------------------------------------------------------
def test_extract_deadlines_iso():
    text = "due 2025-06-01"
    deadlines = extract_deadlines(text)
    assert "2025-06-01" in deadlines


def test_extract_deadlines_us_style():
    text = "deadline: 03/15/2025"
    deadlines = extract_deadlines(text)
    assert "03/15/2025" in deadlines


def test_extract_deadlines_written_month():
    text = "due March 15, 2025"
    deadlines = extract_deadlines(text)
    assert "March 15, 2025" in deadlines


def test_extract_deadlines_relative():
    text = "due tomorrow"
    deadlines = extract_deadlines(text)
    assert "tomorrow" in deadlines


def test_extract_deadlines_due_by():
    text = "due by 2025-12-31"
    deadlines = extract_deadlines(text)
    assert "2025-12-31" in deadlines


def test_extract_deadlines_empty():
    assert extract_deadlines("no dates") == []


# ---------------------------------------------------------------------------
# extract_all (combined)
# ---------------------------------------------------------------------------
def test_extract_all():
    text = "TODO: deploy #backend P1 due 2025-06-01"
    result = extract_all(text)
    assert "action_items" in result
    assert "tags" in result
    assert "priorities" in result
    assert "deadlines" in result
    assert "TODO: deploy #backend P1 due 2025-06-01" in result["action_items"]
    assert "backend" in result["tags"]
    assert "P1" in result["priorities"]
    assert "2025-06-01" in result["deadlines"]


def test_extract_all_empty():
    result = extract_all("")
    assert result == {"action_items": [], "tags": [], "priorities": [], "deadlines": []}
