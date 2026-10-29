# Implementation Plan — Naukri.com Support Agent (14 Days)

Companion to [prd.md](prd.md). Tick boxes as you go. Each phase ends with an **exit check**
and saved transcripts in `transcripts/`.

## Timeline Overview
| Phase | Days | Focus | Marks |
|---|---|---|---|
| 0 | 1 | Setup & scaffolding | – |
| 1 | 2–5 | Dataset & RAG core | 30 |
| 2 | 6–8 | LangGraph agent, memory, guardrails | 30 |
| 3 | 9–10 | FastAPI, logging, RAG-triad eval | 20 |
| 4 | 11–13 | MCP, checkpointing, timeouts/retries | 20 |
| 5 | 14 | Polish, README, clean-clone test, submit | – |

> Buffer rule: if a phase slips, shorten Phase 5 polish, never skip a task's transcript.

---

## Phase 0 — Setup (Day 1)
**Goal:** reproducible environment and skeleton.

- [x] Create repo, `git init`, `.gitignore` (`.venv/`, `chroma_db/`, `checkpoints.sqlite`, `__pycache__/`, `logs/`)
- [x] Create folders: `kb rag agent api eval mcp_server resilience tests transcripts logs`
- [x] Create venv, install dependencies, freeze `requirements.txt`
- [x] `config.py`: `SEED`, `SIM_THRESHOLD` (placeholder), paths, `MOCK_LLM = os.getenv("MOCK_LLM","1")=="1"`
- [x] `agent/llm.py`: `generate(prompt, context)`; mock = deterministic extractive answer; real LLM branch behind flag (stub only)
- [x] README skeleton: track statement at top, "How to run", sections for each Part
- [x] Download embedding model once (`SentenceTransformer("all-MiniLM-L6-v2")`) to verify it works

**Exit check:** `python -c "import langgraph, chromadb, fastmcp, fastapi"` succeeds; first git commit made.

---

## Phase 1 — Dataset & RAG Core (Days 2–5)

### Day 2 — Task 1: Dataset
- [x] Write `dataset.py` with `random.Random(SEED)`, weights for categories/statuses
- [x] Per-category salary ranges (INR/yr), pick realistic bands; write one-sentence justification as a comment and in README
- [x] Generate 60 records; `record_id = APP-0001...`
- [x] Add `validate_dataset()` asserting: ≥40 records, each category ≥3, each status ≥1, flagged in [10%, 30%], days in [0, 30], unique ids
- [x] Print count per category, per status, flagged %; save to `transcripts/t01_dataset.txt`
- [x] If flagged % is off, adjust SEED/weights and regenerate (do NOT hand-edit)
- [x] `tests/test_dataset.py` (determinism: two runs equal)
- [x] Record SEED and weights in README

### Day 3 — Task 2: Knowledge base
- [x] Write 12 docs in `kb/` (2–5 sentences each, own words, fictional but specific numbers)
- [x] Topic checklist: eligibility · interview scheduling · offer negotiation · background verification · notice period · referral bonus · internal transfer · probation · remote work · diversity hiring · exit interview · data retention
- [x] Use distinct vocabulary per doc (avoid copy-paste phrasing)
- [x] Script checks: file count ≥12, sentence count 2–5 each

### Day 3–4 — Task 3: Chunking & indexing
- [x] `rag/chunking.py`: `fixed_chunks(text, size=200, overlap=40)` and `sentence_chunks(text, per_chunk=1 or 2)`
- [x] Each chunk: `{doc_id, chunk_id, text, strategy}`
- [x] `rag/index.py`: load embedder, build `kb_fixed` and `kb_sentence` collections (cosine), persistent client
- [x] Idempotent: delete & recreate collections on rerun
- [x] Print chunk counts per strategy + a sample query top-3 from each; save `t03_index.txt`

### Day 4 — Task 4: Grounded generation
- [x] `rag/retrieve.py`: `retrieve(query, k=3, collection)` returning text, doc_id, similarity = 1 − distance
- [x] `rag/calibrate.py`: ≥3 in-scope + ≥2 OOS queries; print top-1 similarities; compute gap and pick threshold in the middle; save `t04_calibration.txt`
- [x] Write chosen threshold into `config.py` and README with measured values
- [x] `rag/generate.py`: if top-1 < threshold → fallback string; else mock-LLM composes answer from retrieved chunks with sources
- [x] Demo ≥5 in-scope + 1 OOS; save `t04_grounded.txt`

