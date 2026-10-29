"""Job application status lookup tool and escalation score calculator (Task 6)."""

from __future__ import annotations

import re
from typing import Any

from config import (
    ESCALATION_FLAG_WEIGHT,
    ESCALATION_RECENCY_WEIGHT,
    ESCALATION_THRESHOLD,
    MAX_DAYS_SINCE_CREATED,
)
from dataset import JOB_APPLICATIONS

_RECORDS_BY_ID: dict[str, dict[str, Any]] = {
    str(rec["record_id"]).upper(): rec for rec in JOB_APPLICATIONS
}


def compute_escalation_score(
    flagged_priority_review: bool,
    days_since_created: int,
) -> float:
    """Compute a normalized escalation score in [0.0, 1.0].

    Formula:
        ``recency = days_since_created / 30.0``
        ``escalation_score = clamp(0.6 * int(flagged_priority_review) + 0.4 * recency, 0.0, 1.0)``

    Args:
        flagged_priority_review: Whether the application was flagged for priority review.
        days_since_created: Age of the application in days (0 to 30).

    Returns:
        Escalation score rounded to 4 decimal places.
    """
    recency = max(0.0, min(1.0, float(days_since_created) / float(MAX_DAYS_SINCE_CREATED)))
    raw_score = (ESCALATION_FLAG_WEIGHT * (1.0 if flagged_priority_review else 0.0)) + (
        ESCALATION_RECENCY_WEIGHT * recency
    )
    return round(max(0.0, min(1.0, raw_score)), 4)


def compute_score_distribution(records: list[dict[str, Any]] = JOB_APPLICATIONS) -> dict[str, float]:
    """Compute percentile statistics of escalation scores across the dataset.

    Args:
        records: List of job-application records.

    Returns:
        Dictionary of min, p25, p50, p75, p80, p90, max scores.
    """
    scores = sorted(
        compute_escalation_score(
            bool(r["flagged_priority_review"]),
            int(r["days_since_created"]),
        )
        for r in records
    )
    n = len(scores)

    def pct(p: float) -> float:
        idx = min(n - 1, max(0, int(round((p / 100.0) * (n - 1)))))
        return scores[idx]

    return {
        "min": scores[0],
        "p25": pct(25),
        "p50": pct(50),
        "p75": pct(75),
        "p80": pct(80),
        "p90": pct(90),
        "max": scores[-1],
    }


def check_job_application_status(record_id: str) -> dict[str, Any]:
    """Look up a Naukri.com job application's status, expected salary, and escalation score.

    Retrieves a candidate job application record by its identifier (e.g. ``APP-0007``)
    from the validated Naukri.com dataset and computes a designed escalation score
    combining priority-review status (weight 0.6) and normalized age in days (weight 0.4).
    Recommends escalation when ``escalation_score >= ESCALATION_THRESHOLD``.

    Args:
        record_id: Job application record identifier formatted as ``APP-XXXX``.

    Returns:
        Dictionary containing ``record_id``, ``category``, ``status``,
        ``expected_salary_inr``, ``days_since_created``, ``flagged_priority_review``,
        ``escalation_score``, ``escalation_threshold``, and ``escalate_recommended``,
        or an ``{"error": ..., "record_id": ...}`` dictionary if the ID is invalid or unknown.
    """
    if not record_id or not isinstance(record_id, str):
        return {
            "error": "A valid application record_id (e.g. APP-0001) is required.",
            "record_id": str(record_id or ""),
        }

    normalized_id = record_id.strip().upper()
    if not re.fullmatch(r"APP-\d{4}", normalized_id):
        return {
            "error": f"Invalid record_id format '{record_id}'. Expected format: APP-0001.",
            "record_id": normalized_id,
        }

    rec = _RECORDS_BY_ID.get(normalized_id)
    if rec is None:
        return {
            "error": f"Application record '{normalized_id}' not found in dataset.",
            "record_id": normalized_id,
        }

    score = compute_escalation_score(
        bool(rec["flagged_priority_review"]),
        int(rec["days_since_created"]),
    )
    escalate = score >= ESCALATION_THRESHOLD

    return {
        "record_id": rec["record_id"],
        "category": rec["category"],
        "status": rec["status"],
        "expected_salary_inr": rec["expected_salary_inr"],
        "days_since_created": rec["days_since_created"],
        "flagged_priority_review": rec["flagged_priority_review"],
        "escalation_score": score,
        "escalation_threshold": ESCALATION_THRESHOLD,
        "escalate_recommended": escalate,
    }


def main() -> None:
    """Print escalation score distribution and demonstrate the status lookup tool."""
    dist = compute_score_distribution(JOB_APPLICATIONS)
    all_scores = [
        compute_escalation_score(
            bool(r["flagged_priority_review"]),
            int(r["days_since_created"]),
        )
        for r in JOB_APPLICATIONS
    ]
    above_count = sum(1 for s in all_scores if s >= ESCALATION_THRESHOLD)

    print("=== Escalation Score Design & Status Tool Demo (Task 6) ===")
    print(
        f"Formula   : escalation_score = {ESCALATION_FLAG_WEIGHT} * flagged_priority_review "
        f"+ {ESCALATION_RECENCY_WEIGHT} * (days_since_created / {MAX_DAYS_SINCE_CREATED})"
    )
    print(f"Threshold : {ESCALATION_THRESHOLD:.4f} (80th percentile of dataset escalation scores)")
    print(
        f"Records >= threshold: {above_count} / {len(JOB_APPLICATIONS)} "
        f"({(above_count / len(JOB_APPLICATIONS)) * 100:.2f}%)"
    )
    print("\n--- Escalation Score Percentile Distribution ---")
    for k, v in dist.items():
        print(f"  {k:<6}: {v:.4f}")

    # Pick 3 distinct categories of records:
    # (1) flagged & old (escalate=True), (2) unflagged & aged >=27d (escalate=True), (3) unflagged & recent (escalate=False)
    flagged_old = next(
        r["record_id"]
        for r in JOB_APPLICATIONS
        if r["flagged_priority_review"] and r["days_since_created"] >= 15
    )
    unflagged_aged = next(
        r["record_id"]
        for r in JOB_APPLICATIONS
        if not r["flagged_priority_review"] and r["days_since_created"] >= 27
    )
    unflagged_recent = next(
        r["record_id"]
        for r in JOB_APPLICATIONS
        if not r["flagged_priority_review"] and r["days_since_created"] <= 10
    )

    demo_ids = [flagged_old, unflagged_aged, unflagged_recent, "APP-9999"]
    print("\n--- Tool Invocations ---")
    for rid in demo_ids:
        res = check_job_application_status(rid)
        print(f"  check_job_application_status({rid!r}) ->\n    {res}")


if __name__ == "__main__":
    main()
