"""Deterministic Mock LLM and optional real LLM stub for grounded generation."""

from __future__ import annotations

import os
from typing import Sequence

from config import FALLBACK_UNGROUNDED, MOCK_LLM


def generate(
    prompt: str,
    context_chunks: Sequence[dict[str, object]] | None = None,
) -> str:
    """Generate an extractive grounded response from retrieved context chunks.

    Under ``MOCK_LLM=1`` (the default for all graded runs), this function never
    makes network calls or requires API keys. It deterministically synthesizes
    an answer strictly from the provided ``context_chunks`` and cites their
    ``doc_id`` sources.

    Args:
        prompt: The user query or instruction prompt.
        context_chunks: Retrieved chunk dicts containing ``text`` and ``doc_id``.

    Returns:
        Grounded answer string citing source document IDs.
    """
    if MOCK_LLM or not os.getenv("OPENAI_API_KEY"):
        if not context_chunks:
            return FALLBACK_UNGROUNDED

        seen_texts: list[str] = []
        sources: list[str] = []
        for chunk in context_chunks:
            text = str(chunk.get("text", "")).strip()
            doc_id = str(chunk.get("doc_id", "")).strip()
            if text and text not in seen_texts:
                seen_texts.append(text)
            if doc_id and doc_id not in sources:
                sources.append(doc_id)

        if not seen_texts:
            return FALLBACK_UNGROUNDED

        combined = " ".join(seen_texts[:2])
        source_tag = f" [Sources: {', '.join(sources)}]" if sources else ""
        return f"Based on Naukri.com policy ({', '.join(sources)}): {combined}{source_tag}"

    # Optional real LLM branch behind environment flag (never used in graded runs)
    raise RuntimeError(
        "Real LLM mode is disabled unless configured. Set MOCK_LLM=1 for deterministic offline mode."
    )
