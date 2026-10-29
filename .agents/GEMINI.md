# Project Rules — Naukri Support Agent

Read this before every change. These rules override convenience.

## 1. Hard constraints (never break)
- Everything must work under `MOCK_LLM=1` with **zero API keys** and **no runtime network**.
- Never add paid services. A real LLM may exist only behind an env flag and is never used in graded transcripts.
- No images, screenshots, PDFs, slides, audio or video in the repo.
- Use only **fabricated** PII. Never log raw phone numbers; mask before logging (same masker as model input).
- Never hand-edit dataset records to meet thresholds — change seed/weights and regenerate.
- Never use untested similarity thresholds; calibrate with measured values (≥3 in-scope, ≥2 out-of-scope).
- Packages: `fastmcp` (no hyphen), `langgraph-checkpoint-sqlite`.
- MCP URL ends with `/mcp`.
- One public GitHub repo; README top states the Naukri.com (Recruitment & HR) track.

## 2. Fixed project values
| Item | Value |
|---|---|
| Categories | Software Engineer, Data Analyst, Product Manager, HR Executive, Sales Associate |
| Statuses | Applied, Screening, Interview Scheduled, Offered, Rejected |
| Dataset | ≥40 records; each category ≥3; each status ≥1; flagged 10–30% |
| Chroma collections | `kb_fixed`, `kb_sentence` |
| Embedding model | `all-MiniLM-L6-v2` |
| Ports | API 8001, MCP 8000, Vite 5173 |
| Memory file | `memory.json` |
| Checkpoint DB | `checkpoints.sqlite` |
| Log file | `logs/requests.jsonl` |
| Required KB topics | eligibility, interview scheduling, offer negotiation, background verification, notice period, referral bonus, internal transfer, probation, remote work, diversity hiring, exit interview, data retention |

## 3. Code conventions
- Python 3.10+, type hints everywhere, docstrings on public functions (tool docstrings are **required** — MCP uses them).
- Config lives in `config.py` (SEED, thresholds, paths, `MOCK_LLM`). No magic numbers in code.
- Modules small and single-purpose; no global random state (use `random.Random(SEED)`).
- File names snake_case. Record IDs `APP-0001`. Doc IDs = filename stem in `kb/`.
- Prefer pure functions; side effects (files, DB) isolated and path-configurable for tests.
- Do not remove or rewrite unrelated existing comments/docstrings when editing.
- Handle errors with clear messages; tools return error dicts rather than raising for user mistakes.

## 4. Evidence & documentation
- Transcripts: `transcripts/tNN_<name>.txt` (NN = task number). Save every demo.
- Record choices in `DECISIONS.md`, numbers in `EVALUATION.md`, progress in `CHANGELOG.md`.
- Fill README `TODO`s as soon as values are known.
- Every task done = code + transcript + test + doc update.

## 5. Git
- Commit style: `feat: task N <summary>`, `fix:`, `docs:`, `chore:`.
- Tags: `setup`, `part1`…`part4`, `frontend`, `v1.0`.
- `.gitignore`: `.venv/`, `chroma_db/`, `checkpoints.sqlite`, `memory.json`, `__pycache__/`, `node_modules/`.
- Commit transcripts and a sample `logs/requests.jsonl`.

## 6. Workflow per task
1. Read the task in `Doc/Question.md` and `prd.md`; follow `plan.md` order.
2. Implement → run → save transcript → add/adjust test.
3. Update `DECISIONS.md` / `EVALUATION.md` / `README.md` / `CHANGELOG.md`.
4. Commit.

## 7. Guardrail & logging rules
- Mask phone numbers (Indian formats) before anything is logged or sent to the model.
- Name, expected salary and background-check data are out of masking scope; fabricated only.
- Log one JSONL line per request: `trace_id`, timestamp, endpoint, masked query, route, latency, status code.
- Groundedness refusals use the calibrated threshold from `config.py`.

## 8. Frontend rules (optional phase)
- React + Vite + Tailwind **v4**; friendly copy; accessible components (see `FRONTEND.md`).
- API base from `VITE_API_URL`; never hard-code URLs.
- No images/screenshots in the repo.

## 9. Do / Don't quick list
| Do | Don't |
|---|---|
| Measure then choose thresholds | Use 0.5/0.6/0.7 presets |
| Regenerate with new seed | Hand-edit records |
| Mask before logging | Log raw phone numbers |
| Use `fastmcp` | Install `fast-mcp` |
| Reuse the same `thread_id` on resume | Create a new thread when resuming |
| Dedupe chunks → docs before P/R | Score at chunk level |
| Keep demos deterministic | Depend on network or keys |
