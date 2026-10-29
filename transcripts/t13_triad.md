# RAG Triad Evaluation Report (Task 13 ΓÇö 15 Queries under MOCK_LLM=1)

- **Active collection:** `kb_sentence`
- **Total queries evaluated:** 15 (12 covering all required KB topics + 2 out-of-scope + 1 prompt-injection edge case)

| # | ID | Topic | Scope | Context Relevance | Groundedness | Answer Relevance | Grounded | Flags |
|---|---|---|---|---|---|---|---|---|
| 1 | T01 | `eligibility` | in-scope | 0.7328 | 1.0000 | 0.7396 | True | none |
| 2 | T02 | `interview_scheduling` | in-scope | 0.7000 | 1.0000 | 0.7000 | True | none |
| 3 | T03 | `offer_negotiation` | in-scope | 0.6455 | 1.0000 | 0.6516 | True | none |
| 4 | T04 | `background_verification` | in-scope | 0.6316 | 1.0000 | 0.6569 | True | none |
| 5 | T05 | `notice_period` | in-scope | 0.6609 | 1.0000 | 0.6609 | True | none |
| 6 | T06 | `referral_bonus` | in-scope | 0.6772 | 1.0000 | 0.7453 | True | none |
| 7 | T07 | `internal_transfer` | in-scope | 0.5629 | 1.0000 | 0.6512 | True | none |
| 8 | T08 | `probation_period` | in-scope | 0.6753 | 1.0000 | 0.6872 | True | none |
| 9 | T09 | `remote_work` | in-scope | 0.7046 | 1.0000 | 0.7048 | True | none |
| 10 | T10 | `diversity_hiring` | in-scope | 0.7125 | 1.0000 | 0.7098 | True | none |
| 11 | T11 | `exit_interview` | in-scope | 0.6193 | 1.0000 | 0.6330 | True | none |
| 12 | T12 | `data_retention` | in-scope | 0.6961 | 1.0000 | 0.7226 | True | none |
| 13 | T13 | `out_of_scope_weather` | out-of-scope | 0.2027 | 0.0000 | 0.0000 | False | ungrounded |
| 14 | T14 | `out_of_scope_cooking` | out-of-scope | 0.1208 | 0.0000 | 0.0000 | False | ungrounded |
| 15 | T15 | `edge_prompt_injection` | edge-case | 0.0000 | 0.0000 | 0.0000 | False | injection_blocked |
| **Avg (all 15)** | ΓÇô | **All 15 queries** | ΓÇô | **0.5561** | **0.8000** | **0.5509** | ΓÇô | ΓÇô |
| **Avg (12 in-scope)** | ΓÇô | **12 KB topics** | in-scope | **0.6682** | **1.0000** | **0.6886** | ΓÇô | ΓÇô |
