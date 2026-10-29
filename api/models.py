"""Pydantic request and response models for the FastAPI deployment (Task 11)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request payload for POST /ask."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="User policy or job-application status question.",
    )
    conversation_id: str | None = Field(
        default=None,
        description="Optional conversation ID for multi-turn memory persistence.",
    )


class AskResponse(BaseModel):
    """Response payload for POST /ask conforming to agent/response_schema.json."""

    answer: str
    route: Literal["rag", "status"]
    sources: list[str]
    grounded: bool
    guardrail_flags: list[str]
    trace_id: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    tool_result: dict[str, Any] | None = None
    conversation_id: str


class AddDocRequest(BaseModel):
    """Request payload for POST /add-document."""

    doc_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        pattern=r"^[a-z0-9_]+$",
        description="Unique snake_case document identifier.",
    )
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Human-readable document title.",
    )
    text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Document policy text (2-5 sentences recommended).",
    )


class AddDocResponse(BaseModel):
    """Response payload for POST /add-document."""

    doc_id: str
    chunks_added: dict[str, int]


class HealthResponse(BaseModel):
    """Response payload for GET /health."""

    status: str
    mock_llm: bool
    collections: dict[str, int]
