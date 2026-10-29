"""Persistent JSON conversation memory keyed by conversation_id (Task 8)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import MEMORY_PATH

RECORD_ID_REGEX: re.Pattern[str] = re.compile(r"\bAPP-\d{4}\b", re.I)


def load_all_memory(memory_path: Path = MEMORY_PATH) -> dict[str, list[dict[str, Any]]]:
    """Load the full conversation store from ``memory_path``.

    Args:
        memory_path: Path to the JSON memory file.

    Returns:
        Dictionary mapping ``conversation_id`` to a list of turn dicts.
    """
    if not memory_path.exists():
        return {}
    try:
        raw = memory_path.read_text(encoding="utf-8").strip()
        if not raw:
            return {}
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def load_conversation_history(
    conversation_id: str,
    memory_path: Path = MEMORY_PATH,
) -> list[dict[str, Any]]:
    """Return prior turns for ``conversation_id`` from ``memory_path``.

    Args:
        conversation_id: Unique conversation identifier.
        memory_path: Path to the JSON memory file.

    Returns:
        List of turn dicts ``{"role", "content", "record_id", "route", "ts"}``.
    """
    store = load_all_memory(memory_path)
    turns = store.get(conversation_id, [])
    return list(turns) if isinstance(turns, list) else []


def save_turn(
    conversation_id: str,
    user_query: str,
    assistant_answer: str,
    route: str,
    record_id: str | None = None,
    memory_path: Path = MEMORY_PATH,
) -> list[dict[str, Any]]:
    """Append a user + assistant turn pair for ``conversation_id`` and persist to disk.

    Args:
        conversation_id: Conversation identifier.
        user_query: Masked user query text.
        assistant_answer: Final assistant response text.
        route: Route taken (``"rag"`` or ``"status"``).
        record_id: Resolved application ``record_id``, if any.
        memory_path: Path to the JSON memory file.

    Returns:
        Updated list of turns for ``conversation_id``.
    """
    store = load_all_memory(memory_path)
    history = list(store.get(conversation_id, []))
    now_iso = datetime.now(timezone.utc).isoformat()

    history.append(
        {
            "role": "user",
            "content": user_query,
            "record_id": record_id,
            "route": route,
            "ts": now_iso,
        }
    )
    history.append(
        {
            "role": "assistant",
            "content": assistant_answer,
            "record_id": record_id,
            "route": route,
            "ts": now_iso,
        }
    )
    store[conversation_id] = history
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(json.dumps(store, indent=2, ensure_ascii=False), encoding="utf-8")
    return history


def get_last_record_id(history: list[dict[str, Any]]) -> str | None:
    """Find the most recent ``APP-XXXX`` record_id mentioned in ``history``.

    Args:
        history: List of prior conversation turn dicts.

    Returns:
        Uppercase ``APP-XXXX`` string if present in history, else ``None``.
    """
    for turn in reversed(history):
        rec_id = turn.get("record_id")
        if isinstance(rec_id, str) and RECORD_ID_REGEX.fullmatch(rec_id.strip()):
            return rec_id.strip().upper()
        content = str(turn.get("content", ""))
        match = RECORD_ID_REGEX.search(content)
        if match:
            return match.group(0).upper()
    return None