### Day 5 — Task 5: Retrieval evaluation
- [x] Define ground truth: `{query: [relevant doc_ids]}` for the same ≥5 queries
- [x] `rag/eval_retrieval.py`: top-3 chunks → parent docs → dedupe → P@3 and R@3
- [x] Print per-query arithmetic, e.g. `P@3 = 1/2 = 0.50, R@3 = 1/1 = 1.00`, for both collections + averages
- [x] Write recommendation (2–3 sentences with numbers) in README; set `ACTIVE_COLLECTION` in config
- [x] `tests/test_rag.py` basic tests (fallback fires on OOS)

**Exit check (Part 1):** all five Part 1 acceptance bullets satisfied; transcripts saved; commit + tag `part1`.

---

## Phase 2 — LangGraph Agent (Days 6–8)

### Day 6 — Task 6 & guardrail code
- [x] `agent/tools.py`: `check_job_application_status(record_id)` with docstring
- [x] Escalation formula: `0.6*flagged + 0.4*(days/30)`; compute score for all records
- [x] Choose threshold from distribution (e.g. 80th percentile of scores); print percentiles; justify in README
- [x] Handle unknown/invalid ids gracefully
- [x] Demo ≥3 ids (flagged/old, flagged/new, unflagged); save `t06_status_tool.txt`
- [x] `agent/guardrails.py`: `mask_pii()` (phone regex), `detect_injection()` (pattern list), `check_grounded()` (threshold)
- [x] `tests/test_guardrails.py`

### Day 7 — Tasks 7 & 9: Graph + schema
- [x] `agent/state.py` TypedDict state
- [x] Nodes: `guard_input`, `route_intent`, `rag_retrieve`, `status_lookup`, `generate_answer`, `guard_output`, `format_response`
- [x] Conditional edges: after `guard_input` (blocked → format_response), after `route_intent` (policy vs status)
- [x] Intent rules: `APP-\d+` regex or keywords (status/application/escalat) → status route
- [x] `agent/response_schema.json` + `validate_response()`; call in `format_response`
- [x] Demo both routes with different queries; save `t07_routes.txt`, `t09_schema.txt`
- [x] `tests/test_agent.py`

### Day 8 — Tasks 8 & 10: Memory + guardrail demos
- [x] `agent/memory.py`: load/save `memory.json` keyed by `conversation_id`
- [x] Follow-up resolution: reuse last `record_id` from history
- [x] Transcript A (multi-turn: ask status, then "what is its salary?") → `t08_memory_multi.txt`
- [x] Transcript B (fresh conversation, same follow-up → asks for record id) → `t08_memory_fresh.txt`
- [x] Guardrail demos: phone masked, injection blocked, OOS refused (3 files)
- [x] Confirm every demo response passes schema validation

**Exit check (Part 2):** graph visibly routes both ways; schema validation never fails; commit + tag `part2`.

---

## Phase 3 — API, Logging, Evaluation (Days 9–10)

### Day 9 — Tasks 11 & 12
- [x] `api/models.py`: `AskRequest`, `AskResponse`, `AddDocRequest`, `AddDocResponse`
- [x] `api/main.py`: `POST /ask`, `POST /add-document`, `GET /health`; load graph once at startup
- [x] `/add-document`: chunk with both strategies, embed, add to both collections
- [x] `api/logging_utils.py`: middleware generating `trace_id` (uuid4), timing via `perf_counter`, append JSONL
- [x] Log only masked query text; add masked phone test
- [x] Test with `TestClient` + curl; save `t11_api.txt`
- [x] Log check script: send phone number request, grep log file → none found; save `t12_log_check.txt`
- [x] `tests/test_api.py`

### Day 10 — Task 13: RAG triad
- [x] `eval/test_queries.json`: 15 queries (12 topic-covering + 3 OOS/edge, e.g. weather, empty-ish, injection-like)
- [x] `eval/triad.py`: mock judge — context relevance (query↔context), groundedness (answer↔context overlap), answer relevance (query↔answer)
- [x] Score range 0–1, deterministic; print table of 15 rows + averages
- [x] Save `transcripts/t13_triad.md`; add summary to README

**Exit check (Part 3):** API runs; every request logged; table complete; commit + tag `part3`.

---

