import re


def extract_action_items(text: str) -> list[str]:
    """Extract action items from text.

    Recognises lines starting with TODO:, ACTION:, FIXME:, HACK:,
    lines containing checkbox patterns (``[ ]`` or ``[x]``),
    and lines ending with ``!``.
    """
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    results: list[str] = []
    for line in lines:
        normalized = line.lower()
        if any(normalized.startswith(prefix) for prefix in ("todo:", "action:", "fixme:", "hack:")):
            results.append(line)
        elif re.search(r"\[\s?\]", line) or re.search(r"\[x\]", line, re.IGNORECASE):
            results.append(line)
        elif line.endswith("!"):
            results.append(line)
    return results


def extract_tags(text: str) -> list[str]:
    """Extract hashtag-style tags (e.g. ``#backend``) from text."""
    return sorted(set(re.findall(r"#([A-Za-z][A-Za-z0-9_-]*)", text)))


def extract_priorities(text: str) -> list[str]:
    """Extract priority markers such as ``P0``, ``P1``, ``high priority``, etc."""
    results: list[str] = []

    # Explicit Pn markers (P0 – P4)
    for match in re.finditer(r"\bP([0-4])\b", text):
        results.append(f"P{match.group(1)}")

    # Natural-language priorities
    priority_phrases = re.findall(
        r"\b(high priority|medium priority|low priority|urgent|critical|blocker)\b",
        text,
        re.IGNORECASE,
    )
    results.extend(p.lower() for p in priority_phrases)
    return results


def extract_deadlines(text: str) -> list[str]:
    """Extract deadline-like date references from text.

    Supports patterns such as:
    - ``due 2025-03-15``
    - ``deadline: March 15, 2025``
    - ``by 03/15/2025``
    - ``due by tomorrow``
    """
    results: list[str] = []

    # ISO-style: due YYYY-MM-DD or deadline: YYYY-MM-DD
    for match in re.finditer(
        r"(?:due(?:\s+by)?|deadline[:\s]+|by)\s*(\d{4}-\d{2}-\d{2})",
        text,
        re.IGNORECASE,
    ):
        results.append(match.group(1))

    # US-style: MM/DD/YYYY
    for match in re.finditer(
        r"(?:due(?:\s+by)?|deadline[:\s]+|by)\s*(\d{1,2}/\d{1,2}/\d{4})",
        text,
        re.IGNORECASE,
    ):
        results.append(match.group(1))

    # Written month: Month DD, YYYY
    for match in re.finditer(
        r"(?:due(?:\s+by)?|deadline[:\s]+|by)\s*"
        r"((?:January|February|March|April|May|June|July|August|September|October|November|December)"
        r"\s+\d{1,2},?\s+\d{4})",
        text,
        re.IGNORECASE,
    ):
        results.append(match.group(1))

    # Relative dates: "due tomorrow", "due next Monday"
    for match in re.finditer(
        r"(?:due(?:\s+by)?)\s+(today|tomorrow|next\s+\w+)",
        text,
        re.IGNORECASE,
    ):
        results.append(match.group(1).strip())

    return results


def extract_all(text: str) -> dict[str, list[str]]:
    """Run all extraction routines and return a combined result dict."""
    return {
        "action_items": extract_action_items(text),
        "tags": extract_tags(text),
        "priorities": extract_priorities(text),
        "deadlines": extract_deadlines(text),
    }
