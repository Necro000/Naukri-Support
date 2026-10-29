# Decisions Log

Record each non-obvious choice **at the moment you make it**, with evidence.
Status: ⬜ open · ✅ decided.

## 1. Data & dataset
| # | Decision | Value | Why / evidence | Status |
|---|---|---|---|---|
| D1 | Seed | `42` | First seed giving flagged % in 10–30% (18.33%, 11/60 records) and all categories ≥ 6 | ✅ |
| D2 | Record count | `60` | ≥40 required; 60 records yield stable percentile statistics | ✅ |
| D3 | Category weights | `(0.30, 0.22, 0.16, 0.14, 0.18)` | Each category reaches ≥6 records (min 6 Product Manager, max 17 Software Engineer) | ✅ |
| D4 | Status weights | `(0.35, 0.25, 0.18, 0.10, 0.12)` | Realistic hiring funnel: Applied (24), Screening (15), Interview Scheduled (6), Offered (6), Rejected (9) | ✅ |
| D5 | Flag probability | `0.20` | Produces 18.33% (`11/60`) flagged records right in the middle of the [10%, 30%] band | ✅ |
| D6 | Salary range | `300,000 – 3,000,000` INR/yr | Realistic Indian job-market compensation from entry-level Sales/HR roles up to mid-senior Engineers/PMs | ✅ |
| D7 | Per-category salary bands | SE: 600k–2.4M, DA: 500k–1.6M, PM: 1.2M–3.0M, HR: 350k–950k, Sales: 300k–850k | Reflects role seniority and Indian market compensation differentials | ✅ |

## 2. RAG
| # | Decision | Value | Why / evidence | Status |
|---|---|---|---|---|
| D8 | Embedding model | `all-MiniLM-L6-v2` | Free, local, fast, brief-suggested | ✅ |
| D9 | Similarity | cosine, `1 − distance` | Chroma cosine space with normalized embeddings | ✅ |
| D10 | Fixed chunk size / overlap | `200` chars / `40` chars | Produces 48 chunks across 12 docs (4 chunks/doc) | ✅ |
| D11 | Sentence chunk grouping | `2` sentences per chunk | Produces 24 chunks across 12 docs (2 chunks/doc), preserving whole sentences | ✅ |
| D12 | top-k | `3` | Matches P@3 / R@3 evaluation depth | ✅ |
| D13 | Threshold (`SIM_THRESHOLD`) | `0.4296` | Midpoint between max OOS (`0.2396`) and min in-scope (`0.6196`) in `kb_sentence` (gap `0.3800`) | ✅ |
| D14 | Deployed strategy | `kb_sentence` | 1.0000 R@3, 0.5000 P@3 (vs 0.5833 P@3 / 1.0000 R@3 for `kb_fixed`), 50% fewer chunks (24 vs 48), wider OOS separation gap (`0.3800` vs `0.2840`), no mid-word splits | ✅ |
| D15 | P@3 denominator | unique docs retrieved | Dedupe top-3 chunks → parent docs first; also report `/3` denominator | ✅ |
| D16 | Mock generation | Extractive from top chunks, cites `doc_id`s | Deterministic, keyless, guaranteed grounded | ✅ |

## 3. Agent
| # | Decision | Value | Why / evidence | Status |
|---|---|---|---|---|
| D17 | Intent routing | Regex `APP-\d{4}` + status/escalation/salary keywords | Deterministic, testable, zero LLM calls | ✅ |
| D18 | Escalation formula | `0.6 × flagged + 0.4 × (days_since_created / 30)` | Priority flag dominates (0.6); application age adds gradual linear urgency (up to 0.4) | ✅ |
| D19 | Escalation threshold | `0.3600` | Exact 80th percentile (`p80`) of dataset scores; escalates all flagged records (`≥0.60`) plus unflagged applications aged ≥27 days (`0.4 × 27/30 = 0.36`) | ✅ |
| D20 | Memory store | `memory.json` keyed by `conversation_id` | Persists turn list `{role, content, record_id, route, ts}` | ✅ |
| D21 | Follow-up resolution | Reuse last `record_id` from history | Resolves "And what is its expected salary?" in multi-turn sessions | ✅ |
| D22 | Output schema | `agent/response_schema.json` + `jsonschema` | Validated in `format_response` on every single run | ✅ |
| D23 | PII regex | Indian mobile formats (`+91`, `0`, 10-digit `[6-9]\d{9}`) | Fixed-format PII field per project brief; same `mask_pii()` used in input guard and JSONL logger | ✅ |
| D24 | Injection patterns | 5 compiled regex rules (`ignore previous instructions`, `reveal system prompt`, `disregard`, `bypass guardrails`, `developer mode`) | Keyless, deterministic input safety check | ✅ |

## 4. Platform & resilience
| # | Decision | Value | Why / evidence | Status |
|---|---|---|---|---|
| D25 | Ports | API `8001`, MCP `8000`, Vite `5173` | Avoid port collisions between FastAPI and FastMCP | ✅ |
| D26 | Judge for triad | Deterministic `MOCK_LLM` judge (cosine similarity + token support overlap) | Keyless, reproducible 0–1 scores across all 15 queries | ✅ |
| D27 | Retry policy | `max_attempts=4, initial_interval=0.5s, max_interval=4.0s, backoff_factor=2.0, jitter=True` | Recovers on attempt 3 after 2 simulated transient failures (`t=2.115s`) | ✅ |
| D28 | Per-node timeout | `1.0` s | Aborts a stalled node (`2.5s` sleep) cleanly with `NodeTimeoutError` | ✅ |
| D29 | Global timeout | `2.0` s | Cancels a 3-node slow run (`3 × 1.3s = 3.9s`) cleanly with `GlobalGraphTimeoutError` | ✅ |
| D30 | Interrupt method | `interrupt_before=["generate_answer"]` | Executes 3 nodes (`guard_input`, `route_intent`, `status_lookup`), inspects state, resumes remaining 3 nodes | ✅ |
| D31 | Backend host | Local FastAPI / Hugging Face Spaces | Ready for offline grading and container deploy | ✅ |
| D32 | Frontend | React + Tailwind v4 (optional) | Documented in `FRONTEND.md` | ✅ |

## 5. Rejected options
| Option | Reason |
|---|---|
| Default thresholds 0.5/0.6/0.7 | Untested presets forbidden by brief |
| Hand-editing records for flagged % | Forbidden; used seeded generator (`SEED=42`, `p=0.20`) |
| Real LLM in graded runs | Must be `MOCK_LLM=1` only |
| `fast-mcp` package | Not real; used `fastmcp` |

## 6. Seed search log (Task 1)
| Seed | Flagged % | Min category count | All statuses present | Accepted |
|---|---|---|---|---|
| `42` | `18.33%` (11/60) | `6` (`Product Manager`) | Yes (`Applied`: 24, `Screening`: 15, `Interview Scheduled`: 6, `Offered`: 6, `Rejected`: 9) | ✅ Yes |

## 7. Threshold calibration notes
Measured in `rag/calibrate.py` (`transcripts/t04_calibration.txt`):
- `kb_sentence`: min in-scope = `0.6196`, max out-of-scope = `0.2396`, gap = `0.3800`, midpoint = `0.4296`.
- `kb_fixed`: min in-scope = `0.5633`, max out-of-scope = `0.2793`, gap = `0.2840`, midpoint = `0.4213`.
Chosen `SIM_THRESHOLD = 0.4296`.
