<![CDATA[# 🤝 Personalized Network Assistant

> **AI-powered conversation starter generator** that extracts themes from networking event descriptions, generates tailored icebreakers using GPT-2, and verifies facts via Wikipedia — all wrapped in a sleek dark-themed web interface.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Running the Application](#-running-the-application)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Data Storage](#-data-storage)
- [Design Decisions](#-design-decisions)
- [Future Enhancements](#-future-enhancements)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

Networking events can be daunting — knowing what to say is half the battle. The **Personalized Network Assistant** solves this by combining state-of-the-art NLP models with a user's professional profile to generate relevant, personalized conversation starters.

### How It Works

1. **You describe the event** — paste the event description or summary.
2. **AI extracts themes** — DistilBERT zero-shot classification identifies the top professional themes.
3. **AI generates starters** — GPT-2 creates tailored conversation openers based on themes + your interests.
4. **You verify facts** — Optional Wikipedia lookup to fact-check any topic mentioned.
5. **You give feedback** — Like/dislike starters to build a dataset for future improvements.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🏷️ **Theme Extraction** | DistilBERT zero-shot classification identifies top-3 professional themes from event descriptions |
| 💬 **Conversation Starters** | GPT-2 generates 3 personalized icebreakers based on event themes + user interests |
| 🔍 **Fact Verification** | Real-time Wikipedia lookups to verify topics, technologies, or concepts |
| 👍👎 **Feedback System** | Like/dislike individual starters — data logged for future recommendation improvements |
| 📖 **Session History** | All generated conversations are auto-saved and browsable |
| 🎨 **Premium Dark UI** | Glassmorphism design with gradient accents, smooth animations, and responsive layout |
| 📊 **Session Stats** | Live counters for starters generated and feedback given in the sidebar |
| 📄 **Interactive API Docs** | Auto-generated Swagger UI at `/docs` with full request/response schemas |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend API** | [FastAPI](https://fastapi.tiangolo.com) + [Uvicorn](https://www.uvicorn.org) | High-performance async REST API |
| **Theme Extraction** | [DistilBERT](https://huggingface.co/typeform/distilbert-base-uncased-mnli) (zero-shot) | Classify event descriptions into professional themes |
| **Text Generation** | [GPT-2 Small](https://huggingface.co/gpt2) | Generate natural conversation starters |
| **Fact Checking** | [Wikipedia REST API](https://en.wikipedia.org/api/rest_v1/) | Real-time fact verification |
| **Frontend** | [Streamlit](https://streamlit.io) | Interactive web dashboard |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev) | Request/response schema validation |
| **Testing** | [pytest](https://pytest.org) + [httpx](https://www.python-httpx.org) | Unit & integration tests |
| **Data Storage** | JSON files | Lightweight persistence for history & feedback |

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Streamlit)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐   │
│  │ Generate  │  │  Fact    │  │ History  │  │   Feedback    │   │
│  │   Tab     │  │  Check   │  │   Tab    │  │    Log Tab    │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬────────┘   │
│       │              │             │               │            │
└───────┼──────────────┼─────────────┼───────────────┼────────────┘
        │ HTTP/JSON    │             │               │
        ▼              ▼             ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI + Uvicorn)                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Router Layer                           │    │
│  │              /conversation/* endpoints                   │    │
│  └───────────┬──────────┬──────────┬──────────┬────────────┘    │
│              │          │          │          │                  │
│              ▼          ▼          ▼          ▼                  │
│  ┌──────────────┐ ┌──────────┐ ┌────────┐ ┌──────────────┐     │
│  │    Event     │ │  Topic   │ │  Fact  │ │   History &  │     │
│  │   Analyzer   │ │Generator │ │Checker │ │  Feedback    │     │
│  │ (DistilBERT) │ │ (GPT-2)  │ │ (Wiki) │ │  Loggers     │     │
│  └──────────────┘ └──────────┘ └────────┘ └──────┬───────┘     │
│                                                   │             │
└───────────────────────────────────────────────────┼─────────────┘
                                                    │
                                                    ▼
                                           ┌──────────────┐
                                           │  data/*.json  │
                                           │  (Persistent  │
                                           │   Storage)    │
                                           └──────────────┘
```

### Request Lifecycle (Full Pipeline)

```
User clicks "🚀 Generate" in Streamlit
    │
    │  POST /conversation/generate-conversation
    │  Body: { description, user_profile: { name, interests } }
    ▼
FastAPI Router (conversation.py)
    │
    ├─ Step 1: extract_event_themes(description)
    │           └─► DistilBERT zero-shot classifier
    │               └─► Returns top-3 themes (e.g., ["AI", "healthcare", "finance"])
    │
    ├─ Step 2: generate_topics(themes, interests)
    │           └─► GPT-2 text generation with prompt engineering
    │               └─► Returns 3 conversation starters
    │
    ├─ Step 3: log_conversation(session_data)  [auto, non-blocking]
    │           └─► Appends to data/conversation_history.json
    │
    └─► Response: { themes: [...], starters: [...] }
         │
         ▼
    Streamlit renders results with theme badges + starter cards + feedback buttons
```

### Hub-and-Spoke Routing Pattern

The application follows a **Hub-and-Spoke** architecture:

- **Hub** (`main.py`): Central FastAPI application that assembles all router modules
- **Spokes** (`routers/*.py`): Modular endpoint groups, each handling a distinct feature area

New features (e.g., `/users`, `/recommendations`) can be added as new router files without modifying existing code — following the **Open/Closed Principle**.

---

## 📁 Project Structure

```
personalized-network-assistant/
│
├── app/                            # Backend application package
│   ├── __init__.py
│   ├── main.py                     # FastAPI entry point (hub)
│   ├── models.py                   # Pydantic request/response schemas
│   │
│   ├── routers/                    # API route handlers (spokes)
│   │   ├── __init__.py
│   │   └── conversation.py         # All /conversation/* endpoints
│   │
│   └── services/                   # Business logic & AI integration
│       ├── __init__.py
│       ├── event_analyzer.py       # DistilBERT theme extraction
│       ├── topic_generator.py      # GPT-2 conversation starter generation
│       ├── fact_checker.py         # Wikipedia REST API fact verification
│       ├── history_logger.py       # Conversation session persistence
│       └── feedback_logger.py      # User feedback persistence
│
├── frontend/                       # Streamlit web interface
│   └── streamlit_app.py            # Full-featured UI (568 lines)
│
├── tests/                          # Automated test suite
│   ├── __init__.py
│   ├── test_event_analyzer.py      # Unit tests for theme extraction
│   ├── test_topic_generator.py     # Unit tests for text generation
│   ├── test_fact_checker.py        # Unit tests for Wikipedia lookup
│   └── test_routes.py             # Integration tests for all API routes
│
├── data/                           # Auto-created JSON storage
│   ├── conversation_history.json   # Saved conversation sessions
│   └── feedback_log.json           # Recorded like/dislike feedback
│
├── .streamlit/
│   └── config.toml                 # Streamlit theme & server configuration
│
├── .gitignore                      # Git ignore rules
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version | Check |
|------------|---------|-------|
| Python | 3.11+ | `python --version` |
| pip | Latest | `pip --version` |
| Git | Any | `git --version` |
| RAM | 4 GB+ | Required for AI model loading |
| Disk Space | ~1 GB | For model weights cache |

### Step 1: Clone the Repository

```bash
git clone https://github.com/GeethaPranathi/Personalized-Networking-Assistant.git
cd Personalized-Networking-Assistant
```

### Step 2: Create a Virtual Environment

```bash
# Create
python -m venv venv

# Activate — Windows (PowerShell)
venv\Scripts\activate

# Activate — Windows (cmd)
venv\Scripts\activate.bat

# Activate — macOS / Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import fastapi, streamlit, transformers, torch; print('✅ All packages installed successfully!')"
```

> **Note:** The first run will download AI model weights (~500 MB total for DistilBERT + GPT-2). These are cached locally for subsequent runs.

---

## ▶️ Running the Application

You need **two terminals** — one for the backend, one for the frontend.

### Terminal 1: Start the FastAPI Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

| URL | Description |
|-----|-------------|
| http://localhost:8000 | API root (health check) |
| http://localhost:8000/docs | Interactive Swagger documentation |
| http://localhost:8000/redoc | Alternative API docs (ReDoc) |

The `--reload` flag enables **hot-reloading** — the server restarts automatically on file changes.

### Terminal 2: Start the Streamlit Frontend

```bash
streamlit run frontend/streamlit_app.py
```

| URL | Description |
|-----|-------------|
| http://localhost:8501 | Web application UI |

### Quick Start (Both Together)

**Windows PowerShell:**
```powershell
Start-Process powershell -ArgumentList "cd $PWD; venv\Scripts\activate; uvicorn app.main:app --reload"
Start-Process powershell -ArgumentList "cd $PWD; venv\Scripts\activate; streamlit run frontend/streamlit_app.py"
```

**macOS / Linux:**
```bash
uvicorn app.main:app --reload &
streamlit run frontend/streamlit_app.py
```

---

## 📡 API Reference

Base URL: `http://localhost:8000`

### Health Check

```
GET /
```

**Response** `200 OK`:
```json
{
  "status": "ok",
  "message": "Personalized Network Assistant API is running.",
  "docs": "/docs"
}
```

---

### Extract Event Themes

```
POST /conversation/analyze-event
```

Extracts top-3 professional themes from an event description using DistilBERT zero-shot classification.

**Request Body:**
```json
{
  "description": "A tech summit bringing together founders and investors to discuss AI in healthcare and sustainable finance.",
  "user_profile": {
    "name": "Alex Johnson",
    "interests": ["machine learning", "fintech"]
  }
}
```

**Response** `200 OK`:
```json
{
  "themes": ["artificial intelligence", "healthcare", "finance"]
}
```

**Error Responses:**
| Status | Reason |
|--------|--------|
| `422` | Validation error (description < 10 chars, missing fields, empty interests) |
| `500` | Model inference failure |

---

### Generate Conversation Starters (Full Pipeline)

```
POST /conversation/generate-conversation
```

Orchestrates the **full AI pipeline**: theme extraction → starter generation → auto-logging.

**Request Body:**
```json
{
  "description": "A fintech summit exploring the intersection of AI and decentralised finance.",
  "user_profile": {
    "name": "Charlie Brown",
    "interests": ["fintech", "blockchain", "startup investing"]
  }
}
```

**Response** `200 OK`:
```json
{
  "themes": ["finance", "artificial intelligence", "blockchain"],
  "starters": [
    "What's your take on how AI is reshaping credit risk assessment in DeFi?",
    "Have you seen any promising startups combining NLP with financial compliance?",
    "How do you think traditional banks will respond to blockchain-based lending?"
  ]
}
```

> 💾 **Side effect:** The session is automatically saved to `data/conversation_history.json`.

---

### Fact-Check via Wikipedia

```
POST /conversation/fact-check
```

**Request Body:**
```json
{
  "query": "Large Language Models"
}
```

**Response** `200 OK`:
```json
{
  "query": "Large Language Models",
  "result": "A large language model (LLM) is a computational model notable for its ability to achieve general-purpose language generation and understanding..."
}
```

---

### Submit Feedback

```
POST /conversation/feedback
```

**Request Body:**
```json
{
  "suggestion": "What's your take on AI in diagnostics?",
  "action": "like"
}
```

**Response** `200 OK`:
```json
{
  "status": "ok",
  "message": "Feedback recorded."
}
```

> `action` must be exactly `"like"` or `"dislike"` — any other value returns `422`.

---

### Retrieve Conversation History

```
GET /conversation/history
```

**Response** `200 OK`:
```json
[
  {
    "user_name": "Alex Johnson",
    "interests": ["machine learning", "fintech"],
    "event_description": "A tech summit...",
    "themes": ["artificial intelligence", "healthcare", "finance"],
    "starters": ["...", "...", "..."],
    "timestamp": "2026-07-06T14:25:00.123456+00:00"
  }
]
```

---

### Retrieve Feedback Log

```
GET /conversation/feedback
```

**Response** `200 OK`:
```json
[
  {
    "suggestion": "What's your take on AI in diagnostics?",
    "action": "like",
    "timestamp": "2026-07-06T14:26:00.654321+00:00"
  }
]
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test Files

```bash
# Unit tests
pytest tests/test_event_analyzer.py -v    # Theme extraction
pytest tests/test_topic_generator.py -v   # Text generation
pytest tests/test_fact_checker.py -v      # Wikipedia lookup

# Integration tests
pytest tests/test_routes.py -v            # All API endpoints
```

### Test Coverage

```bash
pytest tests/ -v --cov=app --cov-report=html
# Open htmlcov/index.html in your browser
```

### Test Architecture

| Test File | Type | What's Tested |
|-----------|------|---------------|
| `test_event_analyzer.py` | Unit | DistilBERT theme extraction (output format, label count, types) |
| `test_topic_generator.py` | Unit | GPT-2 starter generation (output format, fallback behavior) |
| `test_fact_checker.py` | Unit | Wikipedia API integration (success, timeout, 404 handling) |
| `test_routes.py` | Integration | All 7 API endpoints with mocked services (validation, status codes, response schemas) |

> **Note:** Integration tests mock all AI services and file I/O, so they run **instantly** without model downloads or filesystem side-effects.

---

## 💾 Data Storage

The application uses **JSON files** for lightweight, zero-configuration persistence.

### Conversation History

**File:** `data/conversation_history.json`

Each entry contains:
```json
{
  "user_name": "string",
  "interests": ["string"],
  "event_description": "string",
  "themes": ["string"],
  "starters": ["string"],
  "timestamp": "ISO 8601 UTC"
}
```

### Feedback Log

**File:** `data/feedback_log.json`

Each entry contains:
```json
{
  "suggestion": "string",
  "action": "like | dislike",
  "timestamp": "ISO 8601 UTC"
}
```

> Both files are auto-created on first write. They are listed in `.gitignore` to avoid committing user data.

---

## 🧠 Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Models loaded at startup** | AI models are loaded once at module import time — not per-request — eliminating per-request loading overhead (~2-5s) |
| **`set_seed(42)` on GPT-2** | Reproducible outputs for the same input, valuable for testing and consistent demos |
| **Auto-logging on `/generate-conversation`** | The frontend doesn't need to manage history separately; data integrity is ensured server-side |
| **Graceful error handling on Wikipedia** | Network failures return user-friendly messages instead of crashing — the app remains resilient |
| **`pathlib.Path` throughout** | Cross-platform file handling (Windows / macOS / Linux) without OS-specific path separators |
| **Hub-and-Spoke routing** | New feature routers can be added without modifying existing code (Open/Closed Principle) |
| **Pydantic v2 schemas** | Type-safe validation with automatic 422 responses for malformed requests |
| **Service layer separation** | Each service file has a single responsibility; services are imported at the router level and easily mockable in tests |
| **JSON storage over databases** | Zero configuration, no external dependencies, sufficient for single-user / demo deployments |
| **`sys.path.insert` in Streamlit** | Allows importing `app.services` from the `frontend/` subdirectory regardless of working directory |

---

## 🔮 Future Enhancements

| Enhancement | Approach | Priority |
|-------------|----------|----------|
| 🌍 Multilingual support | Swap DistilBERT for `xlm-roberta-large` for 100+ language support | Medium |
| 🎯 Recommendation engine | Collaborative filtering on `feedback_log.json` data to improve suggestions | High |
| 🎤 Voice input | Integrate OpenAI Whisper for speech-to-text event descriptions | Low |
| ☁️ Cloud deployment | Docker → Google Cloud Run (API) + Streamlit Cloud (UI) | High |
| 🔐 Authentication | Add `/users` router with JWT-based auth and per-user history | Medium |
| 🗄️ Database backend | Replace JSON logs with SQLite/PostgreSQL via SQLAlchemy | Medium |
| 📧 Email integration | Send generated starters to user's email before the event | Low |
| 🧪 A/B testing | Compare different GPT-2 prompts and temperature settings | Medium |

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create a feature branch:** `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite:** `pytest tests/ -v`
5. **Commit:** `git commit -m "Add amazing feature"`
6. **Push:** `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Python code follows [PEP 8](https://peps.python.org/pep-0008/)
- All functions include docstrings with parameter/return documentation
- Type hints are used throughout

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **GeethaPranathi** — [GitHub Profile](https://github.com/GeethaPranathi)

---

<p align="center">
  <strong>Built with ❤️ using FastAPI, Streamlit, and Hugging Face Transformers</strong>
</p>
]]>
