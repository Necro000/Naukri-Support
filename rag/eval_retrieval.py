"""Document-level Precision@3 and Recall@3 evaluation across both collections (Task 5)."""

from __future__ import annotations

from typing import Any

from config import COLLECTION_FIXED, COLLECTION_SENTENCE, TOP_K
from rag.retrieve import retrieve

# Ground-truth relevance map for the same 6 in-scope queries from Task 4 (>= 5 required)
GROUND_TRUTH: list[dict[str, Any]] = [
    {
        "id": "Q1",
        "query": "What are the eligibility criteria and active application limits for candidates applying on Naukri.com?",
        "relevant_docs": ["eligibility"],
    },
    {
        "id": "Q2",
        "query": "How are technical interview slots scheduled and how many times can a candidate reschedule?",
        "relevant_docs": ["interview_scheduling"],
    },
    {
        "id": "Q3",
        "query": "What is the policy for negotiating a salary offer and what is the joining bonus cap?",
        "relevant_docs": ["offer_negotiation"],
    },
    {
        "id": "Q4",
        "query": "What documents are required for background verification and how long does clearance take?",
        "relevant_docs": ["background_verification"],
    },
    {
        "id": "Q5",
        "query": "What is the notice period for engineering roles and how does notice buyout work?",
        "relevant_docs": ["notice_period"],
    },
    {
        "id": "Q6",
        "query": "How much is the employee referral bonus and what are the payout installment milestones?",
        "relevant_docs": ["referral_bonus"],
    },
]


def dedupe_doc_ids(chunks: list[dict[str, Any]]) -> list[str]:
    """Map retrieved chunks back to parent doc_ids and deduplicate preserving rank order."""
    unique_docs: list[str] = []
    for chunk in chunks:
        doc_id = str(chunk["doc_id"])
        if doc_id and doc_id not in unique_docs:
            unique_docs.append(doc_id)
    return unique_docs


def evaluate_collection(
    collection_name: str,
    k: int = TOP_K,
) -> dict[str, Any]:
    """Compute document-level Precision@k and Recall@k for ``collection_name``.

    Denominator rules (explicitly stated per PRD FR-5):
    - Map top-k chunks -> parent ``doc_id`` and deduplicate first.
    - Precision@3 = |relevant ∩ unique_retrieved_docs| / |unique_retrieved_docs|
      (also reports strict k=3 denominator |relevant ∩ unique_retrieved_docs| / 3 for full transparency).
    - Recall@3 = |relevant ∩ unique_retrieved_docs| / |relevant_docs|.

    Args:
        collection_name: ChromaDB collection to evaluate.
        k: Retrieval depth (default 3).

    Returns:
        Evaluation dictionary with per-query rows and macro-averages.
    """
    rows: list[dict[str, Any]] = []
    for item in GROUND_TRUTH:
        chunks = retrieve(item["query"], k=k, collection_name=collection_name)
        raw_chunk_docs = [c["doc_id"] for c in chunks]
        unique_docs = dedupe_doc_ids(chunks)
        rel_set = set(item["relevant_docs"])
        hits = [d for d in unique_docs if d in rel_set]

        num_hits = len(hits)
        num_unique = len(unique_docs) if unique_docs else 1
        num_rel = len(rel_set) if rel_set else 1

        p_at_3_unique = num_hits / num_unique
        p_at_3_fixed_k = num_hits / k
        r_at_3 = num_hits / num_rel

        rows.append(
            {
                "id": item["id"],
                "query": item["query"],
                "relevant_docs": item["relevant_docs"],
                "top3_chunk_docs": raw_chunk_docs,
                "unique_docs": unique_docs,
                "hits": hits,
                "p_unique_str": f"{num_hits}/{num_unique} = {p_at_3_unique:.4f}",
                "p_k_str": f"{num_hits}/{k} = {p_at_3_fixed_k:.4f}",
                "r_str": f"{num_hits}/{num_rel} = {r_at_3:.4f}",
                "p_at_3": round(p_at_3_unique, 4),
                "p_at_3_k": round(p_at_3_fixed_k, 4),
                "r_at_3": round(r_at_3, 4),
            }
        )

    avg_p = round(sum(r["p_at_3"] for r in rows) / len(rows), 4)
    avg_p_k = round(sum(r["p_at_3_k"] for r in rows) / len(rows), 4)
    avg_r = round(sum(r["r_at_3"] for r in rows) / len(rows), 4)

    return {
        "collection": collection_name,
        "rows": rows,
        "avg_p_at_3": avg_p,
        "avg_p_at_3_k": avg_p_k,
        "avg_r_at_3": avg_r,
    }


def main() -> None:
    """Evaluate and compare both chunking strategies with explicit per-query arithmetic."""
    print("=== Retrieval Evaluation: Fixed-Size vs Sentence Chunking (Task 5) ===")
    print(
        "Scoring rule: Map top-3 retrieved chunks to parent doc_ids and deduplicate before scoring.\n"
        "  Precision@3 (unique-doc denominator) = |relevant ∩ unique_retrieved_docs| / |unique_retrieved_docs|\n"
        "  Recall@3                             = |relevant ∩ unique_retrieved_docs| / |relevant_docs|\n"
    )

    results = {}
    for col in (COLLECTION_FIXED, COLLECTION_SENTENCE):
        res = evaluate_collection(col, k=TOP_K)
        results[col] = res
        print(f"--- Collection: {col} ---")
        for r in res["rows"]:
            print(
                f"  {r['id']}: relevant={r['relevant_docs']} | "
                f"top3_chunks={r['top3_chunk_docs']} -> unique_docs={r['unique_docs']} | "
                f"hits={len(r['hits'])} | P@3 = {r['p_unique_str']} | R@3 = {r['r_str']}"
            )
        print(
            f"  AVERAGE ({col}): Precision@3 = {res['avg_p_at_3']:.4f} "
            f"(strict /3 denom: {res['avg_p_at_3_k']:.4f}), Recall@3 = {res['avg_r_at_3']:.4f}\n"
        )

    f_res = results[COLLECTION_FIXED]
    s_res = results[COLLECTION_SENTENCE]
    print("=== Recommendation ===")
    print(
        f"We recommend deploying '{COLLECTION_SENTENCE}' (sentence-based chunking, 2 sentences/chunk) "
        f"as our active production collection. Across the 6 evaluation queries, '{COLLECTION_SENTENCE}' "
        f"achieves an average Precision@3 of {s_res['avg_p_at_3']:.4f} and Recall@3 of {s_res['avg_r_at_3']:.4f}, "
        f"compared to '{COLLECTION_FIXED}' with Precision@3 of {f_res['avg_p_at_3']:.4f} and Recall@3 of "
        f"{f_res['avg_r_at_3']:.4f}, while requiring only 24 chunks instead of 46 and preserving complete "
        f"policy sentences without mid-word boundary splits."
    )


if __name__ == "__main__":
    main()
