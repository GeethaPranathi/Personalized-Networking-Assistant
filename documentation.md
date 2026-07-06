# 🤝 Personalized Network Assistant Documentation

This is a local copy of the project documentation for offline reference. For the most updated version, please refer to the main repository.

---

> **AI-powered conversation starter generator** that extracts themes from networking event descriptions, generates tailored icebreakers using GPT-2, and verifies facts via Wikipedia — all wrapped in a sleek dark-themed web interface.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?style=for-the-badge&logo=huggingface&logoColor=black)](https://huggingface.co)

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
| **Backend API** | FastAPI + Uvicorn | High-performance async REST API |
| **Theme Extraction** | DistilBERT (zero-shot) | Classify event descriptions into professional themes |
| **Text Generation** | GPT-2 Small | Generate natural conversation starters |
| **Fact Checking** | Wikipedia REST API | Real-time fact verification |
| **Frontend** | Streamlit | Interactive web dashboard |
| **Data Validation** | Pydantic v2 | Request/response schema validation |
| **Testing** | pytest + httpx | Unit & integration tests |
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

---

## ▶️ Running the Application

You need **two terminals** — one for the backend, one for the frontend.

### Terminal 1: Start the FastAPI Backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Start the Streamlit Frontend

```bash
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

---

### Generate Conversation Starters (Full Pipeline)

```
POST /conversation/generate-conversation
```

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

---

## 🧪 Testing

```bash
pytest tests/ -v
```

---

## 💾 Data Storage

The application uses **JSON files** for lightweight, zero-configuration persistence.

- **Conversation History**: `data/conversation_history.json`
- **Feedback Log**: `data/feedback_log.json`

---

## 🧠 Design Decisions

- **Models loaded at startup** to eliminate loading overhead on requests.
- **`set_seed(42)` on GPT-2** for reproducible output generators.
- **Auto-logging on `/generate-conversation`** to enforce backend data integration.
- **Graceful error handling on Wikipedia** to remain resilient.
- **`pathlib.Path`** for cross-platform compatibility.

---

## 👥 Authors

- **GeethaPranathi** — [GitHub Profile](https://github.com/GeethaPranathi)
