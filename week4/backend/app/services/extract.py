import re


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_tags(text: str) -> list[str]:
    """Return a deduplicated, sorted list of #hashtags found in *text*."""
    raw = re.findall(r"#([A-Za-z0-9_]+)", text)
    seen: set[str] = set()
    result: list[str] = []
    for tag in raw:
        lower = tag.lower()
        if lower not in seen:
            seen.add(lower)
            result.append(lower)
    return sorted(result)


def extract_all(text: str) -> dict[str, list[str]]:
    """Convenience wrapper returning both action items and tags."""
    return {
        "action_items": extract_action_items(text),
        "tags": extract_tags(text),
    }
