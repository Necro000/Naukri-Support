"""RAG Triad evaluation at scale across 15 queries using LLM-as-judge under MOCK_LLM (Task 13)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import numpy as np

from agent.graph import run_agent
from config import ACTIVE_COLLECTION, EVAL_QUERIES_PATH, FALLBACK_UNGROUNDED, TOP_K
from rag.index import embed_texts
from rag.retrieve import retrieve

JUDGE_PROMPT_TEMPLATE: str = """You are an impartial evaluation judge scoring a RAG support agent response on three RAG-triad criteria in [0.0, 1.0]:
1. Context Relevance: Does the retrieved context directly address the user's question?
2. Groundedness (Faithfulness): Is every claim in the answer supported by the retrieved context (or appropriately refused when context is insufficient)?
3. Answer Relevance: Does the final answer directly and completely address the user's question?

Query: {query}
Retrieved Context: {context}
Agent Answer: {answer}
"""

_STOPWORDS: set[str] = {
    "a", "an", "and", "are", "as", "at", "based", "be", "by", "for", "from", "in",
    "is", "it", "naukri", "com", "of", "on", "or", "policy", "sources", "that",
    "the", "to", "with",
}


def _cosine(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute bounded cosine similarity in [0.0, 1.0] between two unit vectors."""
    dot = float(np.dot(np.asarray(vec_a), np.asarray(vec_b)))
    return round(max(0.0, min(1.0, dot)), 4)


