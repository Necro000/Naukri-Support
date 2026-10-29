"""Central configuration for the Naukri.com Support Agent."""

from __future__ import annotations

import os
from pathlib import Path

# Project paths
ROOT_DIR: Path = Path(__file__).resolve().parent
KB_DIR: Path = ROOT_DIR / "kb"
CHROMA_DIR: Path = ROOT_DIR / "chroma_db"
LOGS_DIR: Path = ROOT_DIR / "logs"
REQUEST_LOG_PATH: Path = LOGS_DIR / "requests.jsonl"
MEMORY_PATH: Path = ROOT_DIR / "memory.json"
CHECKPOINT_DB_PATH: Path = ROOT_DIR / "checkpoints.sqlite"
TRANSCRIPTS_DIR: Path = ROOT_DIR / "transcripts"
EVAL_QUERIES_PATH: Path = ROOT_DIR / "eval" / "test_queries.json"
RESPONSE_SCHEMA_PATH: Path = ROOT_DIR / "agent" / "response_schema.json"

# Runtime LLM mode (default: deterministic mock LLM, zero API keys, zero network)
MOCK_LLM: bool = os.getenv("MOCK_LLM", "1") == "1"

# Dataset generation parameters (Task 1)
SEED: int = 42
NUM_RECORDS: int = 60
MAX_DAYS_SINCE_CREATED: int = 30
FLAGGED_PROBABILITY: float = 0.20

CATEGORIES: tuple[str, ...] = (
    "Software Engineer",
    "Data Analyst",
    "Product Manager",
    "HR Executive",
    "Sales Associate",
)
CATEGORY_WEIGHTS: tuple[float, ...] = (0.30, 0.22, 0.16, 0.14, 0.18)

STATUSES: tuple[str, ...] = (
    "Applied",
    "Screening",
    "Interview Scheduled",
    "Offered",
    "Rejected",
)
STATUS_WEIGHTS: tuple[float, ...] = (0.35, 0.25, 0.18, 0.10, 0.12)

# Per-category annual salary ranges in INR (realistic Indian entry-to-mid role bands)
SALARY_RANGES_INR: dict[str, tuple[int, int]] = {
    "Software Engineer": (600_000, 2_400_000),
    "Data Analyst": (500_000, 1_600_000),
    "Product Manager": (1_200_000, 3_000_000),
    "HR Executive": (350_000, 950_000),
    "Sales Associate": (300_000, 850_000),
}

# RAG & Embedding configuration (Tasks 3-5)
EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
COLLECTION_FIXED: str = "kb_fixed"
COLLECTION_SENTENCE: str = "kb_sentence"
ACTIVE_COLLECTION: str = COLLECTION_SENTENCE  # Updated after Task 5 evaluation

FIXED_CHUNK_SIZE: int = 200
FIXED_CHUNK_OVERLAP: int = 40
SENTENCES_PER_CHUNK: int = 2
TOP_K: int = 3

# Calibrated similarity threshold for grounded generation (Task 4)
# Midpoint of min in-scope (0.6196) and max out-of-scope (0.2396) in kb_sentence
SIM_THRESHOLD: float = 0.4296

# Escalation score configuration (Task 6)
ESCALATION_FLAG_WEIGHT: float = 0.6
ESCALATION_RECENCY_WEIGHT: float = 0.4
ESCALATION_THRESHOLD: float = 0.3600  # Exact 80th percentile (p80) of dataset scores

# Service ports & endpoints (Tasks 11, 14)
API_HOST: str = "127.0.0.1"
API_PORT: int = 8001
MCP_HOST: str = "127.0.0.1"
MCP_PORT: int = 8000
MCP_PATH: str = "/mcp"
MCP_URL: str = f"http://{MCP_HOST}:{MCP_PORT}{MCP_PATH}"

# Resilience configuration (Task 16)
RETRY_MAX_ATTEMPTS: int = 4
RETRY_INITIAL_INTERVAL: float = 0.5
RETRY_BACKOFF_FACTOR: float = 2.0
RETRY_MAX_INTERVAL: float = 4.0
RETRY_JITTER: bool = True
NODE_TIMEOUT_SECONDS: float = 1.0
GLOBAL_TIMEOUT_SECONDS: float = 2.0

# Refusal / fallback messages
FALLBACK_UNGROUNDED: str = (
    "I don't know based on the available policy information. "
    "Please contact Naukri.com employer support for questions outside our documented policies."
)
FALLBACK_INJECTION: str = (
    "Request blocked by input safety guardrail: prompt injection or instruction override attempt detected."
)
