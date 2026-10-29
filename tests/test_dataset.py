"""Unit tests for deterministic job-application dataset generation (Task 1)."""

from __future__ import annotations

from config import CATEGORIES, STATUSES
from dataset import JOB_APPLICATIONS, generate_dataset, validate_dataset


def test_dataset_determinism() -> None:
    """Two calls with the same seed must produce identical records."""
    run_a = generate_dataset()
    run_b = generate_dataset()
    assert run_a == run_b
    assert run_a == JOB_APPLICATIONS


def test_dataset_thresholds() -> None:
    """Dataset must satisfy all count, range, and percentage assertions."""
    summary = validate_dataset(JOB_APPLICATIONS)
    assert summary["total_records"] >= 40
    for cat in CATEGORIES:
        assert summary["category_counts"][cat] >= 3
    for st in STATUSES:
        assert summary["status_counts"][st] >= 1
    assert 10.0 <= summary["flagged_pct"] <= 30.0
