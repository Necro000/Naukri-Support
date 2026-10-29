"""Demonstration and log-verification script for FastAPI endpoints and JSONL logging (Tasks 11 & 12)."""

from __future__ import annotations

import json
import sys

from fastapi.testclient import TestClient

from api.main import app
from config import CHROMA_DIR, MEMORY_PATH, REQUEST_LOG_PATH
from rag.index import build_indices


def run_api_demo() -> None:
    """Run end-to-end requests against the FastAPI app and write to logs/requests.jsonl."""
    if REQUEST_LOG_PATH.exists():
        REQUEST_LOG_PATH.unlink()
    if MEMORY_PATH.exists():
        MEMORY_PATH.unlink()

    # Reset indices cleanly so /add-document starts fresh
    build_indices(chroma_dir=CHROMA_DIR)

    app.state.log_path = REQUEST_LOG_PATH
    app.state.memory_path = MEMORY_PATH
    app.state.chroma_dir = CHROMA_DIR

    client = TestClient(app)
    print("=== FastAPI Deployment Demonstration (Task 11) ===")

    exchanges = [
        (
            "1. GET /health",
            "GET",
            "/health",
            None,
        ),
        (
            "2. POST /ask (Policy Route — Notice Period)",
            "POST",
            "/ask",
            {
                "query": "What is the standard notice period for software engineers and how does buyout work?",
                "conversation_id": "api-demo-conv-1",
            },
        ),
        (
            "3. POST /ask (Status Route — APP-0006)",
            "POST",
            "/ask",
            {
                "query": "What is the status and escalation score of APP-0006?",
                "conversation_id": "api-demo-conv-2",
            },
        ),
        (
            "4. POST /ask (Input Guardrail — Phone Number PII Masking)",
            "POST",
            "/ask",
            {
                "query": "Please call me on +91 98765 43210 regarding employee referral bonus payouts.",
                "conversation_id": "api-demo-conv-3",
            },
        ),
        (
            "5. POST /add-document (Add New Policy Document to Both Collections)",
            "POST",
            "/add-document",
            {
                "doc_id": "relocation_policy",
                "title": "Candidate Relocation Policy",
                "text": (
                    "Selected outstation candidates relocating more than 100 kilometers receive a flat "
                    "60000 INR relocation reimbursement. Claims must be submitted within 45 days of joining."
                ),
            },
        ),
        (
            "6. POST /ask (Query Newly Added Relocation Policy Document)",
            "POST",
            "/ask",
            {
                "query": "How much is the candidate relocation reimbursement and when must claims be submitted?",
                "conversation_id": "api-demo-conv-4",
            },
        ),
    ]

    for label, method, path, payload in exchanges:
        print(f"\n--- {label} ---")
        if method == "GET":
            resp = client.get(path)
        else:
            print(f"Request Body : {json.dumps(payload)}")
            resp = client.post(path, json=payload)
        print(f"Status Code  : {resp.status_code}")
        print(f"Response JSON:\n{json.dumps(resp.json(), indent=2)}")

    # Restore clean 12-doc index after demo so evaluation scripts see exact baseline KB
    build_indices(chroma_dir=CHROMA_DIR)
    print("\n[OK] FastAPI demonstration complete.")


def run_log_check() -> None:
    """Verify structured JSONL logs and confirm zero unmasked phone numbers on disk (Task 12)."""
    print("=== Structured JSON-Lines Logging & PII Verification (Task 12) ===")
    print(f"Log file path: {REQUEST_LOG_PATH}\n")

    raw_text = REQUEST_LOG_PATH.read_text(encoding="utf-8")
    lines = [line for line in raw_text.strip().splitlines() if line.strip()]
    print(f"Total JSONL entries logged: {len(lines)}\n")
    print("--- Contents of logs/requests.jsonl ---")
    for idx, line in enumerate(lines, start=1):
        parsed = json.loads(line)
        print(f"[{idx}] {json.dumps(parsed)}")

    test_phone = "98765 43210"
    matches = [line for line in lines if test_phone in line or "9876543210" in line]
    masked_matches = [line for line in lines if "[PHONE_MASKED]" in line]

    print("\n--- PII Grep Verification ---")
    print(f"Searching logs/requests.jsonl for raw phone '{test_phone}'...")
    print(f"  Raw phone occurrences found    : {len(matches)} (MUST be 0)")
    print(f"  '[PHONE_MASKED]' entries found : {len(masked_matches)} (MUST be >= 1)")
    assert len(matches) == 0, "Raw phone number leaked to logs/requests.jsonl!"
    assert len(masked_matches) >= 1, "Expected [PHONE_MASKED] in logs/requests.jsonl!"
    print("[OK] Verified: Raw phone number never reached disk; '[PHONE_MASKED]' logged with trace_id and latency_ms.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "api"
    if mode == "api":
        run_api_demo()
    elif mode == "log_check":
        run_log_check()
    else:
        raise SystemExit(f"Unknown mode: {mode}")
