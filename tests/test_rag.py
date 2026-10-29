"""Unit tests for KB loading, chunking, indexing, retrieval, and grounded fallback (Tasks 2-5)."""

from __future__ import annotations

from config import COLLECTION_FIXED, COLLECTION_SENTENCE, FALLBACK_UNGROUNDED
from rag.chunking import fixed_chunks, load_kb_documents, sentence_chunks
from rag.eval_retrieval import evaluate_collection
from rag.generate import answer_policy_query
from rag.retrieve import retrieve


def test_kb_documents_count_and_sentences() -> None:
    """KB must contain >=12 documents with 2-5 sentences each."""
    docs = load_kb_documents()
    assert len(docs) >= 12
    for doc in docs:
        assert 2 <= doc["sentence_count"] <= 5


def test_chunking_strategies() -> None:
    """Both fixed and sentence chunkers must produce valid metadata and non-empty text."""
    sample = "Sentence one is short. Sentence two has more policy details. Sentence three concludes."
    f_chunks = fixed_chunks("sample_doc", sample, size=40, overlap=10)
    s_chunks = sentence_chunks("sample_doc", sample, per_chunk=2)
    assert len(f_chunks) >= 2
    assert len(s_chunks) == 2
    assert f_chunks[0]["strategy"] == "fixed"
    assert s_chunks[0]["strategy"] == "sentence"


def test_retrieval_and_grounded_fallback() -> None:
    """In-scope query must be grounded; out-of-scope query must trigger fallback refusal."""
    in_res = answer_policy_query(
        "What is the notice period for engineering roles and how does notice buyout work?"
    )
    assert in_res["grounded"] is True
    assert "notice_period" in in_res["sources"]

    oos_res = answer_policy_query(
        "What is the weather forecast for Mumbai tomorrow and will it rain during the cricket match?"
    )
    assert oos_res["grounded"] is False
    assert oos_res["answer"] == FALLBACK_UNGROUNDED


def test_both_collections_retrieve() -> None:
    """Both kb_fixed and kb_sentence collections must return top-3 results and valid P@3/R@3."""
    for col in (COLLECTION_FIXED, COLLECTION_SENTENCE):
        hits = retrieve("employee referral bonus payout", k=3, collection_name=col)
        assert len(hits) == 3
        assert hits[0]["doc_id"] == "referral_bonus"
        eval_res = evaluate_collection(col, k=3)
        assert eval_res["avg_r_at_3"] >= 0.8
