# Changelog

Format: newest first. One entry per phase/tag. Commit style: `feat: task N <summary>`, `fix:`, `docs:`, `chore:`.

## [v1.0] — 2026-10-29
### Added
- **Phase 0 (`setup`)**: Created virtual environment, `requirements.txt`, `.gitignore`, central `config.py`, and deterministic extractive `agent/llm.py`.
- **Part 1 (`part1`, Tasks 1–5)**:
  - `dataset.py`: Deterministic 60-record job-application generator (`SEED=42`, `flagged=18.33%`) and `validate_dataset()`.
  - `kb/*.md`: Authored 12 domain policy documents (4 sentences each) covering all required Naukri.com topics.
  - `rag/chunking.py` & `rag/index.py`: Implemented fixed-size (`kb_fixed`, 48 chunks) and sentence-based (`kb_sentence`, 24 chunks) strategies indexed in ChromaDB with `all-MiniLM-L6-v2`.
  - `rag/calibrate.py` & `rag/generate.py`: Calibrated groundedness threshold (`SIM_THRESHOLD=0.4296`) from empirical cluster midpoint (`min_in=0.6196`, `max_oos=0.2396`) and demonstrated grounded generation + OOS fallback.
  - `rag/eval_retrieval.py`: Evaluated document-level Precision@3 and Recall@3 across both collections (`1.0000` R@3 on both).
- **Part 2 (`part2`, Tasks 6–10)**:
  - `agent/tools.py`: Implemented `check_job_application_status` with escalation formula `0.6*flagged + 0.4*(days/30)` and 80th-percentile threshold `0.3600`.
  - `agent/graph.py` & `agent/state.py`: Built 7-node LangGraph workflow with conditional routing (`guard_input` -> `route_intent` -> `rag_retrieve` | `status_lookup` -> `generate_answer` -> `guard_output` -> `format_response`).
  - `agent/memory.py`: Added persistent JSON conversation memory (`memory.json`) with multi-turn vs fresh-conversation transcripts.
  - `agent/response_schema.json`: Enforced JSON Schema validation on every agent response.
  - `agent/guardrails.py`: Implemented Indian phone number PII masking (`[PHONE_MASKED]`), prompt-injection blocking, and output groundedness refusal.
- **Part 3 (`part3`, Tasks 11–13)**:
  - `api/main.py` & `api/models.py`: Deployed FastAPI service with `POST /ask`, `POST /add-document`, and `GET /health`.
  - `api/logging_utils.py`: Added structured JSONL logging (`logs/requests.jsonl`) with `trace_id`, latency timing, and verified PII masking.
  - `eval/test_queries.json` & `eval/triad.py`: Evaluated 15 queries with deterministic `MOCK_LLM` RAG-triad judge (`avg_context_relevance=0.5561`, `avg_groundedness=0.8000`, `avg_answer_relevance=0.5509` across all 15; `0.6682 / 1.0000 / 0.6886` across 12 in-scope topics).
- **Part 4 (`part4`, Tasks 14–16)**:
  - `mcp_server/server.py` & `mcp_server/client.py`: Exposed `check_job_application_status` via `fastmcp` at `http://127.0.0.1:8000/mcp` and verified multi-ID client round trip.
  - `resilience/checkpoint_demo.py`: Demonstrated `SqliteSaver` pause (`interrupt_before=["generate_answer"]`) and resume on the same `thread_id` without re-executing completed nodes.
  - `resilience/timeout_retry_demo.py`: Demonstrated exponential-backoff `RetryPolicy` recovery (attempt 3 of 4), per-node timeout (`1.0s`), and global graph timeout (`2.0s`).

---

## Progress tracker
| Tag | Phase | Tasks | Status | Date | Notes |
|---|---|---|---|---|---|
| `setup` | Phase 0 — environment | – | ✅ | 2026-10-29 | venv, deps, model verified |
| `part1` | Dataset & RAG core | 1–5 | ✅ | 2026-10-29 | 60 records, 12 KB docs, 2 collections, calibrated threshold `0.4296` |
| `part2` | LangGraph agent | 6–10 | ✅ | 2026-10-29 | 7 nodes, conditional routing, memory, schema, 3 guardrails |
| `part3` | API, logging, eval | 11–13 | ✅ | 2026-10-29 | FastAPI, masked JSONL logs, 15-query RAG triad |
| `part4` | MCP & resilience | 14–16 | ✅ | 2026-10-29 | FastMCP `/mcp`, SQLite checkpoint resume, retries & timeouts |
| `v1.0` | Final submission | 1–16 | ✅ | 2026-10-29 | All transcripts saved in UTF-8; all pytest tests passing |

## Task tracker
| Task | Description | Done | Transcript saved | Test added | Docs updated |
|---|---|---|---|---|---|
| 1 | Dataset | ✅ | ✅ `t01_dataset.txt` | ✅ `test_dataset.py` | ✅ |
| 2 | Knowledge base | ✅ | – (`kb/*.md`) | ✅ `test_kb.py` | ✅ |
| 3 | Chunk + index (2 collections) | ✅ | ✅ `t03_index.txt` | ✅ `test_rag.py` | ✅ |
| 4 | Grounded generation + threshold | ✅ | ✅ `t04_calibration.txt`, `t04_grounded.txt` | ✅ `test_rag.py` | ✅ |
| 5 | P@3 / R@3 comparison | ✅ | ✅ `t05_pr_at3.txt` | ✅ `test_rag.py` | ✅ |
| 6 | Status tool + escalation | ✅ | ✅ `t06_status_tool.txt` | ✅ `test_agent.py` | ✅ |
| 7 | LangGraph agent | ✅ | ✅ `t07_routes.txt` | ✅ `test_agent.py` | ✅ |
| 8 | Persisted memory | ✅ | ✅ `t08_memory_multi.txt`, `t08_memory_fresh.txt` | ✅ `test_agent.py` | ✅ |
| 9 | Structured output schema | ✅ | ✅ `t09_schema.txt` | ✅ `test_agent.py` | ✅ |
| 10 | Guardrails | ✅ | ✅ `t10_guard_pii.txt`, `t10_guard_injection.txt`, `t10_guard_grounded.txt` | ✅ `test_guardrails.py` | ✅ |
| 11 | FastAPI | ✅ | ✅ `t11_api.txt` | ✅ `test_api.py` | ✅ |
| 12 | Structured logging | ✅ | ✅ `t12_log_check.txt`, `logs/requests.jsonl` | ✅ `test_api.py` | ✅ |
| 13 | RAG triad (15 queries) | ✅ | ✅ `t13_triad.md` | ✅ `test_eval.py` | ✅ |
| 14 | MCP server + client | ✅ | ✅ `t14_mcp_server.txt`, `t14_mcp_client.txt` | ✅ `test_resilience.py` | ✅ |
| 15 | SQLite checkpointing | ✅ | ✅ `t15_checkpoint.txt` | ✅ `test_resilience.py` | ✅ |
| 16 | Timeouts & retries | ✅ | ✅ `t16_retry.txt`, `t16_node_timeout.txt`, `t16_global_timeout.txt` | ✅ `test_resilience.py` | ✅ |
