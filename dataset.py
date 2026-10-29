"""Deterministic job-application dataset generator and validator (Task 1)."""

from __future__ import annotations

import random
from collections import Counter
from typing import Any

from config import (
    CATEGORIES,
    CATEGORY_WEIGHTS,
    FLAGGED_PROBABILITY,
    MAX_DAYS_SINCE_CREATED,
    NUM_RECORDS,
    SALARY_RANGES_INR,
    SEED,
    STATUSES,
    STATUS_WEIGHTS,
)

# Salary reasoning (one sentence):
# Annual expected salaries span 300,000 to 3,000,000 INR across role bands to reflect
# realistic Indian recruitment market compensation from entry-level Sales/HR associates
# up to mid-senior Product Managers and Software Engineers on Naukri.com.
SALARY_REASONING: str = (
    "Annual expected salaries span 300,000 to 3,000,000 INR across role-specific bands "
    "to reflect realistic Indian job-market compensation from entry-level Sales and HR "
    "roles up to experienced Software Engineers and Product Managers."
)


def generate_dataset(
    seed: int = SEED,
    num_records: int = NUM_RECORDS,
) -> list[dict[str, Any]]:
    """Generate a deterministic list of fabricated job-application records.

    Uses a local ``random.Random(seed)`` instance with zero global random state.

    Args:
        seed: Random seed for reproducible generation.
        num_records: Number of records to generate (must be >= 40).

    Returns:
        List of job-application record dictionaries.
    """
    rng = random.Random(seed)
    records: list[dict[str, Any]] = []

    for idx in range(1, num_records + 1):
        record_id = f"APP-{idx:04d}"
        category = rng.choices(CATEGORIES, weights=CATEGORY_WEIGHTS, k=1)[0]
        status = rng.choices(STATUSES, weights=STATUS_WEIGHTS, k=1)[0]
        low_sal, high_sal = SALARY_RANGES_INR[category]
        # Round to nearest 10,000 INR for realistic salary figures
        expected_salary_inr = rng.randrange(low_sal, high_sal + 1, 10_000)
        days_since_created = rng.randint(0, MAX_DAYS_SINCE_CREATED)
        flagged_priority_review = rng.random() < FLAGGED_PROBABILITY

        records.append(
            {
                "record_id": record_id,
                "category": category,
                "status": status,
                "expected_salary_inr": expected_salary_inr,
                "days_since_created": days_since_created,
                "flagged_priority_review": flagged_priority_review,
            }
        )

    return records


def validate_dataset(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Validate that the dataset satisfies all Part 1 Task 1 structural thresholds.

    Args:
        records: List of job-application records to validate.

    Returns:
        Summary dictionary with category counts, status counts, and flagged percentage.

    Raises:
        AssertionError: If any structural requirement is violated.
    """
    assert len(records) >= 40, f"Expected >= 40 records, got {len(records)}"

    record_ids = [r["record_id"] for r in records]
    assert len(record_ids) == len(set(record_ids)), "Record IDs must be unique"

    category_counts = Counter(r["category"] for r in records)
    for cat in CATEGORIES:
        count = category_counts.get(cat, 0)
        assert count >= 3, f"Category '{cat}' has {count} records (minimum 3 required)"

    status_counts = Counter(r["status"] for r in records)
    for st in STATUSES:
        count = status_counts.get(st, 0)
        assert count >= 1, f"Status '{st}' has {count} records (minimum 1 required)"

    for r in records:
        days = r["days_since_created"]
        assert isinstance(days, int) and 0 <= days <= 30, (
            f"Record {r['record_id']} has invalid days_since_created={days}"
        )
        sal = r["expected_salary_inr"]
        assert isinstance(sal, int) and 300_000 <= sal <= 3_000_000, (
            f"Record {r['record_id']} has out-of-range salary={sal}"
        )
        assert isinstance(r["flagged_priority_review"], bool), (
            f"Record {r['record_id']} flagged_priority_review must be bool"
        )

    flagged_count = sum(1 for r in records if r["flagged_priority_review"])
    flagged_pct = (flagged_count / len(records)) * 100.0
    assert 10.0 <= flagged_pct <= 30.0, (
        f"flagged_priority_review percentage {flagged_pct:.2f}% outside [10%, 30%]"
    )

    return {
        "total_records": len(records),
        "category_counts": {cat: category_counts[cat] for cat in CATEGORIES},
        "status_counts": {st: status_counts[st] for st in STATUSES},
        "flagged_count": flagged_count,
        "flagged_pct": round(flagged_pct, 2),
    }


JOB_APPLICATIONS: list[dict[str, Any]] = generate_dataset()
DATASET_SUMMARY: dict[str, Any] = validate_dataset(JOB_APPLICATIONS)


def print_dataset_report() -> None:
    """Print deterministic dataset design choices, counts, and validation summary."""
    summary = validate_dataset(JOB_APPLICATIONS)
    print("=== Naukri.com Job Application Dataset Report (Task 1) ===")
    print(f"Seed                       : {SEED}")
    print(f"Total records              : {summary['total_records']} (threshold: >= 40)")
    print(f"Category weights           : {dict(zip(CATEGORIES, CATEGORY_WEIGHTS))}")
    print(f"Status weights             : {dict(zip(STATUSES, STATUS_WEIGHTS))}")
    print(f"Flagged probability target : {FLAGGED_PROBABILITY}")
    print(f"Salary range (INR/yr)      : 300,000 - 3,000,000 (per-category bands)")
    print(f"Salary reasoning           : {SALARY_REASONING}")
    print("\n--- Count per Category (each must be >= 3) ---")
    for cat, cnt in summary["category_counts"].items():
        print(f"  {cat:<22}: {cnt}")
    print("\n--- Count per Status (each must be >= 1) ---")
    for st, cnt in summary["status_counts"].items():
        print(f"  {st:<22}: {cnt}")
    print(
        f"\n--- Priority Review Flagged ---\n"
        f"  Flagged count            : {summary['flagged_count']} / {summary['total_records']}\n"
        f"  Flagged percentage       : {summary['flagged_pct']:.2f}% (threshold: 10.00% - 30.00%)"
    )
    print("\n--- Sample Records (first 5) ---")
    for rec in JOB_APPLICATIONS[:5]:
        print(f"  {rec}")
    print("\n[OK] All dataset assertions passed.")


if __name__ == "__main__":
    print_dataset_report()
