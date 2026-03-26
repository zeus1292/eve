# Eve — AI Eval Framework Builder

Generate a tailored evaluation framework for your AI application in minutes.

## Stack

| Layer | Tech |
|---|---|
| Frontend | Next.js 14 (App Router) + Tailwind + shadcn/ui |
| Backend | Python FastAPI + LangChain + Anthropic Claude |
| Deployment | Vercel (frontend) + Railway (backend) |

## Local Development

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your ANTHROPIC_API_KEY
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`. Health check: `GET /health`.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Frontend runs at `http://localhost:3000`.

## Deployment

### Backend → Railway

1. Push to GitHub
2. Create a new Railway project → Deploy from GitHub → select `/backend`
3. Set environment variables: `ANTHROPIC_API_KEY`, `CORS_ORIGINS` (your Vercel URL)
4. Railway auto-detects the `Dockerfile`

### Frontend → Vercel

1. Import the repo in Vercel → set root directory to `frontend`
2. Add environment variable: `NEXT_PUBLIC_API_URL` = your Railway backend URL
3. Deploy

## Architecture

```
User
 │
 ▼
Next.js (Vercel)
 │  Three input modes: Text | File | Git
 │
 ▼
FastAPI (Railway)
 ├── /ingest/text|file|git  →  LangChain extraction chain  →  ProductContext
 ├── /questionnaire         →  SteerLM-inspired guided flow
 └── /eval-plan             →  LCEL pipeline (5 chains, streaming SSE)
                                └─ claude-sonnet-4-6
                                   ├── Eval Discovery
                                   ├── Deterministic Specs + SLAs
                                   ├── Non-Deterministic Rubrics
                                   ├── Phase Assignment
                                   └── Markdown Renderer
```

## Output

A phased markdown eval framework covering:

**Phase 1 (all products):**
- Deterministic evals: schema validation, latency baselines, accuracy assertions
- Non-deterministic evals: LLM-judge rubrics with 5-point scales and test prompts

**Phase 2 (production products only):**
- Performance SLAs, safety/compliance evals, bias checks, edge cases
