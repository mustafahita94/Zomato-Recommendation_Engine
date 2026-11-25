# AI-Powered Restaurant Recommendation System

Personalized restaurant recommendations using the Zomato Hugging Face dataset, deterministic filtering, and an LLM for ranking with explanations.

**Stack:** FastAPI (Python) + Next.js (Discover UI)

## Prerequisites

- Python 3.11+
- Node.js 20+
- A [Groq](https://console.groq.com/keys) API key

## Setup

```bash
# Create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux
# Edit .env and set LLM_API_KEY (Groq). Defaults:
#   LLM_MODEL=openai/gpt-oss-20b
#   LLM_BASE_URL=https://api.groq.com/openai/v1

# Install Next.js frontend
cd web
npm install
copy .env.local.example .env.local   # Windows
# cp .env.local.example .env.local   # macOS / Linux
cd ..
```

## Data ingestion (Phase 1)

```bash
# Download HF dataset, clean fields, write data/processed/restaurants.*
python -m src.ingestion.load_dataset

# Row counts + distributions + exit-criteria checks
python scripts/sanity_check_ingestion.py
```

Processed columns: `id`, `name`, `location` (neighborhood), `city`, `cuisines`, `cost_for_two`, `budget_band` (`low` ≤300 / `medium` ≤600 / `high`), `rating`, `votes`, plus a few extras (`rest_type`, etc.).

## Filtering (Phase 2)

```bash
# Preference validation + candidate filter edge-case checks
python scripts/test_filter.py
```

Pipeline: location → cuisine → budget band → min rating → sort by rating → top N (default 20). Free-text `additional_preferences` is validated/truncated only — not used as a hard filter.

## LLM recommendations (Phase 3)

Uses **Groq** (`openai/gpt-oss-20b`) to rank the filtered shortlist and write explanations. Invented restaurant names are dropped; rating/cost/cuisine are always taken from the processed store. If the API key is missing or the call fails, the engine falls back to top-N by rating with generic explanations.

```bash
# Prompt builder + grounding + fallback (+ live Groq if LLM_API_KEY is set)
python scripts/test_recommender.py
```

## Run the app (Phase 4)

Local demo uses **two processes**:

```bash
# Terminal 1 — API (port 8000)
uvicorn src.api.main:app --reload --port 8000

# Terminal 2 — Next.js UI (port 3000)
cd web
npm run dev
```

Open **http://localhost:3000**

API docs: http://localhost:8000/docs

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness |
| `GET /meta` | Catalog size, locations, cuisines, LLM status |
| `POST /recommend` | Ranked recommendations + explanations |

End-to-end flow: preference form → validation → candidate filter → Groq ranking/explanations → results list (name, cuisine, rating, cost, explanation). Empty filters show relax-filter guidance; missing/failed LLM falls back to rating-based picks.

## Project layout

```text
Zomato/
├── Docs/                 # Problem statement, architecture, plan
├── data/
│   ├── raw/              # Optional local HF cache
│   └── processed/        # Cleaned restaurant catalog
├── src/
│   ├── ingestion/        # Dataset load + preprocess
│   ├── models/           # Preference / restaurant schemas
│   ├── services/         # Filter, prompt builder, recommender
│   ├── api/              # FastAPI routes
│   └── config.py         # Env-based settings
├── web/                  # Next.js Discover UI (Stitch dark theme)
├── prompts/              # LLM prompt templates
├── .env.example
└── requirements.txt
```

## Docs

- [Problem statement](Docs/problemStatement.md)
- [Architecture](Docs/architecture.md)
- [Implementation plan](Docs/implementation-plan.md)
- [Deployment plan](Docs/deployment-plan.md) (Vercel + Railway)
