# 🤝 Personalized Network Assistant

An AI-powered networking assistant that extracts themes from event descriptions, generates tailored conversation starters, and verifies facts — all in a clean web UI.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Theme Extraction | DistilBERT (zero-shot classification) |
| Starter Generation | GPT-2 Small |
| Fact Verification | Wikipedia REST API |
| Frontend | Streamlit |
| Testing | pytest + httpx |

---

## Project Structure

```
personalized-network-assistant/
├── app/
│   ├── main.py                  # FastAPI entry point (hub)
│   ├── models.py                # Pydantic data schemas
│   ├── routers/
│   │   └── conversation.py      # API routes (spokes)
│   └── services/
│       ├── event_analyzer.py    # DistilBERT theme extraction
│       ├── topic_generator.py   # GPT-2 conversation starters
│       ├── fact_checker.py      # Wikipedia fact-check
│       ├── history_logger.py    # Conversation history (JSON)
│       └── feedback_logger.py   # Feedback log (JSON)
├── frontend/
│   └── streamlit_app.py         # Streamlit UI
├── tests/
│   ├── test_event_analyzer.py
│   ├── test_topic_generator.py
│   ├── test_fact_checker.py
│   └── test_routes.py
├── data/                        # Auto-created JSON storage
├── requirements.txt
└── README.md
```

---

## Setup

### Prerequisites
- Python 3.11+
- Git

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd personalized-network-assistant
```

### 2. Create and activate a virtual environment
```bash
# Create
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify installation
```bash
python -c "import fastapi, streamlit, transformers, torch; print('All packages OK')"
```

---

## Running the Application

### Start the FastAPI backend
```bash
uvicorn app.main:app --reload
```
- API: http://localhost:8000
- Interactive Swagger docs: http://127.0.0.1:8000/docs
- `--reload` enables hot-reloading on file save

### Start the Streamlit frontend (new terminal)
```bash
streamlit run frontend/streamlit_app.py
```
- UI: http://localhost:8501

---

## Running Tests
```bash
pytest tests/ -v
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/conversation/analyze-event` | Extract themes from event description |
| POST | `/conversation/fact-check` | Fetch Wikipedia summary for a query |
| POST | `/conversation/generate-conversation` | Full pipeline: themes → starters → auto-log |
| POST | `/conversation/feedback` | Submit like/dislike on a starter |
| GET | `/conversation/history` | Retrieve all conversation sessions |

---

## Architecture

### Hub-and-Spoke Routing

`main.py` acts as the **central hub** assembling modular router components. New endpoints (e.g., `/users`, `/recommendations`) are added as new router files without touching existing code.

### Request Lifecycle

```
Streamlit UI
    │  POST /conversation/generate-conversation
    ▼
FastAPI (main.py)
    │  routes to handler
    ▼
Router (conversation.py)
    │  1. extract_event_themes()  ──► DistilBERT
    │  2. generate_topics()       ──► GPT-2
    │  3. log_conversation()      ──► JSON file
    ▼
ConversationResponse → Streamlit UI
```

### Service Layer Principles

| Principle | How it's applied |
|---|---|
| **Single Responsibility** | Each service file does exactly one job |
| **Dependency Injection** | Services imported at router top-level; mockable in tests |
| **Stateless Functions** | All AI functions are pure; loggers are the only intentional exception |

### Key FastAPI Features Used

- **Automatic OpenAPI docs** — Swagger UI at `/docs` generated from Pydantic models, zero extra configuration
- **Type-safe validation** — `422 Unprocessable Entity` returned automatically for bad requests
- **Response model enforcement** — `response_model=` ensures only intended fields are returned to the client

---

## Key Design Decisions

- **Models load once at startup** — not per-request — for low-latency responses
- **`set_seed(42)`** on GPT-2 — reproducible outputs for the same input (valuable for testing)
- **Auto-logging** on `/generate-conversation` — frontend does not need to manage history separately
- **Graceful error handling** on Wikipedia API — network failures return user-friendly messages, never crash the app
- **`pathlib.Path`** throughout — cross-platform file handling (Windows / macOS / Linux)
- **`sys.path.insert`** in Streamlit app — allows importing `app.services` from the `frontend/` subdirectory

---

## Future Enhancements

| Enhancement | Approach |
|---|---|
| Multilingual support | Swap DistilBERT for `xlm-roberta` |
| Recommendation engine | Collaborative filtering on `feedback_log.json` data |
| Voice input | Integrate OpenAI Whisper |
| Cloud deployment | Docker → Cloud Run (API) + Streamlit Cloud (UI) |
| Authentication | Add `/users` router with JWT-based auth |
| Database backend | Replace JSON logs with SQLite/PostgreSQL via SQLAlchemy |
