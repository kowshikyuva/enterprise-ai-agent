# Enterprise AI Research Agent

An AI application that runs **structured enterprise research at scale** — give it a topic, and it decomposes it into sub-questions, searches and scrapes real sources, extracts and classifies findings, detects contradictions between sources, and produces conclusions that trace back to exact evidence.

> Built for MODUS Transformation AI — Assignment 9.

**This is deliberately not "ChatGPT with web search."** A single search-and-summarize call has no memory, no traceability, and no way to prove where an answer came from. This project maintains a real, queryable knowledge base and a multi-stage pipeline instead of one undifferentiated prompt.

---

## The pipeline

```
Topic
  │
  ▼
1. Define Research Questions   → decompose the topic into 2-3 focused sub-questions
  │
  ▼  (per question)
2. Search Sources               → web search via DuckDuckGo
3. Collect Information          → scrape each result page
4. Store Sources                → persist to PostgreSQL + embed into ChromaDB
5. Extract Findings             → pull discrete, checkable claims out of each source
6. Compare Evidence             → cross-check findings against each other
7. Classify Findings            → tag as benefit / challenge / trend / risk / statistic
8. Detect Contradictions        → flag genuine disagreements between sources
9. Generate Conclusions         → synthesize an answer, naming which findings it used
  │
  ▼
10. Maintain Traceability       → every conclusion links back to its findings and sources
```

Every stage writes structured rows to Postgres — nothing is just "displayed and forgotten." A `Finding` has a `source_id` and `question_id`. A `Contradiction` points at two specific `Finding` rows with an explanation. A `Conclusion` is linked (many-to-many) to the exact findings it relied on.

---

## Architecture

| Layer | Tech | Role |
|---|---|---|
| Frontend | React + Vite | Thin pipeline visualizer — no logic lives here |
| Backend | FastAPI | Pipeline orchestrator: rate-limit guard, timeouts, stage-by-stage logging |
| Relational DB | PostgreSQL | The structured knowledge base — questions, sources, findings, contradictions, conclusions |
| Vector store | ChromaDB | Embeddings for sources, so they're reusable across future research runs |
| LLM | Gemini (`gemini-3.5-flash-lite`) | Called at 3 distinct points — question generation, finding extraction, contradiction/conclusion synthesis — never asked to do everything in one prompt |

```
React (5173) → FastAPI (8000) → PostgreSQL
                             ↘  ChromaDB
                             ↘  Gemini API
```

---

## Project structure

```
backend/
  app/
    api/            # FastAPI routers: research, chat, history, stats
    models/          # SQLAlchemy models: ResearchProject, ResearchQuestion,
                      #   Source, Finding, Contradiction, Conclusion, ResearchResult
    schemas/          # Pydantic response schemas
    services/
      research_service.py      # the pipeline orchestrator
      question_service.py      # Stage 1
      search_service.py        # Stage 2
      scraper_service.py       # Stage 3
      source_service.py        # Stage 4 (Postgres)
      chroma_service.py        # Stage 4 (vector store)
      extraction_service.py    # Stages 5 & 7
      comparison_service.py    # Stages 6 & 8
      conclusion_service.py    # Stage 9
      gemini_service.py        # shared LLM client: throttling, retry, timeouts
    core/config.py    # env var loading
    database/         # SQLAlchemy engine/session
  requirements.txt
frontend/
  src/
    components/       # SearchBox, SummaryCard, SourceCard, StatsCard
    api/api.js         # backend base URL
  package.json
```

---

## Setup

### Prerequisites
- Python 3.10+ (a `runtime.txt` pins the deployed version)
- Node.js 18+
- A PostgreSQL database (local or hosted — Render, Supabase, Neon, etc.)
- A Gemini API key ([aistudio.google.com](https://aistudio.google.com))

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env`:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
GOOGLE_API_KEY=your_gemini_api_key
CHROMA_DB=./chroma_db
```

Tables are created automatically on startup (`Base.metadata.create_all`) — no separate migration step needed for a fresh database.

```bash
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to confirm it's running.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`.

---

## API

| Endpoint | Method | Description |
|---|---|---|
| `/research` | `POST` | Runs the full pipeline for a new topic. Body: `{"topic": "..."}` |
| `/research/{project_id}` | `GET` | Re-fetches a past run from the stored knowledge base without re-running the pipeline |
| `/projects` | `GET` | Lists past research runs |
| `/history` | `GET` | Lists every source ever collected (the reusable knowledge base) |
| `/chat` | `POST` | Simple chat endpoint over stored context |
| `/stats` | `GET` | Basic usage stats |

---

## Design notes & trade-offs

- **Sources per question / questions per topic are intentionally capped** (currently 2 questions × 2 sources) to keep each run's Gemini call count manageable on a rate-limited free-tier key. Raise `SOURCES_PER_QUESTION` and the `max_questions` argument in `research_service.py` for more depth once you have paid API access.
- **Graceful degradation, not fabrication.** If a search doesn't surface a source specific enough to extract a real finding, the pipeline reports `"No sufficiently relevant findings were gathered"` rather than guessing. This is deliberate — an enterprise research tool that invents answers when evidence is thin is worse than one that says so.
- **Every external call has a hard timeout** (Gemini, web search, ChromaDB embedding) and is wrapped in a rate-limit-aware retry. Without this, a single stalled network call would hang the whole request indefinitely with no error.
- **ChromaDB storage is local-disk** (`./chroma_db`). This is fine for local development; on most hosted platforms' free tiers the filesystem is ephemeral and resets on redeploy, so the vector store won't persist across restarts in production without an external Chroma instance or persistent volume.
- **Synchronous by design.** This is FastAPI, not Django/Celery — a research run blocks the request until it finishes rather than running as a background job. Fine for a demo; a production version would move this to a background task with a polling or websocket status endpoint.

---

## Known limitations

- Free-tier Gemini keys are capped in both requests/minute and requests/day. The pipeline throttles and retries automatically, but a very low daily quota (some free projects report as little as 20 requests/day for certain models) can still exhaust itself within one or two full runs.
- With low `SOURCES_PER_QUESTION`, some questions may return zero findings if the web search doesn't surface a strong source on the first try — this is the graceful-degradation behavior above, not a bug.
