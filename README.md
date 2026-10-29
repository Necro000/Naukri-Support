# Naukri.com Employer-Support Agent (LangGraph)

> ## ✅ Track completed: **Naukri.com (Recruitment & HR)**
> Everything runs under `MOCK_LLM=1` with **zero API keys** and **no network access at runtime**.
> (The SentenceTransformers model `all-MiniLM-L6-v2` is downloaded once on first use and cached locally.)

A production-minded support agent for Naukri.com's employer-support team. It:
- answers hiring-policy questions **only** from a knowledge base written for this project (RAG);
- looks up a job application's status from a seeded dataset and computes a designed escalation score;
- remembers conversations, masks PII, blocks prompt injection and refuses ungrounded answers;
- survives interruptions (SQLite checkpoints), transient failures (retries) and overruns (timeouts);
- exposes its lookup tool over MCP and its agent over FastAPI;
- is evaluated end-to-end (Precision@3 / Recall@3, RAG triad).

## Documentation index
| Doc | What it contains |
|---|---|
| [Doc/DECISIONS.md](Doc/DECISIONS.md) | Why every choice was made (seed, chunk sizes, threshold, weights, retry values) |
| [Doc/EVALUATION.md](Doc/EVALUATION.md) | P@3/R@3 tables, calibration values, RAG-triad table |
| [Doc/ARCHITECTURE.md](Doc/ARCHITECTURE.md) | Graph nodes, data flow, folder map |
| [Doc/API.md](Doc/API.md) | Endpoints, examples, log format, MCP tool |
| [Doc/RUNBOOK.md](Doc/RUNBOOK.md) | Commands per phase, troubleshooting, ports |
| [Doc/TESTING.md](Doc/TESTING.md) | Test list and manual checks |
| [Doc/DEPLOYMENT.md](Doc/DEPLOYMENT.md) | Vercel + Hugging Face Spaces (optional) |
| [Doc/FRONTEND.md](Doc/FRONTEND.md) | React + Tailwind UI (optional) |
| [Doc/CHANGELOG.md](Doc/CHANGELOG.md) | Progress per phase |
| [Doc/prd.md](Doc/prd.md) / [Doc/plan.md](Doc/plan.md) | Requirements and phase-wise plan |

---

