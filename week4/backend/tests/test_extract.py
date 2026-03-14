from backend.app.services.extract import extract_action_items, extract_all, extract_tags


# ── extract_action_items ─────────────────────────────────────────────────────


def test_extract_action_items_todo_prefix():
    text = "- TODO: write tests"
    items = extract_action_items(text)
    assert "TODO: write tests" in items


def test_extract_action_items_exclamation_suffix():
    text = "- Ship it!"
    items = extract_action_items(text)
    assert "Ship it!" in items


def test_extract_action_items_combined():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_action_items_ignores_plain_lines():
    text = "Just a regular sentence.\nAnother ordinary line."
    items = extract_action_items(text)
    assert items == []


def test_extract_action_items_empty_string():
    assert extract_action_items("") == []


def test_extract_action_items_todo_case_insensitive():
    text = "todo: lowercase todo prefix"
    items = extract_action_items(text)
    assert len(items) == 1


def test_extract_action_items_todo_mixed_case():
    text = "Todo: mixed case prefix"
    items = extract_action_items(text)
    assert len(items) == 1


def test_extract_action_items_strips_leading_dash_and_spaces():
    text = "  -   TODO: with leading dash and spaces"
    items = extract_action_items(text)
    assert any("TODO:" in item for item in items)


def test_extract_action_items_multiple_todos():
    text = "TODO: task one\nTODO: task two\nTODO: task three"
    items = extract_action_items(text)
    assert len(items) == 3


def test_extract_action_items_multiple_exclamations():
    text = "Do this!\nDo that!\nDo nothing"
    items = extract_action_items(text)
    assert len(items) == 2


def test_extract_action_items_only_whitespace_lines_skipped():
    text = "   \n\t\n   \nTODO: real item"
    items = extract_action_items(text)
    assert len(items) == 1


# ── extract_tags ─────────────────────────────────────────────────────────────


def test_extract_tags_single_tag():
    tags = extract_tags("Working on #backend today.")
    assert tags == ["backend"]


def test_extract_tags_multiple_tags():
    tags = extract_tags("Topics: #python #fastapi #testing")
    assert "python" in tags
    assert "fastapi" in tags
    assert "testing" in tags


def test_extract_tags_deduplication():
    tags = extract_tags("#backend and #backend again #BACKEND")
    assert tags.count("backend") == 1


def test_extract_tags_case_normalised_to_lowercase():
    tags = extract_tags("#Python #PYTHON #python")
    assert tags == ["python"]


def test_extract_tags_returns_sorted_list():
    tags = extract_tags("#zebra #apple #mango")
    assert tags == sorted(tags)


def test_extract_tags_empty_string():
    assert extract_tags("") == []


def test_extract_tags_no_hashtags():
    assert extract_tags("No tags here at all.") == []


def test_extract_tags_alphanumeric_and_underscores():
    tags = extract_tags("#tag_1 #tag2 #TAG_THREE")
    assert "tag_1" in tags
    assert "tag2" in tags
    assert "tag_three" in tags


def test_extract_tags_hashtag_at_start_of_string():
    tags = extract_tags("#first word")
    assert "first" in tags


def test_extract_tags_numeric_tag():
    tags = extract_tags("Issue #123 should be tracked.")
    assert "123" in tags


def test_extract_tags_only_hash_symbol_ignored():
    tags = extract_tags("The price is # dollars.")
    assert tags == []


# ── extract_all ──────────────────────────────────────────────────────────────


def test_extract_all_returns_dict_with_expected_keys():
    result = extract_all("some text")
    assert "action_items" in result
    assert "tags" in result


def test_extract_all_combined():
    text = "- TODO: deploy the service!\n- Ship it!\nTagged as #devops and #urgent."
    result = extract_all(text)
    assert any("deploy" in item for item in result["action_items"])
    assert any("Ship" in item for item in result["action_items"])
    assert "devops" in result["tags"]
    assert "urgent" in result["tags"]


def test_extract_all_empty_input():
    result = extract_all("")
    assert result["action_items"] == []
    assert result["tags"] == []


def test_extract_all_only_tags_no_action_items():
    text = "Just a note about #python and #fastapi."
    result = extract_all(text)
    assert result["action_items"] == []
    assert "python" in result["tags"]


def test_extract_all_only_action_items_no_tags():
    text = "TODO: write docs\nDeploy to prod!"
    result = extract_all(text)
    assert len(result["action_items"]) >= 1
    assert result["tags"] == []


def test_extract_all_action_items_type_is_list():
    result = extract_all("some text")
    assert isinstance(result["action_items"], list)


def test_extract_all_tags_type_is_list():
    result = extract_all("some text")
    assert isinstance(result["tags"], list)


def test_extract_all_tags_are_sorted_and_deduplicated():
    text = "#zebra #apple #zebra #Mango"
    result = extract_all(text)
    assert result["tags"] == sorted(set(result["tags"]))
    assert result["tags"].count("zebra") == 1
