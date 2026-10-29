"""Vector retrieval from ChromaDB collections with cosine similarity (Task 4)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import (
    ACTIVE_COLLECTION,
    CHROMA_DIR,
    TOP_K,
)
from rag.index import build_indices, embed_texts, get_chroma_client


def ensure_collection_exists(
    collection_name: str = ACTIVE_COLLECTION,
    chroma_dir: Path = CHROMA_DIR,
) -> Any:
    """Return the requested ChromaDB collection, building indices if not yet created."""
    client = get_chroma_client(chroma_dir)
    existing = [c.name for c in client.list_collections()]
    if collection_name not in existing:
        build_indices(chroma_dir=chroma_dir)
    return client.get_collection(name=collection_name)


def retrieve(
    query: str,
    k: int = TOP_K,
    collection_name: str = ACTIVE_COLLECTION,
    chroma_dir: Path = CHROMA_DIR,
) -> list[dict[str, Any]]:
    """Retrieve top-k chunks for ``query`` and compute cosine similarity = 1 - distance.

    Args:
        query: User query text.
        k: Number of top chunks to retrieve.
        collection_name: ChromaDB collection name (``kb_fixed`` or ``kb_sentence``).
        chroma_dir: Persistent ChromaDB directory.

    Returns:
        List of chunk dicts sorted by descending cosine similarity.
    """
    if not query or not query.strip():
        return []

    collection = ensure_collection_exists(collection_name=collection_name, chroma_dir=chroma_dir)
    query_vec = embed_texts([query.strip()])[0]

    results = collection.query(
        query_embeddings=[query_vec],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    docs = (results.get("documents") or [[]])[0]
    metas = (results.get("metadatas") or [[]])[0]
    dists = (results.get("distances") or [[]])[0]

    chunks: list[dict[str, Any]] = []
    for text, meta, dist in zip(docs, metas, dists):
        similarity = round(max(0.0, min(1.0, 1.0 - float(dist))), 4)
        chunks.append(
            {
                "doc_id": str(meta.get("doc_id", "")),
                "chunk_id": str(meta.get("chunk_id", "")),
                "strategy": str(meta.get("strategy", "")),
                "text": str(text),
                "distance": round(float(dist), 4),
                "similarity": similarity,
            }
        )
    return chunks
