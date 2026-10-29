"""Unit and integration tests for FastAPI endpoints, JSONL logging, and RAG triad evaluation (Tasks 11-13)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from agent.graph import validate_response
from api.main import app
from config import CHROMA_DIR, MEMORY_PATH, REQUEST_LOG_PATH
from eval.triad import run_triad_evaluation


def test_api_endpoints_and_masked_logging(tmp_path: Path) -> None:
    """Test /health, /ask (policy, status, PII), /add-document, and verify JSONL log masking."""
    log_file = tmp_path / "requests.jsonl"
    mem_file = tmp_path / "memory.json"
    app.state.log_path = log_file
    app.state.memory_path = mem_file
    app.state.chroma_dir = CHROMA_DIR

    try:
        client = TestClient(app)

        # 1. Health endpoint
        r_health = client.get("/health")
        assert r_health.status_code == 200
        assert r_health.json()["status"] == "ok"

        # 2. Policy query on /ask
        r_policy = client.post(
            "/ask",
            json={"query": "What is the notice period for software engineers?", "conversation_id": "api-c1"},
        )
        assert r_policy.status_code == 200
        body_policy = r_policy.json()
        validate_response(body_policy)
        assert body_policy["route"] == "rag"
        assert body_policy["grounded"] is True

        # 3. Status query on /ask
        r_status = client.post(
            "/ask",
            json={"query": "Check status of APP-0002", "conversation_id": "api-c2"},
        )
        assert r_status.status_code == 200
        body_status = r_status.json()
        validate_response(body_status)
        assert body_status["route"] == "status"
        assert body_status["tool_result"]["record_id"] == "APP-0002"

        # 4. PII phone query on /ask — raw phone must NEVER appear in logs/requests.jsonl
        raw_phone = "98765 43210"
        r_pii = client.post(
            "/ask",
            json={"query": f"Please call me on +91 {raw_phone} about referral bonus policy"},
        )
        assert r_pii.status_code == 200
        body_pii = r_pii.json()
        assert "pii_masked" in body_pii["guardrail_flags"]

        # 5. Invalid payload -> 422
        r_bad = client.post("/ask", json={"query": ""})
        assert r_bad.status_code == 422

        # 6. Verify JSONL log entries and absence of raw phone number
        assert log_file.exists()
        log_text = log_file.read_text(encoding="utf-8")
        assert raw_phone not in log_text
        assert "[PHONE_MASKED]" in log_text
        lines = [json.loads(line) for line in log_text.strip().splitlines()]
        assert len(lines) >= 4
        for entry in lines:
            assert "trace_id" in entry
            assert "latency_ms" in entry
            assert "masked_query" in entry
    finally:
        app.state.log_path = REQUEST_LOG_PATH
        app.state.memory_path = MEMORY_PATH
        app.state.chroma_dir = CHROMA_DIR


def test_add_document_and_duplicate_check(tmp_path: Path) -> None:
    """POST /add-document must index into both collections and reject duplicate doc_ids with 409."""
    log_file = tmp_path / "requests.jsonl"
    chroma_tmp = tmp_path / "chroma_test"
    app.state.log_path = log_file
    app.state.chroma_dir = chroma_tmp

    try:
        client = TestClient(app)
        payload = {
            "doc_id": "relocation_allowance",
            "title": "Relocation Allowance Policy",
            "text": (
                "Outstation candidates relocating more than 150 kilometers receive a flat 50000 INR "
                "relocation allowance. Reimbursements are processed with the first month payroll."
            ),
        }
        r1 = client.post("/add-document", json=payload)
        assert r1.status_code == 200
        data = r1.json()
        assert data["doc_id"] == "relocation_allowance"
        assert data["chunks_added"]["kb_fixed"] >= 1
        assert data["chunks_added"]["kb_sentence"] >= 1

        # Duplicate doc_id must return 409
        r2 = client.post("/add-document", json=payload)
        assert r2.status_code == 409
    finally:
        app.state.log_path = REQUEST_LOG_PATH
        app.state.chroma_dir = CHROMA_DIR


def test_rag_triad_evaluation_15_queries() -> None:
    """Triad evaluation must score 15 queries with all scores in [0, 1]."""
    res = run_triad_evaluation()
    assert len(res["rows"]) == 15
    for row in res["rows"]:
        assert 0.0 <= row["context_relevance"] <= 1.0
        assert 0.0 <= row["groundedness"] <= 1.0
        assert 0.0 <= row["answer_relevance"] <= 1.0
    assert 0.0 <= res["avg_context_relevance"] <= 1.0
    assert 0.0 <= res["avg_groundedness"] <= 1.0
    assert 0.0 <= res["avg_answer_relevance"] <= 1.0
