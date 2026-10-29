"""Grounded generation using calibrated similarity threshold and Mock LLM (Task 4)."""

from __future__ import annotations

from typing import Any

from agent.llm import generate
from config import ACTIVE_COLLECTION, FALLBACK_UNGROUNDED, SIM_THRESHOLD, TOP_K
from rag.retrieve import retrieve

DEMO_QUERIES: list[dict[str, str]] = [
    {
        "query": "What are the eligibility criteria and active application limits for candidates applying on Naukri.com?",
        "scope": "in-scope",
    },
    {
        "query": "How are technical interview slots scheduled and how many times can a candidate reschedule?",
        "scope": "in-scope",
    },
    {
        "query": "What is the policy for negotiating a salary offer and what is the joining bonus cap?",
        "scope": "in-scope",
    },
    {
        "query": "What documents are required for background verification and how long does clearance take?",
        "scope": "in-scope",
    },
    {
        "query": "What is the notice period for engineering roles and how does notice buyout work?",
        "scope": "in-scope",
    },
    {
        "query": "How much is the employee referral bonus and what are the payout installment milestones?",
        "scope": "in-scope",
    },
    {
        "query": "What is the current stock price of Infosys and which mutual fund gives the highest return?",
        "scope": "out-of-scope",
    },
]


def answer_policy_query(
    query: str,
    k: int = TOP_K,
    collection_name: str = ACTIVE_COLLECTION,
    threshold: float = SIM_THRESHOLD,
) -> dict[str, Any]:
    """Retrieve context chunks and generate a strictly grounded answer or fallback refusal.

    Args:
        query: User policy query.
        k: Number of chunks to retrieve.
        collection_name: Target ChromaDB collection.
        threshold: Calibrated minimum top-1 cosine similarity threshold.

    Returns:
        Dictionary containing ``query``, ``grounded``, ``top_score``, ``sources``,
        ``retrieved_chunks``, and ``answer``.
    """
    chunks = retrieve(query, k=k, collection_name=collection_name)
    top_score = float(chunks[0]["similarity"]) if chunks else 0.0

    if not chunks or top_score < threshold:
        return {
            "query": query,
            "grounded": False,
            "top_score": top_score,
            "threshold": threshold,
            "sources": [],
            "retrieved_chunks": chunks,
            "answer": FALLBACK_UNGROUNDED,
        }

    supporting = [c for c in chunks if float(c["similarity"]) >= threshold]
    sources: list[str] = []
    for c in supporting:
        if c["doc_id"] not in sources:
            sources.append(c["doc_id"])

    answer = generate(query, supporting)
    return {
        "query": query,
        "grounded": True,
        "top_score": top_score,
        "threshold": threshold,
        "sources": sources,
        "retrieved_chunks": chunks,
        "answer": answer,
    }


def main() -> None:
    """Run grounded generation demonstration on >=5 in-scope queries + 1 out-of-scope query."""
    print("=== Grounded Generation Demonstration (Task 4) ===")
    print(f"Active collection    : {ACTIVE_COLLECTION}")
    print(f"Calibrated threshold : {SIM_THRESHOLD:.4f}")
    print(f"Top-k retrieved      : {TOP_K}\n")

    for idx, item in enumerate(DEMO_QUERIES, start=1):
        res = answer_policy_query(item["query"])
        status_label = "GROUNDED ANSWER" if res["grounded"] else "FALLBACK REFUSAL (OOS)"
        print(f"--- Query {idx} ({item['scope']}) ---")
        print(f"Question   : {res['query']}")
        print(
            f"Top-1 Sim  : {res['top_score']:.4f} "
            f"({'passes' if res['grounded'] else 'below'} threshold {res['threshold']:.4f}) -> {status_label}"
        )
        print(f"Sources    : {res['sources']}")
        print(f"Answer     : {res['answer']}\n")


if __name__ == "__main__":
    main()
