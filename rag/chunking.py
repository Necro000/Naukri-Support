"""Document loading and dual chunking strategies (Task 3)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from config import FIXED_CHUNK_OVERLAP, FIXED_CHUNK_SIZE, KB_DIR, SENTENCES_PER_CHUNK


def strip_markdown_header(raw_text: str) -> tuple[str, str]:
    """Extract optional Markdown title and clean body text from a document.

    Args:
        raw_text: Raw Markdown file contents.

    Returns:
        Tuple of ``(title, body_text)``.
    """
    lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]
    if not lines:
        return ("Untitled", "")
    if lines[0].startswith("#"):
        title = lines[0].lstrip("#").strip()
        body = " ".join(lines[1:]).strip()
        return (title, body)
    return ("Untitled", " ".join(lines).strip())


def split_sentences(text: str) -> list[str]:
    """Split text into sentences using deterministic punctuation boundaries.

    Args:
        text: Clean paragraph text.

    Returns:
        List of non-empty sentence strings.
    """
    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized:
        return []
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return [p.strip() for p in parts if p.strip()]


def load_kb_documents(kb_dir: Path = KB_DIR) -> list[dict[str, Any]]:
    """Load and validate all Markdown knowledge-base documents from ``kb_dir``.

    Args:
        kb_dir: Path to knowledge-base folder.

    Returns:
        List of dicts with ``doc_id``, ``title``, ``text``, and ``sentence_count``.
    """
    docs: list[dict[str, Any]] = []
    for path in sorted(kb_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        title, body = strip_markdown_header(raw)
        sentences = split_sentences(body)
        assert 2 <= len(sentences) <= 5, (
            f"KB doc '{path.name}' must have 2-5 sentences, found {len(sentences)}"
        )
        docs.append(
            {
                "doc_id": path.stem,
                "title": title,
                "text": body,
                "sentence_count": len(sentences),
            }
        )
    assert len(docs) >= 12, f"Expected >= 12 KB documents, found {len(docs)}"
    return docs


def fixed_chunks(
    doc_id: str,
    text: str,
    size: int = FIXED_CHUNK_SIZE,
    overlap: int = FIXED_CHUNK_OVERLAP,
) -> list[dict[str, str]]:
    """Chunk a document using fixed character length with sliding window overlap.

    Args:
        doc_id: Parent document identifier (filename stem).
        text: Clean document body text.
        size: Maximum character length per chunk.
        overlap: Character overlap between consecutive chunks.

    Returns:
        List of chunk dicts containing ``doc_id``, ``chunk_id``, ``text``, and ``strategy``.
    """
    assert size > overlap >= 0, "Chunk size must be greater than overlap >= 0"
    normalized = re.sub(r"\s+", " ", text.strip())
    if not normalized:
        return []

    chunks: list[dict[str, str]] = []
    step = size - overlap
    start = 0
    idx = 0
    while start < len(normalized):
        end = min(start + size, len(normalized))
        piece = normalized[start:end].strip()
        if piece:
            chunks.append(
                {
                    "doc_id": doc_id,
                    "chunk_id": f"{doc_id}__fixed_{idx:02d}",
                    "text": piece,
                    "strategy": "fixed",
                }
            )
            idx += 1
        if end >= len(normalized):
            break
        start += step

    return chunks


def sentence_chunks(
    doc_id: str,
    text: str,
    per_chunk: int = SENTENCES_PER_CHUNK,
) -> list[dict[str, str]]:
    """Chunk a document by grouping consecutive sentences.

    Args:
        doc_id: Parent document identifier (filename stem).
        text: Clean document body text.
        per_chunk: Number of sentences per chunk.

    Returns:
        List of chunk dicts containing ``doc_id``, ``chunk_id``, ``text``, and ``strategy``.
    """
    assert per_chunk >= 1, "per_chunk must be >= 1"
    sentences = split_sentences(text)
    chunks: list[dict[str, str]] = []
    for idx, i in enumerate(range(0, len(sentences), per_chunk)):
        group = " ".join(sentences[i : i + per_chunk]).strip()
        if group:
            chunks.append(
                {
                    "doc_id": doc_id,
                    "chunk_id": f"{doc_id}__sentence_{idx:02d}",
                    "text": group,
                    "strategy": "sentence",
                }
            )
    return chunks
