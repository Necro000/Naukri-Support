"""Unit tests for Knowledge Base documents (Task 2)."""

from __future__ import annotations

from rag.chunking import load_kb_documents

REQUIRED_TOPICS: set[str] = {
    "eligibility",
    "interview_scheduling",
    "offer_negotiation",
    "background_verification",
    "notice_period",
    "referral_bonus",
    "internal_transfer",
    "probation_period",
    "remote_work",
    "diversity_hiring",
    "exit_interview",
    "data_retention",
}


def test_doc_count_and_topics_present() -> None:
    """KB must contain >=12 documents covering all 12 required topics."""
    docs = load_kb_documents()
    assert len(docs) >= 12
    doc_ids = {d["doc_id"] for d in docs}
    assert REQUIRED_TOPICS.issubset(doc_ids)


def test_sentence_count() -> None:
    """Every KB document must contain between 2 and 5 sentences."""
    docs = load_kb_documents()
    for doc in docs:
        assert 2 <= doc["sentence_count"] <= 5, (
            f"Doc {doc['doc_id']} has {doc['sentence_count']} sentences"
        )
