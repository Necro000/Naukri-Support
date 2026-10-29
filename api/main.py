"""FastAPI application exposing /ask, /add-document, and /health with JSONL logging (Tasks 11 & 12)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import os
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from agent.graph import get_default_graph, run_agent
from api.logging_utils import append_request_log
from api.models import (
    AddDocRequest,
    AddDocResponse,
    AskRequest,
    AskResponse,
    HealthResponse,
)
from config import (
    CHROMA_DIR,
    COLLECTION_FIXED,
    COLLECTION_SENTENCE,
    MEMORY_PATH,
    MOCK_LLM,
    REQUEST_LOG_PATH,
)
from rag.index import add_single_document
from rag.retrieve import ensure_collection_exists


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Warm up the compiled LangGraph agent and ensure ChromaDB collections exist."""
    get_default_graph()
    ensure_collection_exists(COLLECTION_FIXED, chroma_dir=application.state.chroma_dir)
    ensure_collection_exists(COLLECTION_SENTENCE, chroma_dir=application.state.chroma_dir)
    yield


app = FastAPI(
    title="Naukri.com Employer-Support Agent API",
    description="LangGraph support agent for hiring-policy RAG and job-application status lookup.",
    version="1.0.0",
    lifespan=lifespan,
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurable paths on app.state so tests can isolate logs/memory/chroma
app.state.log_path = REQUEST_LOG_PATH
app.state.memory_path = MEMORY_PATH
app.state.chroma_dir = CHROMA_DIR


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(payload: AskRequest, request: Request) -> AskResponse:
    """Answer a hiring-policy question or check a job application's status."""
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())
    conv_id = payload.conversation_id or f"conv-{uuid.uuid4().hex[:8]}"
    log_path: Path = getattr(request.app.state, "log_path", REQUEST_LOG_PATH)
    memory_path: Path = getattr(request.app.state, "memory_path", MEMORY_PATH)

    response = run_agent(
        query=payload.query,
        conversation_id=conv_id,
        trace_id=trace_id,
        memory_path=memory_path,
        persist_memory=True,
    )
    latency_ms = (time.perf_counter() - start) * 1000.0

    append_request_log(
        trace_id=trace_id,
        endpoint="/ask",
        method="POST",
        raw_query=payload.query,
        conversation_id=conv_id,
        route=response["route"],
        grounded=response["grounded"],
        guardrail_flags=response["guardrail_flags"],
        latency_ms=latency_ms,
        status_code=200,
        log_path=log_path,
    )
    return AskResponse(**response)


@app.post("/add-document", response_model=AddDocResponse)
def add_document_endpoint(payload: AddDocRequest, request: Request) -> AddDocResponse:
    """Chunk, embed, and index a new policy document into both ChromaDB collections."""
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())
    log_path: Path = getattr(request.app.state, "log_path", REQUEST_LOG_PATH)
    chroma_dir: Path = getattr(request.app.state, "chroma_dir", CHROMA_DIR)

    col_fixed = ensure_collection_exists(COLLECTION_FIXED, chroma_dir=chroma_dir)
    existing = col_fixed.get(where={"doc_id": payload.doc_id})
    if existing and existing.get("ids"):
        latency_ms = (time.perf_counter() - start) * 1000.0
        append_request_log(
            trace_id=trace_id,
            endpoint="/add-document",
            method="POST",
            raw_query=f"add_document:{payload.doc_id}:{payload.title}",
            conversation_id=None,
            route="rag",
            grounded=True,
            guardrail_flags=[],
            latency_ms=latency_ms,
            status_code=409,
            log_path=log_path,
        )
        raise HTTPException(
            status_code=409,
            detail=f"Document '{payload.doc_id}' already exists in the knowledge base.",
        )

    counts = add_single_document(
        doc_id=payload.doc_id,
        title=payload.title,
        text=payload.text,
        chroma_dir=chroma_dir,
    )
    latency_ms = (time.perf_counter() - start) * 1000.0
    append_request_log(
        trace_id=trace_id,
        endpoint="/add-document",
        method="POST",
        raw_query=f"add_document:{payload.doc_id}:{payload.title}",
        conversation_id=None,
        route="rag",
        grounded=True,
        guardrail_flags=[],
        latency_ms=latency_ms,
        status_code=200,
        log_path=log_path,
    )
    return AddDocResponse(
        doc_id=payload.doc_id,
        chunks_added={
            COLLECTION_FIXED: counts[COLLECTION_FIXED],
            COLLECTION_SENTENCE: counts[COLLECTION_SENTENCE],
        },
    )


@app.get("/health", response_model=HealthResponse)
def health_endpoint(request: Request) -> HealthResponse:
    """Liveness and index readiness check."""
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())
    log_path: Path = getattr(request.app.state, "log_path", REQUEST_LOG_PATH)
    chroma_dir: Path = getattr(request.app.state, "chroma_dir", CHROMA_DIR)

    col_f = ensure_collection_exists(COLLECTION_FIXED, chroma_dir=chroma_dir)
    col_s = ensure_collection_exists(COLLECTION_SENTENCE, chroma_dir=chroma_dir)
    collections_info: dict[str, int] = {
        COLLECTION_FIXED: col_f.count(),
        COLLECTION_SENTENCE: col_s.count(),
    }

    latency_ms = (time.perf_counter() - start) * 1000.0
    append_request_log(
        trace_id=trace_id,
        endpoint="/health",
        method="GET",
        raw_query="health_check",
        conversation_id=None,
        route=None,
        grounded=True,
        guardrail_flags=[],
        latency_ms=latency_ms,
        status_code=200,
        log_path=log_path,
    )
    return HealthResponse(
        status="ok",
        mock_llm=MOCK_LLM,
        collections=collections_info,
    )
