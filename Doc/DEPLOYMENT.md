# Deployment (optional)

Grading runs locally under `MOCK_LLM=1`. Deployment is a showcase extra — do it after Part 4.

## 1. Strategy
| Piece | Host | Why |
|---|---|---|
| React + Tailwind v4 UI | **Vercel** | Static, free, fast |
| FastAPI + LangGraph + Chroma + embeddings | **Hugging Face Spaces (Docker)** | ~16 GB RAM free; fits torch + Chroma |
| Fallback backend | Render | Needs CPU-only torch; 512 MB RAM is tight |
| MCP server | local only | Demo-only |

Why not Vercel for Python: the sentence-transformers/torch stack is far larger than serverless
function limits, and there is no persistent disk (only `/tmp`), so `memory.json`,
`checkpoints.sqlite`, logs and Chroma would not persist. (Verify current platform limits before deciding.)

## 2. Environment variables
| Where | Name | Example | Purpose |
|---|---|---|---|
| Backend | `MOCK_LLM` | `1` | Keyless mode |
| Backend | `ALLOWED_ORIGINS` | `https://my-app.vercel.app,http://localhost:5173` | CORS |
| Backend | `PORT` | `7860` | Space port |
| Frontend | `VITE_API_URL` | `https://<user>-<space>.hf.space` | API base |

## 3. Backend prep (code changes)
- [ ] `api/main.py`: add `CORSMiddleware` using `ALLOWED_ORIGINS`
- [ ] Paths in `config.py` configurable via env (e.g. `DATA_DIR`) with `/tmp` fallback if the disk is read-only
- [ ] `requirements.txt` pinned; prefer CPU torch (`--extra-index-url https://download.pytorch.org/whl/cpu`)
- [ ] Index built at image build time (so no heavy work at startup)

## 4. Dockerfile (repo root)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV MOCK_LLM=1
RUN python dataset.py && python rag/index.py
EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
```
`.dockerignore`: `.venv`, `chroma_db`, `checkpoints.sqlite`, `memory.json`, `node_modules`, `frontend`, `logs`, `__pycache__`.

## 5. Deploy backend — Hugging Face Spaces
1. huggingface.co → New Space → SDK **Docker** → CPU basic (free).
2. Space README header must include `sdk: docker` and `app_port: 7860`.
3. Push:
```powershell
git remote add space https://huggingface.co/spaces/<user>/<space>
git push space main
```
4. Wait for the build, then:
```powershell
curl.exe https://<user>-<space>.hf.space/health
```
5. Space storage is ephemeral: memory/log files reset on restart (acceptable for demo).

### Alternative — Render
New → Web Service → Docker → free plan; set env vars; start command from Dockerfile.
Expect cold starts (~15 min idle sleep) and tight memory.

## 6. Deploy frontend — Vercel
```powershell
cd frontend
npm install
npm run build                  # local sanity check
npm install -g vercel
vercel login
vercel                         # preview
vercel --prod
```
Project settings: Framework **Vite** · Root `frontend` · Build `npm run build` · Output `dist`.
Environment variable: `VITE_API_URL` (Production + Preview) → then redeploy:
```powershell
vercel env add VITE_API_URL production
vercel --prod
```
Optional `frontend/vercel.json` for SPA routing:
```json
{ "rewrites": [{ "source": "/(.*)", "destination": "/" }] }
```

## 7. Smoke-test checklist
- [ ] `/health` returns `ok` on the Space URL
- [ ] `/docs` loads
- [ ] CORS: browser call from the Vercel domain succeeds (no CORS error in console)
- [ ] Policy query returns a grounded answer with sources
- [ ] `Status of APP-0007?` returns the status card
- [ ] Phone number is masked in the response flags
- [ ] Cold-start behaviour acceptable (first call may be slow)

## 8. Rollback & troubleshooting
| Problem | Fix |
|---|---|
| CORS error | Add the exact Vercel URL to `ALLOWED_ORIGINS`; redeploy Space |
| Frontend calls localhost | `VITE_API_URL` missing at build time; set and redeploy |
| Space build OOM/timeouts | Use CPU torch; pin versions; shrink image |
| Mixed content error | Use `https://` API URL |
| 404 on refresh | Add `vercel.json` rewrite |
| Rollback | Vercel dashboard → Deployments → Promote previous; Space → revert git commit |

## 9. Security notes
No secrets in the repo; only fabricated data; real LLM keys (if ever used) go in platform secrets, never in git.
