"""TypedDict state definition for the Naukri.com LangGraph support agent (Task 7)."""

from __future__ import annotations

from typing import Any, Literal, TypedDict


class AgentState(TypedDict, total=False):
    """State dictionary passed between nodes in the LangGraph support workflow."""

    conversation_id: str
    trace_id: str
    query: str
    masked_query: str
    guardrail_flags: list[str]
    blocked: bool
    history: list[dict[str, Any]]
    intent: Literal["policy", "status"]
    record_id: str | None
    retrieved_chunks: list[dict[str, Any]]
    top_score: float
    tool_result: dict[str, Any] | None
    answer: str
    grounded: bool
    confidence: float
    response: dict[str, Any]
