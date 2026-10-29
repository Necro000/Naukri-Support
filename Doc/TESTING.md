# Testing

Run everything: `pytest -q` (venv active, `$env:MOCK_LLM = "1"`).
Single file: `pytest tests\test_agent.py -q` · Verbose: add `-v` · Stop on first fail: `-x`.

## 1. Strategy
| Level | Tool | Goal |
|---|---|---|
| Unit | pytest | Pure functions (dataset, chunkers, guardrails, formula) |
| Integration | pytest | RAG + graph + API with `TestClient` |
| Demo/transcript | scripts | Evidence for graders (`transcripts/`) |
| Manual | checklist | MCP, clean clone, log grep |

All tests must pass offline with `MOCK_LLM=1`.

## 2. Test matrix
### `tests/test_dataset.py` (Task 1)
| Test | Assertion |
|---|---|
| `test_min_records` | ≥ 40 records |
| `test_unique_ids` | `APP-0001` format, unique |
| `test_category_coverage` | each of 5 categories ≥ 3 |
| `test_status_coverage` | each of 5 statuses ≥ 1 |
| `test_flagged_band` | 10% ≤ flagged ≤ 30% |
| `test_days_range` | 0 ≤ days ≤ 30, int |
| `test_salary_range` | within configured bounds |
| `test_deterministic` | two generations are identical |

### `tests/test_kb.py` (Task 2)
| Test | Assertion |
|---|---|
| `test_doc_count` | ≥ 12 files |
| `test_topics_present` | all 12 required stems exist |
| `test_sentence_count` | 2–5 sentences each |

### `tests/test_rag.py` (Tasks 3–5)
| Test | Assertion |
|---|---|
| `test_chunkers` | fixed chunks ≤ size; overlap respected; sentences not empty |
| `test_collections_exist` | both non-empty, separate names |
| `test_in_scope_above_threshold` | calibrated in-scope queries ≥ threshold |
| `test_oos_fallback` | OOS query returns fallback |
| `test_pr_bounds` | P@3, R@3 ∈ [0, 1]; dedupe to docs |

### `tests/test_agent.py` (Tasks 6–9)
| Test | Assertion |
|---|---|
| `test_status_fields` | has `status`, `expected_salary_inr`, `escalation_score` |
| `test_escalation_range` | ∈ [0, 1] for all records |
| `test_escalation_monotonic` | older + flagged scores ≥ newer + unflagged |
| `test_unknown_id` | returns error dict, no exception |
| `test_route_policy` / `test_route_status` | conditional edge picks the right node |
| `test_schema_valid` | every response validates |
| `test_schema_rejects_bad` | invalid payload raises |
| `test_memory_carryover` | follow-up resolves record id |
| `test_memory_fresh` | new conversation has no history |

### `tests/test_guardrails.py` (Task 10)
| Test | Assertion |
|---|---|
| `test_mask_phone_formats` | `+91 98765 43210`, `9876543210`, `+919876543210` masked |
| `test_no_false_mask` | `APP-0007` and years unchanged |
| `test_injection_detected` | known phrases flagged |
| `test_clean_query_not_blocked` | normal policy question passes |
| `test_ungrounded_refusal` | low score → refusal text |

### `tests/test_api.py` (Tasks 11–12)
| Test | Assertion |
|---|---|
| `test_health` | 200 + ok |
| `test_ask_policy` / `test_ask_status` | 200, schema-valid |
| `test_ask_validation` | empty query → 422 |
| `test_add_document` | chunks added in both collections |
| `test_add_document_duplicate` | 409 |
| `test_log_line` | JSONL line with `trace_id`, `latency_ms` |
| `test_no_raw_phone_in_log` | raw number absent from log file |

### `tests/test_eval.py` (Task 13)
| Test | Assertion |
|---|---|
| `test_15_queries` | 15 queries, ≥1 per topic, ≥2 OOS |
| `test_scores_bounds` | all three scores ∈ [0, 1]; averages computed |

### `tests/test_resilience.py` (Tasks 14–16)
| Test | Assertion |
|---|---|
| `test_retry_recovers` | succeeds on attempt 3; attempts logged |
| `test_node_timeout` | raises `NodeTimeoutError` within bound |
| `test_global_timeout` | `asyncio.TimeoutError` handled cleanly |
| `test_checkpoint_resume` | counters of finished nodes unchanged after resume |
| `test_mcp_tool_function` | underlying tool callable (server round trip is manual) |

## 3. Manual checks
- [ ] `python mcp_server\server.py` + `python mcp_server\client.py` → 2 IDs return results
- [ ] `Select-String logs\requests.jsonl -Pattern "<test phone>"` prints nothing
- [ ] Fresh clone + fresh venv runs `dataset.py`, `rag\index.py`, API with no API keys
- [ ] Every transcript file listed in README exists and is non-empty
- [ ] No image/PDF/video files: `Get-ChildItem -Recurse -Include *.png,*.jpg,*.pdf,*.mp4`

## 4. Fixtures & conventions
- `conftest.py`: fixture for `JOB_APPLICATIONS`, indexed temporary Chroma dir (`tmp_path`), `TestClient`.
- Use `tmp_path` for memory/log files — tests never touch real `memory.json`.
- Seed always from `config.SEED`; no reliance on global random state.
- Test names: `test_<behaviour>`; one assertion theme per test.

## 5. Coverage target
Core logic (`dataset.py`, `rag/`, `agent/`, `api/`): aim ≥ 80% line coverage.
```powershell
pip install pytest-cov
pytest --cov=. --cov-report=term-missing -q
```

## 6. Test run log
| Date | Command | Result | Notes |
|---|---|---|---|
| | `pytest -q` | | |
