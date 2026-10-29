"""Structured JSON-Lines request logger with mandatory PII phone masking (Task 12)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent.guardrails import mask_pii
from config import REQUEST_LOG_PATH


def append_request_log(
    *,
    trace_id: str,
    endpoint: str,
    method: str,
    raw_query: str,
    conversation_id: str | None,
    route: str | None,
    grounded: bool | None,
    guardrail_flags: list[str] | None,
    latency_ms: float,
    status_code: int,
    log_path: Path = REQUEST_LOG_PATH,
) -> dict[str, Any]:
    """Write a single structured JSON-Lines entry to ``logs/requests.jsonl``.

    Applies ``mask_pii()`` to ``raw_query`` before constructing the record so that
    raw phone numbers never reach disk under any code path.

    Args:
        trace_id: Unique per-request UUID string.
        endpoint: HTTP path (e.g. ``/ask``).
        method: HTTP verb (e.g. ``POST``).
        raw_query: Unmasked or partially processed query text.
        conversation_id: Conversation identifier, if applicable.
        route: Agent route taken (``rag`` or ``status``).
        grounded: Whether the response passed groundedness checks.
        guardrail_flags: List of triggered guardrail flags.
        latency_ms: Request execution duration in milliseconds.
        status_code: HTTP response status code.
        log_path: Destination JSONL log file path.

    Returns:
        The dictionary written to disk.
    """
    masked_query, _ = mask_pii(raw_query or "")
    entry: dict[str, Any] = {
        "trace_id": trace_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "endpoint": endpoint,
        "method": method,
        "conversation_id": conversation_id,
        "masked_query": masked_query,
        "route": route,
        "grounded": grounded,
        "guardrail_flags": guardrail_flags or [],
        "latency_ms": round(float(latency_ms), 2),
        "status_code": int(status_code),
    }

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    return entry