## 1. Quick start (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:MOCK_LLM = "1"
python dataset.py
python rag\index.py
python rag\calibrate.py
python rag\generate.py
python rag\eval_retrieval.py
python agent\tools.py
python agent\graph.py demo_routes
uvicorn api.main:app --port 8001
```
Full command list: [Doc/RUNBOOK.md](Doc/RUNBOOK.md).

## 2. Dataset design choices (Task 1) — for deterministic reproduction
Re-running `python dataset.py` reproduces the exact dataset below.

| Choice | Value |
|---|---|
| Seed | `42` (`random.Random(42)`, no global random state) |
| Record count | `60` (≥ 40 required) |
| ID format | `APP-0001` … `APP-0060` |
| Category vocabulary | `Software Engineer`, `Data Analyst`, `Product Manager`, `HR Executive`, `Sales Associate` |
| Category weights | `(0.30, 0.22, 0.16, 0.14, 0.18)` |
| Status vocabulary | `Applied`, `Screening`, `Interview Scheduled`, `Offered`, `Rejected` |
| Status weights | `(0.35, 0.25, 0.18, 0.10, 0.12)` |
| `flagged_priority_review` probability | `0.20` |
| `days_since_created` | integer `0–30` |
| `expected_salary_inr` range | `300,000` – `3,000,000` INR per year (role-specific bands: Sales `300k–850k`, HR `350k–950k`, DA `500k–1.6M`, SE `600k–2.4M`, PM `1.2M–3.0M`) |
| Salary reasoning (one sentence) | Annual expected salaries span 300,000 to 3,000,000 INR across role-specific bands to reflect realistic Indian job-market compensation from entry-level Sales and HR roles up to experienced Software Engineers and Product Managers. |

**Generated dataset report** (`transcripts/t01_dataset.txt`):
| Category | Count (must be ≥3) |
|---|---|
| Software Engineer | `17` |
| Data Analyst | `13` |
| Product Manager | `6` |
| HR Executive | `9` |
| Sales Associate | `15` |

| Status | Count (must be ≥1) |
|---|---|
| Applied | `24` |
| Screening | `15` |
| Interview Scheduled | `6` |
| Offered | `6` |
| Rejected | `9` |

Flagged priority review: **`18.33%`** (`11 / 60` records, within the required `10% – 30%` band).

## 3. Knowledge base (Task 2)
12 documents in `kb/` (4 sentences each, authored in original wording): `eligibility.md`, `interview_scheduling.md`, `offer_negotiation.md`, `background_verification.md`, `notice_period.md`, `referral_bonus.md`, `internal_transfer.md`, `probation_period.md`, `remote_work.md`, `diversity_hiring.md`, `exit_interview.md`, `data_retention.md`. All figures are fictional.

## 4. Chunking & indexing (Task 3)
| Strategy | Collection | Parameters | Chunk count |
|---|---|---|---|
| Fixed-size with overlap | `kb_fixed` | size `200` chars, overlap `40` chars | `48` |
| Sentence-based | `kb_sentence` | `2` sentences per chunk | `24` |
Embedding model: `all-MiniLM-L6-v2` (local, free). Vector store: ChromaDB, cosine distance space (`transcripts/t03_index.txt`).

## 5. Calibrated "I don't know" threshold (Task 4)
Measured **before** choosing the threshold (`rag/calibrate.py`, saved in `transcripts/t04_calibration.txt`).

| Query | Type | Top-1 cosine similarity (`kb_sentence`) | Matched doc |
|---|---|---|---|
| How many active job applications can an external candidate submit in 90 days? | in-scope | `0.6383` | `eligibility` |
| What is the standard notice period for software engineers and can leave offset it? | in-scope | `0.6196` | `notice_period` |
| How much is the employee referral bonus for technical roles and when is it paid? | in-scope | `0.7259` | `referral_bonus` |
| How long are applicant resumes retained before automatic anonymization or deletion? | in-scope | `0.6874` | `data_retention` |
| What is the weather forecast for Mumbai tomorrow and will it rain during the cricket match? | out-of-scope | `0.2396` | `remote_work` |
| How do I bake a sourdough bread loaf using whole wheat flour at high altitude? | out-of-scope | `0.0992` | `eligibility` |
| Which cryptocurrency hardware wallet supports Solana staking rewards with zero gas fees? | out-of-scope | `0.1458` | `eligibility` |

- Lowest in-scope: `0.6196` · Highest out-of-scope: `0.2396` · Observed gap: `0.3800`
- **Chosen threshold (`SIM_THRESHOLD`): `0.4296`** (exact midpoint of the observed gap).
- Demonstrated on 6 in-scope queries (`0.5618` – `0.7314` → grounded answers) + 1 out-of-scope query (`0.1021 < 0.4296` → `"I don't know based on the available policy information..."` fallback) in `transcripts/t04_grounded.txt`.

## 6. Chunking comparison & recommendation (Task 5)
| Collection | Avg P@3 (unique-doc denom) | Avg P@3 (strict `/3` denom) | Avg R@3 | Chunk count |
|---|---|---|---|---|
| `kb_fixed` | `0.5833` | `0.3333` | `1.0000` | `48` |
| `kb_sentence` | `0.5000` | `0.3333` | `1.0000` | `24` |

**Recommendation:** We recommend deploying `kb_sentence` (2 sentences per chunk, 24 total chunks) as our active production collection (`ACTIVE_COLLECTION = "kb_sentence"`). Both `kb_sentence` and `kb_fixed` achieve a perfect `1.0000` average Recall@3 (`0.3333` strict `/3` Precision@3), while under the unique-document denominator `kb_fixed` scores `0.5833` P@3 vs `0.5000` for `kb_sentence` only because `kb_sentence` has 2 chunks per 4-sentence document (so retrieving `k=3` chunks always includes 1 runner-up document in rank 3). In exchange, `kb_sentence` reduces index size by 50% (`24` vs `48` chunks), yields a wider in-scope vs out-of-scope calibration gap (`0.3800` vs `0.2840`), and preserves complete policy sentences without mid-word boundary splits. Full per-query arithmetic: `transcripts/t05_pr_at3.txt` and [Doc/EVALUATION.md](Doc/EVALUATION.md).

## 7. Escalation score (Task 6)
- Formula: `escalation_score = clamp(0.6 × flagged_priority_review + 0.4 × (days_since_created / 30), 0.0, 1.0)`
- Recommended escalation threshold: **`0.3600`** (`15 / 60` records = `25.00%` recommended for escalation)
- Justification from own data: `0.3600` equals the exact **80th percentile (`p80`)** of the computed escalation scores in our 60-record dataset (`min=0.0000, p25=0.1200, p50=0.2800, p75=0.3600, p80=0.3600, p90=0.6933, max=0.9733`). Setting the threshold at `0.3600` ensures that all priority-flagged records (`score >= 0.6000`) are escalated immediately, AND unflagged applications that have aged `>= 27` days (`0.4 × 27/30 = 0.3600`) also trigger escalation before breaching the 30-day SLA (`transcripts/t06_status_tool.txt`).

## 8. Agent behaviour summary (Tasks 7–10)
| Feature | Summary |
|---|---|
| Graph | `7` nodes (`guard_input`, `route_intent`, `rag_retrieve`, `status_lookup`, `generate_answer`, `guard_output`, `format_response`), conditional edges after `guard_input` and `route_intent` |
| Routing | Policy → RAG (`rag_retrieve`); `APP-####` / status / escalation / salary keywords → status tool (`status_lookup`) |
| Memory | `memory.json` keyed by `conversation_id`; resolves follow-up pronouns (`"its expected salary"`) from last `record_id` |
| Output schema | `agent/response_schema.json`, validated via `jsonschema` on every response |
| Guardrails | Input phone masking (`[PHONE_MASKED]`, flag `pii_masked`), prompt-injection detection (flag `injection_blocked`), output groundedness refusal (`top_score < 0.4296`, flag `ungrounded`) |

