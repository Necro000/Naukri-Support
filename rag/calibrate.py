"""Empirical similarity threshold calibration for grounded generation (Task 4)."""

from __future__ import annotations

from typing import Any

from config import ACTIVE_COLLECTION, COLLECTION_FIXED, COLLECTION_SENTENCE
from rag.retrieve import retrieve

CALIBRATION_QUERIES: list[dict[str, str]] = [
    {
        "query": "How many active job applications can an external candidate submit in 90 days?",
        "scope": "in-scope",
        "expected_doc": "eligibility",
    },
    {
        "query": "What is the standard notice period for software engineers and can leave offset it?",
        "scope": "in-scope",
        "expected_doc": "notice_period",
    },
    {
        "query": "How much is the employee referral bonus for technical roles and when is it paid?",
        "scope": "in-scope",
        "expected_doc": "referral_bonus",
    },
    {
        "query": "How long are applicant resumes retained before automatic anonymization or deletion?",
        "scope": "in-scope",
        "expected_doc": "data_retention",
    },
    {
        "query": "What is the weather forecast for Mumbai tomorrow and will it rain during the cricket match?",
        "scope": "out-of-scope",
        "expected_doc": "none",
    },
    {
        "query": "How do I bake a sourdough bread loaf using whole wheat flour at high altitude?",
        "scope": "out-of-scope",
        "expected_doc": "none",
    },
    {
        "query": "Which cryptocurrency hardware wallet supports Solana staking rewards with zero gas fees?",
        "scope": "out-of-scope",
        "expected_doc": "none",
    },
]


def run_calibration(collection_name: str = ACTIVE_COLLECTION) -> dict[str, Any]:
    """Measure top-1 cosine similarities for in-scope and out-of-scope queries.

    Computes the observed gap between the lowest in-scope top-1 similarity and the
    highest out-of-scope top-1 similarity, selecting the midpoint as the empirical
    groundedness threshold.

    Args:
        collection_name: ChromaDB collection to calibrate against.

    Returns:
        Dictionary of per-query measurements and computed threshold statistics.
    """
    rows: list[dict[str, Any]] = []
    in_scores: list[float] = []
    oos_scores: list[float] = []

    for item in CALIBRATION_QUERIES:
        hits = retrieve(item["query"], k=1, collection_name=collection_name)
        top_hit = hits[0] if hits else {"doc_id": "none", "similarity": 0.0}
        sim = float(top_hit["similarity"])
        row = {
            "query": item["query"],
            "scope": item["scope"],
            "expected_doc": item["expected_doc"],
            "matched_doc": top_hit["doc_id"],
            "top1_similarity": sim,
        }
        rows.append(row)
        if item["scope"] == "in-scope":
            in_scores.append(sim)
        else:
            oos_scores.append(sim)

    min_in = min(in_scores)
    max_oos = max(oos_scores)
    gap = round(min_in - max_oos, 4)
    midpoint = round((min_in + max_oos) / 2.0, 4)

    return {
        "collection": collection_name,
        "rows": rows,
        "min_in_scope": min_in,
        "max_out_of_scope": max_oos,
        "gap": gap,
        "midpoint_threshold": midpoint,
    }


def main() -> None:
    """Print empirical calibration measurements across both collections."""
    print("=== Empirical Groundedness Threshold Calibration (Task 4) ===")
    for col in (COLLECTION_SENTENCE, COLLECTION_FIXED):
        res = run_calibration(col)
        print(f"\nCollection: {col}")
        print(f"{'#':<3} {'Scope':<13} {'Top-1 Sim':<11} {'Matched Doc':<24} Query")
        print("-" * 105)
        for idx, r in enumerate(res["rows"], start=1):
            print(
                f"{idx:<3} {r['scope']:<13} {r['top1_similarity']:<11.4f} "
                f"{r['matched_doc']:<24} {r['query']}"
            )
        print("-" * 105)
        print(f"Lowest in-scope top-1 similarity     : {res['min_in_scope']:.4f}")
        print(f"Highest out-of-scope top-1 similarity: {res['max_out_of_scope']:.4f}")
        print(f"Observed cluster separation gap      : {res['gap']:.4f}")
        print(f"Empirical midpoint threshold         : {res['midpoint_threshold']:.4f}")


if __name__ == "__main__":
    main()