## Phase 4 — Resilience & MCP (Days 11–13)

### Day 11 — Task 14: MCP
- [x] `mcp_server/server.py`: `mcp = FastMCP("naukri-status")`; tool with docstring; `mcp.run(transport="http", host="127.0.0.1", port=8000)`
- [x] `mcp_server/client.py`: `async with Client("http://127.0.0.1:8000/mcp")`; call for 2+ record ids; print responses
- [x] Run server and client in separate terminals; save `t14_mcp_server.txt`, `t14_mcp_client.txt`
- [x] Note port: API uses 8001 to avoid conflict

### Day 12 — Task 15: Checkpointing
- [x] Build a graph variant (or reuse main graph) with `SqliteSaver.from_conn_string("checkpoints.sqlite")`
- [x] Add per-node execution counters/logs (`[EXEC] node=...`)
- [x] Demo script phases:
  - (a) run with `interrupt_before=["<node3>"]` → nodes 1–2 execute
  - (b) print `graph.get_state(config)` (`next`, values)
  - (c) resume with `invoke(None, config)` on same `thread_id` → only remaining nodes execute
- [x] Show printed proof: counters for node 1–2 unchanged after resume
- [x] Save `t15_checkpoint.txt`

### Day 13 — Task 16: Timeouts & retries
- [x] Flaky node using a module counter (fails first 2 calls)
- [x] Attach `RetryPolicy(max_attempts=4, initial_interval=0.5, backoff_factor=2.0, max_interval=4.0, jitter=True)`; log attempt timings
- [x] Per-node timeout wrapper with `asyncio.wait_for`; slow node (`sleep` > timeout) → clean `NodeTimeoutError`
- [x] Global timeout: `asyncio.wait_for(graph.ainvoke(...), timeout=N)`; slow multi-node run → clean cancellation message
- [x] Save `t16_retry.txt`, `t16_node_timeout.txt`, `t16_global_timeout.txt`
- [x] Document all numbers in README

**Exit check (Part 4):** all three resilience demos and MCP round trip pass; commit + tag `part4`.

---

## Phase 5 — Polish & Submission (Day 14)
- [ ] Run `pytest` — all green
- [ ] Fresh clone in a new folder → new venv → `pip install -r requirements.txt` → run each demo with `MOCK_LLM=1`, no keys
- [ ] README final: track statement at top; dataset choices (seed, weights, salary range + reason); threshold calibration values; escalation formula + threshold; P@3/R@3 tables + recommendation; triad averages; retry/timeout settings; how to run each step; "runs with zero API keys"
- [ ] Walk the acceptance checklist in `prd.md` §11; tick every item
- [ ] Verify no images/PDF/video/secrets in repo
- [ ] Ensure transcripts are committed (remove `logs/` from `.gitignore` or commit a sample log)
- [ ] Push to public GitHub repo; open the URL in an incognito window to confirm
- [ ] Submit the repo link

---

## Phase 6 — Optional: React UI & Deployment (after Part 4, only if time remains)
See [FRONTEND.md](FRONTEND.md) and [DEPLOYMENT.md](DEPLOYMENT.md).
- [x] Scaffold `frontend/` (Vite + React + Tailwind v4)
- [x] Add CORS (`ALLOWED_ORIGINS`) to `api/main.py`
- [x] Build components: chat, route badge, guardrail chips, status card + escalation meter
- [x] Add `Dockerfile`; deploy backend to Hugging Face Spaces; check `/health`
- [x] Deploy frontend to Vercel with `VITE_API_URL`
- [x] Tag `frontend`; update CHANGELOG and README link

---

## Daily Working Routine
1. Read the phase tasks → implement → run → save transcript.
2. Run related tests.
3. Commit with a task-labelled message (`feat: task 4 grounded generation`).
4. Update the checkboxes here.

## Definition of Done per Task
Code runs from a clean shell · transcript saved · README updated · test (if applicable) passing.

## Common Pitfalls Checklist
- [ ] Package names: `fastmcp` and `langgraph-checkpoint-sqlite`
- [ ] MCP URL ends with `/mcp`
- [ ] Don't use 0.5/0.6/0.7 threshold without measurements
- [ ] Map chunks → docs and dedupe before P@3/R@3
- [ ] Never log raw phone numbers
- [ ] Same thread ID on resume
- [ ] Seed fixed before generating final dataset; never hand-edit records
