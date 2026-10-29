# Runbook

Every new terminal:
```powershell
cd "d:\Ai notes\Recruitment"
.\.venv\Scripts\Activate.ps1
$env:MOCK_LLM = "1"
```

## 0. One-time setup
```powershell
git init
mkdir kb, rag, agent, api, eval, mcp_server, resilience, tests, transcripts, logs
python --version                      # needs 3.10+
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install langgraph langgraph-checkpoint-sqlite langchain-core chromadb sentence-transformers fastmcp fastapi "uvicorn[standard]" pydantic jsonschema pytest httpx
pip freeze > requirements.txt
"__pycache__/`n.venv/`nchroma_db/`ncheckpoints.sqlite`nmemory.json" | Out-File -Encoding utf8 .gitignore
python -c "import langgraph, chromadb, fastmcp, fastapi; print('imports ok')"
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2'); print('model ok')"
git add .; git commit -m "chore: project setup"; git tag setup
```
Script blocked? `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## 1. Phase 1 — Dataset & RAG
```powershell
python dataset.py                 | Tee-Object transcripts\t01_dataset.txt
python rag\index.py               | Tee-Object transcripts\t03_index.txt
python rag\calibrate.py           | Tee-Object transcripts\t04_calibration.txt
python rag\generate.py            | Tee-Object transcripts\t04_grounded.txt
python rag\eval_retrieval.py      | Tee-Object transcripts\t05_pr_at3.txt
pytest tests\test_dataset.py tests\test_rag.py -q
git add .; git commit -m "feat: part 1 dataset and RAG core"; git tag part1
```
After this: fill README §2–§6, DECISIONS D1–D15, EVALUATION §1–§3.

## 2. Phase 2 — Agent
```powershell
python agent\tools.py                    | Tee-Object transcripts\t06_status_tool.txt
python agent\graph.py demo_routes        | Tee-Object transcripts\t07_routes.txt
python agent\graph.py demo_schema        | Tee-Object transcripts\t09_schema.txt
python agent\graph.py demo_memory_multi  | Tee-Object transcripts\t08_memory_multi.txt
python agent\graph.py demo_memory_fresh  | Tee-Object transcripts\t08_memory_fresh.txt
python agent\graph.py demo_guard_pii       | Tee-Object transcripts\t10_guard_pii.txt
python agent\graph.py demo_guard_injection | Tee-Object transcripts\t10_guard_injection.txt
python agent\graph.py demo_guard_grounded  | Tee-Object transcripts\t10_guard_grounded.txt
pytest tests\test_agent.py tests\test_guardrails.py -q
git add .; git commit -m "feat: part 2 agent"; git tag part2
```
Delete `memory.json` before the fresh-conversation demo if needed: `Remove-Item memory.json`.

## 3. Phase 3 — API, logging, evaluation
Terminal 1:
```powershell
uvicorn api.main:app --port 8001
```
Terminal 2:
```powershell
curl.exe -X POST http://127.0.0.1:8001/ask -H "Content-Type: application/json" -d "{\"query\":\"What is the notice period policy?\"}"
curl.exe -X POST http://127.0.0.1:8001/ask -H "Content-Type: application/json" -d "{\"query\":\"Status of APP-0007?\"}"
curl.exe -X POST http://127.0.0.1:8001/ask -H "Content-Type: application/json" -d "{\"query\":\"Call me on +91 98765 43210 about referral bonus\"}"
curl.exe -X POST http://127.0.0.1:8001/add-document -H "Content-Type: application/json" -d "{\"doc_id\":\"relocation_policy\",\"title\":\"Relocation\",\"text\":\"Relocation support is offered. Amount depends on grade.\"}"
curl.exe http://127.0.0.1:8001/health
Get-Content logs\requests.jsonl
Select-String -Path logs\requests.jsonl -Pattern "98765 43210"       # must print nothing
python eval\triad.py | Tee-Object transcripts\t13_triad.md
pytest tests\test_api.py -q
git add .; git commit -m "feat: part 3 API logging eval"; git tag part3
```

## 4. Phase 4 — MCP & resilience
```powershell
python mcp_server\server.py                 # terminal 1 (leave running)
python mcp_server\client.py | Tee-Object transcripts\t14_mcp_client.txt   # terminal 2
Remove-Item checkpoints.sqlite -ErrorAction SilentlyContinue
python resilience\checkpoint_demo.py | Tee-Object transcripts\t15_checkpoint.txt
python resilience\timeout_retry_demo.py retry          | Tee-Object transcripts\t16_retry.txt
python resilience\timeout_retry_demo.py node_timeout   | Tee-Object transcripts\t16_node_timeout.txt
python resilience\timeout_retry_demo.py global_timeout | Tee-Object transcripts\t16_global_timeout.txt
pytest tests\test_resilience.py -q
git add .; git commit -m "feat: part 4 MCP and resilience"; git tag part4
```
Copy the server console output into `transcripts\t14_mcp_server.txt`.

## 5. Optional — Frontend & deploy
```powershell
npm create vite@latest frontend -- --template react
cd frontend; npm install; npm install tailwindcss @tailwindcss/vite; npm run dev
```
Deploy steps: [DEPLOYMENT.md](DEPLOYMENT.md).

## 6. Final verification & submit
```powershell
pytest -q
cd ..
git clone "d:\Ai notes\Recruitment" Recruitment_clean_test
cd Recruitment_clean_test
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:MOCK_LLM = "1"
python dataset.py
cd "d:\Ai notes\Recruitment"
git branch -M main
git remote add origin https://github.com/<user>/<repo>.git
git push -u origin main
git push --tags
```

## Port map
| Service | Port |
|---|---|
| FastAPI | 8001 |
| MCP (`/mcp`) | 8000 |
| Vite | 5173 |

## Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `Activate.ps1` blocked | Execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `ModuleNotFoundError` | venv inactive | Activate venv |
| Port in use | Old process | `netstat -ano \| findstr :8000` then `taskkill /PID <id> /F` |
| Stale Chroma results | Old index | `Remove-Item -Recurse chroma_db`; `python rag\index.py` |
| Resume re-runs everything | New thread ID or DB deleted | Reuse same `thread_id`; keep `checkpoints.sqlite` |
| MCP 404 / connection error | Wrong path | URL must end with `/mcp`; server running |
| `pip install fast-mcp` fails | Wrong package | Use `fastmcp` |
| `sqlite` checkpointer import error | Missing package | `pip install langgraph-checkpoint-sqlite` |
| Model download fails | No internet at first run | Connect once; model then caches |
| Flagged % out of band | Unlucky draw | Change SEED/weights, regenerate (never edit records) |
| Unicode errors in Tee-Object | Console encoding | `$env:PYTHONIOENCODING="utf-8"` |
| `MOCK_LLM` not set | New terminal | `$env:MOCK_LLM = "1"` |
