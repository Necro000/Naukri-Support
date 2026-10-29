"""Embedding and ChromaDB indexing for fixed and sentence chunking strategies (Task 3)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DIR,
    COLLECTION_FIXED,
    COLLECTION_SENTENCE,
    EMBEDDING_MODEL_NAME,
    FIXED_CHUNK_OVERLAP,
    FIXED_CHUNK_SIZE,
    KB_DIR,
    SENTENCES_PER_CHUNK,
)
from rag.chunking import fixed_chunks, load_kb_documents, sentence_chunks

_EMBEDDER: SentenceTransformer | None = None
_CHROMA_CLIENTS: dict[str, Any] = {}


def get_embedder() -> SentenceTransformer:
    """Return a cached singleton SentenceTransformer model instance (offline-first)."""
    global _EMBEDDER
    if _EMBEDDER is None:
        try:
            _EMBEDDER = SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)
        except Exception:
            _EMBEDDER = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _EMBEDDER


def get_chroma_client(chroma_dir: Path = CHROMA_DIR) -> Any:
    """Return a cached ChromaDB PersistentClient for the given directory."""
    key = str(chroma_dir.resolve())
    if key not in _CHROMA_CLIENTS:
        chroma_dir.mkdir(parents=True, exist_ok=True)
        _CHROMA_CLIENTS[key] = chromadb.PersistentClient(path=key)
    return _CHROMA_CLIENTS[key]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Compute normalized embeddings for a list of strings using SentenceTransformers.

    Args:
        texts: Texts to embed.

    Returns:
        List of float embedding vectors.
    """
    embedder = get_embedder()
    vectors = embedder.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [vec.tolist() for vec in vectors]


def build_indices(
    kb_dir: Path = KB_DIR,
    chroma_dir: Path = CHROMA_DIR,
) -> dict[str, int]:
    """Chunk all KB documents with both strategies, embed, and index in ChromaDB.

    Idempotently deletes and recreates ``kb_fixed`` and ``kb_sentence`` collections
    configured with cosine distance space.

    Args:
        kb_dir: Knowledge base directory containing ``*.md`` files.
        chroma_dir: Persistent ChromaDB storage directory.

    Returns:
        Dictionary with document count and chunk counts per collection.
    """
    docs = load_kb_documents(kb_dir)
    client = get_chroma_client(chroma_dir)

    all_fixed: list[dict[str, str]] = []
    all_sentence: list[dict[str, str]] = []

    for doc in docs:
        all_fixed.extend(
            fixed_chunks(
                doc["doc_id"],
                doc["text"],
                size=FIXED_CHUNK_SIZE,
                overlap=FIXED_CHUNK_OVERLAP,
            )
        )
        all_sentence.extend(
            sentence_chunks(
                doc["doc_id"],
                doc["text"],
                per_chunk=SENTENCES_PER_CHUNK,
            )
        )

    for col_name, chunk_list in (
        (COLLECTION_FIXED, all_fixed),
        (COLLECTION_SENTENCE, all_sentence),
    ):
        collection = client.get_or_create_collection(
            name=col_name,
            metadata={"hnsw:space": "cosine"},
        )
        existing_data = collection.get()
        existing_ids = existing_data.get("ids") if existing_data else []
        if existing_ids:
            collection.delete(ids=existing_ids)
        texts = [c["text"] for c in chunk_list]
        embeddings = embed_texts(texts)
        ids = [c["chunk_id"] for c in chunk_list]
        metadatas = [
            {
                "doc_id": c["doc_id"],
                "chunk_id": c["chunk_id"],
                "strategy": c["strategy"],
            }
            for c in chunk_list
        ]
        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    return {
        "doc_count": len(docs),
        COLLECTION_FIXED: len(all_fixed),
        COLLECTION_SENTENCE: len(all_sentence),
    }


def add_single_document(
    doc_id: str,
    title: str,
    text: str,
    chroma_dir: Path = CHROMA_DIR,
) -> dict[str, int]:
    """Chunk, embed, and upsert a single document into both ChromaDB collections.

    Used by ``POST /add-document`` in Part 3 Task 11.

    Args:
        doc_id: Unique document identifier.
        title: Document title.
        text: Document body content.
        chroma_dir: Persistent ChromaDB directory.

    Returns:
        Dict with number of chunks added per collection and total chunks added.
    """
    client = get_chroma_client(chroma_dir)
    f_chunks = fixed_chunks(doc_id, text, size=FIXED_CHUNK_SIZE, overlap=FIXED_CHUNK_OVERLAP)
    s_chunks = sentence_chunks(doc_id, text, per_chunk=SENTENCES_PER_CHUNK)

    added_counts: dict[str, int] = {}
    for col_name, chunk_list in (
        (COLLECTION_FIXED, f_chunks),
        (COLLECTION_SENTENCE, s_chunks),
    ):
        collection = client.get_or_create_collection(
            name=col_name,
            metadata={"hnsw:space": "cosine"},
        )
        if chunk_list:
            texts = [c["text"] for c in chunk_list]
            embeddings = embed_texts(texts)
            ids = [c["chunk_id"] for c in chunk_list]
            metadatas = [
                {
                    "doc_id": c["doc_id"],
                    "title": title,
                    "chunk_id": c["chunk_id"],
                    "strategy": c["strategy"],
                }
                for c in chunk_list
            ]
            collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )
        added_counts[col_name] = len(chunk_list)

    return {
        COLLECTION_FIXED: added_counts[COLLECTION_FIXED],
        COLLECTION_SENTENCE: added_counts[COLLECTION_SENTENCE],
        "total": added_counts[COLLECTION_FIXED] + added_counts[COLLECTION_SENTENCE],
    }


def main() -> None:
    """Build both ChromaDB collections and run a smoke retrieval query on each."""
    from rag.retrieve import retrieve

    counts = build_indices()
    print("=== Knowledge Base Chunking & Indexing Report (Tasks 2 & 3) ===")
    print(f"Embedding model            : {EMBEDDING_MODEL_NAME}")
    print(f"Total KB documents indexed : {counts['doc_count']} (required: >= 12)")
    print(
        f"Collection '{COLLECTION_FIXED}'      : {counts[COLLECTION_FIXED]} chunks "
        f"(size={FIXED_CHUNK_SIZE} chars, overlap={FIXED_CHUNK_OVERLAP} chars)"
    )
    print(
        f"Collection '{COLLECTION_SENTENCE}'   : {counts[COLLECTION_SENTENCE]} chunks "
        f"({SENTENCES_PER_CHUNK} sentences/chunk)"
    )

    sample_query = "What is the standard notice period for software engineers and can unused leave offset it?"
    print(f"\n=== Smoke Retrieval Test ===\nSample query: {sample_query!r}")
    for col_name in (COLLECTION_FIXED, COLLECTION_SENTENCE):
        hits = retrieve(sample_query, k=3, collection_name=col_name)
        print(f"\n--- Top-3 from '{col_name}' ---")
        for rank, h in enumerate(hits, start=1):
            print(
                f"  [{rank}] doc_id={h['doc_id']:<24} chunk_id={h['chunk_id']:<34} "
                f"similarity={h['similarity']:.4f}\n      text: {h['text']}"
            )


if __name__ == "__main__":
    main()
