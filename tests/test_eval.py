"""Unit tests for the 15-query RAG triad evaluation (Task 13)."""

from __future__ import annotations

import json

from config import EVAL_QUERIES_PATH
from eval.triad import run_triad_evaluation
from tests.test_kb import REQUIRED_TOPICS


def test_15_queries_coverage() -> None:
    """Test set must have 15 queries covering all 12 topics plus >=2 OOS/edge queries."""
    queries = json.loads(EVAL_QUERIES_PATH.read_text(encoding="utf-8"))
    assert len(queries) == 15
    topics = {q["topic"] for q in queries}
    assert REQUIRED_TOPICS.issubset(topics)
    non_in_scope = [q for q in queries if q["scope"] != "in-scope"]
    assert len(non_in_scope) >= 2


def test_scores_bounds_and_averages() -> None:
    """All three RAG-triad scores and their averages must be in [0.0, 1.0]."""
    res = run_triad_evaluation()
    assert len(res["rows"]) == 15
    for row in res["rows"]:
        assert 0.0 <= row["context_relevance"] <= 1.0
        assert 0.0 <= row["groundedness"] <= 1.0
        assert 0.0 <= row["answer_relevance"] <= 1.0
    assert 0.0 <= res["avg_context_relevance"] <= 1.0
    assert 0.0 <= res["avg_groundedness"] <= 1.0
    assert 0.0 <= res["avg_answer_relevance"] <= 1.0