def _content_tokens(text: str) -> set[str]:
    """Extract lowercase alphanumeric content tokens excluding boilerplate stopwords."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in tokens if len(t) > 2 and t not in _STOPWORDS}


def mock_llm_judge(
    query: str,
    retrieved_chunks: list[dict[str, Any]],
    response: dict[str, Any],
) -> dict[str, float]:
    """Deterministic MOCK_LLM implementation of the RAG-triad LLM-as-judge prompt.

    Computes:
    - ``context_relevance``: Top-1 cosine similarity between the query and retrieved chunks.
    - ``groundedness``: Fraction of content tokens in the generated answer (excluding citation tags)
      that appear verbatim in the retrieved context chunks; ``0.0`` if ungrounded or blocked.
    - ``answer_relevance``: Cosine similarity between the query embedding and answer embedding
      when the agent provides a grounded answer; ``0.0`` when refused/blocked.

    Args:
        query: User test query.
        retrieved_chunks: Chunks retrieved from the active collection.
        response: Agent response dictionary.

    Returns:
        Dict with ``context_relevance``, ``groundedness``, and ``answer_relevance`` in ``[0, 1]``.
    """
    _ = JUDGE_PROMPT_TEMPLATE.format(
        query=query,
        context="\n".join(str(c.get("text", "")) for c in retrieved_chunks),
        answer=response.get("answer", ""),
    )

    if "injection_blocked" in response.get("guardrail_flags", []):
        return {
            "context_relevance": 0.0,
            "groundedness": 0.0,
            "answer_relevance": 0.0,
        }

    context_rel = float(retrieved_chunks[0]["similarity"]) if retrieved_chunks else 0.0
    context_rel = round(max(0.0, min(1.0, context_rel)), 4)

    if not response.get("grounded", False) or response.get("answer") == FALLBACK_UNGROUNDED:
        return {
            "context_relevance": context_rel,
            "groundedness": 0.0,
            "answer_relevance": 0.0,
        }

    answer_text = str(response.get("answer", ""))
    # Strip wrapper prefix/suffix added by extractive generator before checking token overlap
    clean_answer = re.sub(r"^Based on Naukri\.com policy \([^)]*\):\s*", "", answer_text)
    clean_answer = re.sub(r"\s*\[Sources:[^\]]*\]\s*$", "", clean_answer)

    context_combined = " ".join(str(c.get("text", "")) for c in retrieved_chunks)
    ans_tokens = _content_tokens(clean_answer)
    ctx_tokens = _content_tokens(context_combined)

    if not ans_tokens:
        groundedness = 0.0
    else:
        groundedness = round(len(ans_tokens & ctx_tokens) / len(ans_tokens), 4)

    vecs = embed_texts([query, clean_answer])
    answer_rel = _cosine(vecs[0], vecs[1])

    return {
        "context_relevance": context_rel,
        "groundedness": groundedness,
        "answer_relevance": answer_rel,
    }


def run_triad_evaluation(queries_path: Path = EVAL_QUERIES_PATH) -> dict[str, Any]:
    """Run the 15-query RAG triad evaluation suite under MOCK_LLM.

    Args:
        queries_path: Path to ``eval/test_queries.json``.

    Returns:
        Dictionary with per-query rows and the three triad averages across all 15 queries.
    """
    queries: list[dict[str, str]] = json.loads(queries_path.read_text(encoding="utf-8"))
    assert len(queries) == 15, f"Expected 15 test queries, found {len(queries)}"

    rows: list[dict[str, Any]] = []
    for item in queries:
        q_text = item["query"]
        chunks = retrieve(q_text, k=TOP_K, collection_name=ACTIVE_COLLECTION)
        resp = run_agent(
            q_text,
            conversation_id=f"triad-{item['id']}",
            persist_memory=False,
        )
        scores = mock_llm_judge(q_text, chunks, resp)
        rows.append(
            {
                "id": item["id"],
                "topic": item["topic"],
                "scope": item["scope"],
                "query": q_text,
                "grounded": resp["grounded"],
                "flags": resp["guardrail_flags"],
                "context_relevance": scores["context_relevance"],
                "groundedness": scores["groundedness"],
                "answer_relevance": scores["answer_relevance"],
            }
        )

    avg_ctx = round(sum(r["context_relevance"] for r in rows) / len(rows), 4)
    avg_grd = round(sum(r["groundedness"] for r in rows) / len(rows), 4)
    avg_ans = round(sum(r["answer_relevance"] for r in rows) / len(rows), 4)

    in_rows = [r for r in rows if r["scope"] == "in-scope"]
    avg_ctx_in = round(sum(r["context_relevance"] for r in in_rows) / len(in_rows), 4)
    avg_grd_in = round(sum(r["groundedness"] for r in in_rows) / len(in_rows), 4)
    avg_ans_in = round(sum(r["answer_relevance"] for r in in_rows) / len(in_rows), 4)

    return {
        "rows": rows,
        "avg_context_relevance": avg_ctx,
        "avg_groundedness": avg_grd,
        "avg_answer_relevance": avg_ans,
        "in_scope_avg_context_relevance": avg_ctx_in,
        "in_scope_avg_groundedness": avg_grd_in,
        "in_scope_avg_answer_relevance": avg_ans_in,
    }


def main() -> None:
    """Print Markdown report of the 15-query RAG triad evaluation."""
    res = run_triad_evaluation()
    print("# RAG Triad Evaluation Report (Task 13 — 15 Queries under MOCK_LLM=1)\n")
    print(f"- **Active collection:** `{ACTIVE_COLLECTION}`")
    print("- **Total queries evaluated:** 15 (12 covering all required KB topics + 2 out-of-scope + 1 prompt-injection edge case)\n")
    print("| # | ID | Topic | Scope | Context Relevance | Groundedness | Answer Relevance | Grounded | Flags |")
    print("|---|---|---|---|---|---|---|---|---|")
    for idx, r in enumerate(res["rows"], start=1):
        flags_str = ", ".join(r["flags"]) if r["flags"] else "none"
        print(
            f"| {idx} | {r['id']} | `{r['topic']}` | {r['scope']} | "
            f"{r['context_relevance']:.4f} | {r['groundedness']:.4f} | {r['answer_relevance']:.4f} | "
            f"{r['grounded']} | {flags_str} |"
        )
    print(
        f"| **Avg (all 15)** | – | **All 15 queries** | – | "
        f"**{res['avg_context_relevance']:.4f}** | **{res['avg_groundedness']:.4f}** | "
        f"**{res['avg_answer_relevance']:.4f}** | – | – |"
    )
    print(
        f"| **Avg (12 in-scope)** | – | **12 KB topics** | in-scope | "
        f"**{res['in_scope_avg_context_relevance']:.4f}** | **{res['in_scope_avg_groundedness']:.4f}** | "
        f"**{res['in_scope_avg_answer_relevance']:.4f}** | – | – |"
    )


if __name__ == "__main__":
    main()