## 9. API, logging, evaluation (Tasks 11–13)
- Endpoints: `POST /ask`, `POST /add-document`, `GET /health` → [Doc/API.md](Doc/API.md) (`transcripts/t11_api.txt`)
- Logs: one JSON-Lines entry per request in `logs/requests.jsonl` with `trace_id`, `latency_ms`, and **masked** query text (`[PHONE_MASKED]`, verified in `transcripts/t12_log_check.txt`).
- RAG triad averages across all **15 test queries** (`transcripts/t13_triad.md`):
  - All 15 queries (12 KB topics + 2 OOS + 1 injection edge case): Context Relevance **`0.5561`**, Groundedness **`0.8000`**, Answer Relevance **`0.5509`**.
  - 12 in-scope KB topic queries: Context Relevance **`0.6682`**, Groundedness **`1.0000`**, Answer Relevance **`0.6886`**.

## 10. Resilience & MCP (Tasks 14–16)
| Setting | Value |
|---|---|
| MCP server URL | `http://127.0.0.1:8000/mcp` (`fastmcp`, tool `check_job_application_status`) |
| Checkpoint DB / thread | `checkpoints.sqlite` (`langgraph-checkpoint-sqlite`) / `thread-checkpoint-demo-001` |
| Retry: max attempts | `4` (recovers on attempt `3` after `2` transient failures) |
| Retry: initial interval | `0.5` s |
| Retry: max interval | `4.0` s |
| Retry: backoff factor | `2.0` |
| Retry: jitter | `True` |
| Per-node timeout | `1.0` s (raises clean `NodeTimeoutError` on `2.5s` slow node) |
| Global timeout | `2.0` s (cancels `3.9s` multi-node run cleanly with `GlobalGraphTimeoutError`) |

## 11. Task → evidence map
| Task | Code | Transcript |
|---|---|---|
| 1 Dataset | `dataset.py` | `transcripts/t01_dataset.txt` |
| 2 KB | `kb/*.md` | – |
| 3 Chunk & index | `rag/chunking.py`, `rag/index.py` | `transcripts/t03_index.txt` |
| 4 Grounded generation | `rag/calibrate.py`, `rag/generate.py` | `transcripts/t04_calibration.txt`, `transcripts/t04_grounded.txt` |
| 5 P@3 / R@3 | `rag/eval_retrieval.py` | `transcripts/t05_pr_at3.txt` |
| 6 Status tool | `agent/tools.py` | `transcripts/t06_status_tool.txt` |
| 7 Graph | `agent/graph.py` | `transcripts/t07_routes.txt` |
| 8 Memory | `agent/memory.py` | `transcripts/t08_memory_multi.txt`, `transcripts/t08_memory_fresh.txt` |
| 9 Schema | `agent/response_schema.json` | `transcripts/t09_schema.txt` |
| 10 Guardrails | `agent/guardrails.py` | `transcripts/t10_guard_pii.txt`, `transcripts/t10_guard_injection.txt`, `transcripts/t10_guard_grounded.txt` |
| 11 API | `api/main.py`, `api/demo_api.py` | `transcripts/t11_api.txt` |
| 12 Logging | `api/logging_utils.py` | `transcripts/t12_log_check.txt`, `logs/requests.jsonl` |
| 13 RAG triad | `eval/triad.py`, `eval/test_queries.json` | `transcripts/t13_triad.md` |
| 14 MCP | `mcp_server/server.py`, `mcp_server/client.py` | `transcripts/t14_mcp_server.txt`, `transcripts/t14_mcp_client.txt` |
| 15 Checkpointing | `resilience/checkpoint_demo.py` | `transcripts/t15_checkpoint.txt` |
| 16 Timeouts/retries | `resilience/timeout_retry_demo.py` | `transcripts/t16_retry.txt`, `transcripts/t16_node_timeout.txt`, `transcripts/t16_global_timeout.txt` |

## 12. Constraints honoured
- `MOCK_LLM=1` only for all graded transcripts; no API keys needed; no paid services.
- Fabricated data only; phone numbers masked before logging.
- No images, PDFs, slides, audio or video in the repo.
- Dataset, KB and code are original work for this brief.
- Packages: `fastmcp`, `langgraph-checkpoint-sqlite`.

## 13. Submission checklist
- [x] README top states the Naukri.com track
- [x] All values above are filled with measured outputs
- [x] Transcripts for every task are committed
- [x] `pytest -q` passes (21 passed)
- [x] Clean clone runs with no API keys
- [x] Single public GitHub repo link ready for submission
