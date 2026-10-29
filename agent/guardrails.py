"""Input and output guardrails: PII phone masking, prompt-injection detection, and groundedness (Task 10)."""

from __future__ import annotations

import re

from config import SIM_THRESHOLD

# Matches Indian phone numbers with optional +91 / 0 prefix and optional space/hyphen separators
# Examples matched: "+91 98765 43210", "+91-9876543210", "9876543210", "098765 43210"
PHONE_REGEX: re.Pattern[str] = re.compile(
    r"(?<!\w)(?:\+91[\s\-]?|91[\s\-]|0)?[6-9]\d{4}[\s\-]?\d{5}(?!\w)"
)

INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("ignore_previous_instructions", re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions", re.I)),
    ("disregard_instructions", re.compile(r"disregard\s+(?:all\s+)?(?:previous|prior|system)\s+(?:instructions|prompts)", re.I)),
    ("reveal_system_prompt", re.compile(r"(?:reveal|print|show|output|dump)\s+(?:your\s+)?(?:system\s+prompt|hidden\s+instructions|developer\s+prompt)", re.I)),
    ("override_safety", re.compile(r"(?:bypass|disable|override)\s+(?:all\s+)?(?:guardrails|safety|filters|restrictions)", re.I)),
    ("roleplay_jailbreak", re.compile(r"(?:you\s+are\s+now\s+in\s+developer\s+mode|act\s+as\s+dan|do\s+anything\s+now)", re.I)),
)


def mask_pii(text: str) -> tuple[str, bool]:
    """Mask fixed-format Indian phone numbers in ``text`` with ``[PHONE_MASKED]``.

    This exact function is used on both the agent input query and the structured
    request logger so raw phone numbers never reach the model or disk.

    Args:
        text: Raw user query string.

    Returns:
        Tuple of ``(masked_text, was_masked)``.
    """
    if not text:
        return ("", False)
    masked, count = PHONE_REGEX.subn("[PHONE_MASKED]", text)
    return (masked, count > 0)


def detect_injection(text: str) -> tuple[bool, str | None]:
    """Detect prompt-injection or instruction-override patterns in ``text``.

    Args:
        text: User query string (raw or masked).

    Returns:
        Tuple of ``(is_injection, matched_rule_name)``.
    """
    if not text:
        return (False, None)
    for rule_name, pattern in INJECTION_PATTERNS:
        if pattern.search(text):
            return (True, rule_name)
    return (False, None)


def check_grounded(top_score: float, threshold: float = SIM_THRESHOLD) -> bool:
    """Verify whether top-1 retrieval cosine similarity meets the calibrated threshold.

    Args:
        top_score: Highest cosine similarity among retrieved chunks.
        threshold: Empirical similarity threshold from ``config.py``.

    Returns:
        ``True`` if ``top_score >= threshold``, else ``False``.
    """
    return float(top_score) >= float(threshold)
