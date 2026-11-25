# Deployment Plan — Vercel (Frontend) + Railway (Backend)

Deploy the Discover restaurant recommendation app using two free hosts:

| Layer | Service | What runs |
|-------|---------|-----------|
| Frontend | [Vercel](https://vercel.com) (Hobby) | Next.js app in `web/` |
| Backend | [Railway](https://railway.app) | FastAPI (`uvicorn src.api.main:app`) + `data/processed/` |

External dependency (already free-tier friendly): [Groq](https://console.groq.com/keys) for LLM ranking.

```text
Browser → Vercel (Next.js) → NEXT_PUBLIC_API_URL → Railway (FastAPI) → Groq
                                              ↘ data/processed/restaurants.*
```

---

## 0. Prerequisites

- GitHub (or GitLab/Bitbucket) repo with this project pushed
- Accounts: Vercel, Railway, Groq
- Local catalog already built:

```bash
python -m src.ingestion.load_dataset
```

Confirm these exist before deploy:

- `data/processed/restaurants.parquet` (preferred)
- `data/processed/restaurants.csv` (fallback)

Processed data is **not** gitignored — commit it so Railway has the catalog at boot (avoids HF download / ingestion at deploy time).

---

## 1. Code changes required before deploy

Status of repo-ready items:

| Item | Status |
|------|--------|
| §1.1 CORS via `CORS_ORIGINS` / `CORS_ORIGIN_REGEX` | Done (`src/config.py`, `src/api/main.py`, `.env.example`) |
| §1.2 Bind to Railway `PORT` | Done (`railway.toml` / `Procfile` start command) |
| §1.3 Frontend `NEXT_PUBLIC_API_URL` | Ready (`web/src/lib/api.ts` — set value in Vercel) |
| §1.4 Hardening files | Done (`railway.toml`, `nixpacks.toml`, `.python-version`, `Procfile`) |

### 1.1 Allow Vercel origin on FastAPI CORS

Implemented: comma-separated `CORS_ORIGINS` merges with localhost defaults; optional `CORS_ORIGIN_REGEX` for Vercel previews.

After the first Vercel deploy, set on Railway:

```text
CORS_ORIGINS=https://your-app.vercel.app
# optional for preview deployments:
CORS_ORIGIN_REGEX=https://.*\.vercel\.app
```

### 1.2 Bind uvicorn to Railway’s `PORT`

Railway injects `PORT`. Start command is pinned in `railway.toml` / `Procfile`:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

### 1.3 Frontend API base URL

`web/src/lib/api.ts` already reads:

```text
NEXT_PUBLIC_API_URL  →  default http://localhost:8000
```

On Vercel, set this to the Railway public HTTPS URL (no trailing slash).  
`NEXT_PUBLIC_*` is baked in at **build** time — set the var **before** (or trigger a redeploy after) the Railway URL is known.

### 1.4 Deploy hardening (in repo)

| File | Purpose |
|------|---------|
| `railway.toml` | Start command + `/health` check |
| `nixpacks.toml` | Force **Python** provider (ignore `web/package.json`) |
| `.python-version` | Python 3.11 |
| `Procfile` | Same start command (fallback) |

Do **not** commit `.env` / `web/.env.local` — secrets only in host dashboards.

---

## 2. Environment variables

### 2.1 Railway (backend)

| Variable | Required | Example / notes |
|----------|----------|-----------------|
| `LLM_API_KEY` | Yes (for live LLM) | Groq key from console |
| `LLM_MODEL` | No | `openai/gpt-oss-20b` (see `.env.example`) |
| `LLM_BASE_URL` | No | `https://api.groq.com/openai/v1` |
| `LLM_TEMPERATURE` | No | `0.3` |
| `LLM_MAX_RECOMMENDATIONS` | No | `5` |
| `CANDIDATE_LIMIT` | No | `20` |
| `CORS_ORIGINS` | Yes (after §1.1) | `http://localhost:3000,https://<vercel-app>.vercel.app` |
| `PORT` | Auto | Set by Railway — do not hardcode |

If `LLM_API_KEY` is missing, the API still runs and falls back to rating-based recommendations (existing behavior).

### 2.2 Vercel (frontend)

| Variable | Required | Example |
|----------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Yes | `https://<railway-service>.up.railway.app` |

Scope: Production (and Preview if preview apps should hit the same API).

---

## 3. Deploy backend on Railway

### 3.1 Create service

1. Railway → **New Project** → **Deploy from GitHub repo**
2. Select this repository
3. Root directory: **repository root** (not `web/`)
4. Railway/Nixpacks should detect Python via `requirements.txt`

### 3.2 Build & start

**Install / build**

```bash
pip install -r requirements.txt
```

No separate build step required if `data/processed/` is in the repo.

**Start command** (set in Railway Settings → Deploy):

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

Windows note: `$PORT` is for Railway’s Linux container; local Windows still uses `--port 8000`.

### 3.3 Networking

1. Settings → **Networking** → **Generate Domain**
2. Copy public URL, e.g. `https://zomato-api-production.up.railway.app`
3. Verify:

```bash
curl https://<railway-url>/health
# {"status":"ok"}

curl https://<railway-url>/meta
# catalog_size, locations, cuisines, groq_connected, ...
```

If `/meta` returns **503**, the processed catalog is missing from the deploy image — commit/push `data/processed/restaurants.*` and redeploy.

### 3.4 Config files (already in repo)

- `railway.toml` — start command + health check
- `nixpacks.toml` — `providers = ["python"]` so Railway does not treat this as a Node app because of `web/`
- `.python-version` — `3.11`
- `Procfile` — same uvicorn start command

---

## 4. Deploy frontend on Vercel

### 4.1 Create project

1. Vercel → **Add New** → **Project** → import the same Git repo
2. Configure:

| Setting | Value |
|---------|--------|
| Framework Preset | Next.js |
| Root Directory | `web` |
| Build Command | `npm run build` (default) |
| Output | Next.js default (no change) |
| Install Command | `npm install` (default) |

### 4.2 Env vars

Add `NEXT_PUBLIC_API_URL` = Railway HTTPS URL (no trailing slash).

### 4.3 Deploy

1. Deploy → wait for build
2. Copy production URL, e.g. `https://discover-bangalore.vercel.app`
3. Update Railway `CORS_ORIGINS` to include that URL
4. Redeploy Railway (or restart) so CORS picks up the new origin
5. If you changed CORS code after the first Vercel deploy, push and let both hosts redeploy

### 4.4 Verify UI

1. Open the Vercel URL
2. Location/cuisine dropdowns load (from `GET /meta`)
3. Submit preferences → results from `POST /recommend`
4. Browser DevTools → Network: requests go to Railway, status 200; no CORS errors

---

## 5. Ordered rollout checklist

Follow this order to avoid chicken-and-egg URL issues:

1. [ ] Commit processed catalog (`data/processed/restaurants.parquet` / `.csv`) + deploy config files
2. [x] Implement `CORS_ORIGINS` / Railway start config (done in repo)
3. [ ] Push to GitHub
4. [ ] Deploy **Railway** → set Groq + LLM env vars → generate domain
5. [ ] Smoke-test `/health` and `/meta` on Railway
6. [ ] Deploy **Vercel** with Root Directory `web` and `NEXT_PUBLIC_API_URL`
7. [ ] Add Vercel URL to Railway `CORS_ORIGINS` → restart/redeploy backend
8. [ ] End-to-end test on the Vercel URL
9. [ ] (Optional) Custom domains on both hosts; update CORS + `NEXT_PUBLIC_API_URL` again

---

## 6. Post-deploy verification

| Check | How | Pass criteria |
|-------|-----|----------------|
| API liveness | `GET /health` | `{"status":"ok"}` |
| Catalog loaded | `GET /meta` | `catalog_size` > 0, locations/cuisines non-empty |
| Groq wired | `GET /meta` | `groq_connected: true` when key set |
| CORS | Browser from Vercel origin | No blocked cross-origin errors |
| Recommend happy path | `POST /recommend` with valid prefs | Ranked list + explanations |
| Empty filters | Over-narrow prefs | Relax-filter messaging (existing UX) |
| LLM fallback | Temporarily wrong/missing key | Still returns rating-based picks |

---

## 7. Free-tier limits & ops notes

| Topic | Reality |
|-------|---------|
| Railway free/trial credits | Usage-based; monitor dashboard so the API doesn’t stop when credits run out |
| Vercel Hobby | Fine for a demo/portfolio; commercial limits apply per Vercel’s current plan |
| Cold starts | First request after idle may be slower on free compute |
| Groq rate limits | Burst traffic may fail LLM calls → app falls back to rating sort |
| Data size | ~1.5MB CSV / ~0.5MB Parquet — fine to ship in the repo for this project |
| Secrets | Rotate Groq key if ever committed; only set in Railway Variables |
| Redeploys | Push to main (or connected branch) triggers both hosts if Git integration is enabled |

---

## 8. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| UI loads, dropdowns empty / network error | Wrong `NEXT_PUBLIC_API_URL` or backend down | Fix Vercel env; confirm Railway domain; redeploy frontend |
| CORS error in browser | Vercel origin not in `allow_origins` | Add exact Vercel URL to `CORS_ORIGINS`; redeploy API |
| `/meta` or `/recommend` → 503 | Missing `data/processed/` on Railway | Commit catalog files; ensure deploy root is repo root |
| `groq_connected: false` | Missing/placeholder `LLM_API_KEY` | Set real key on Railway |
| Railway boot crash | Bad start command / wrong root | Use `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT` from repo root |
| Vercel build fails | Wrong root directory | Set Root Directory to `web` |
| Works on localhost only | Env still pointing at `http://localhost:8000` | Set production `NEXT_PUBLIC_API_URL` and rebuild |

---

## 9. Out of scope for this plan

- Docker image (Railway Nixpacks is enough)
- Separate staging environment
- CI pipeline beyond Git-connected auto-deploy
- Database (catalog is file-based)
- Merging API into Next.js Route Handlers (would collapse to Vercel-only; not chosen here)

---

## 10. Quick reference

```bash
# Local catalog (once, then commit)
python -m src.ingestion.load_dataset

# Local API (unchanged)
uvicorn src.api.main:app --reload --port 8000

# Local UI
cd web && npm run dev

# Production start (Railway)
uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

| Host | Root | Critical env |
|------|------|----------------|
| Railway | `.` | `LLM_*`, `CORS_ORIGINS` |
| Vercel | `web` | `NEXT_PUBLIC_API_URL` |
