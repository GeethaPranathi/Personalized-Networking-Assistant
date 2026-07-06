"""
routers/conversation.py
-----------------------
Integration point between the HTTP interface and the AI service modules.
Defines three POST endpoints wired together via FastAPI's APIRouter.

Architectural insight:
- /generate-conversation performs automatic side-effect logging — every
  successful call is persisted to history without requiring the frontend to
  take any additional action. This keeps the frontend simple and ensures
  data integrity.
- /analyze-event and /fact-check are standalone endpoints useful for
  debugging, partial integrations, or custom workflows.
"""

from fastapi import APIRouter, HTTPException

from app.models import (
    ConversationResponse,
    EventRequest,
    FactCheckRequest,
    FactCheckResponse,
    FeedbackRequest,
    ThemeResponse,
)
from app.services.event_analyzer import extract_event_themes
from app.services.fact_checker import fact_check
from app.services.feedback_logger import log_feedback, load_feedback
from app.services.history_logger import load_history, log_conversation
from app.services.topic_generator import generate_topics

router = APIRouter(prefix="/conversation", tags=["Conversation"])


# ---------------------------------------------------------------------------
# Endpoint 1: Standalone theme extraction
# ---------------------------------------------------------------------------


@router.post(
    "/analyze-event",
    response_model=ThemeResponse,
    summary="Extract themes from an event description",
    description=(
        "Uses DistilBERT zero-shot classification to identify the top-3 "
        "professional themes from the provided event description."
    ),
)
async def analyze_event(request: EventRequest) -> ThemeResponse:
    """Extract themes from an event description using DistilBERT."""
    try:
        themes = extract_event_themes(request.description)
        return ThemeResponse(themes=themes)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Theme extraction failed: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Endpoint 2: Wikipedia fact-check
# ---------------------------------------------------------------------------


@router.post(
    "/fact-check",
    response_model=FactCheckResponse,
    summary="Fact-check a topic using Wikipedia",
    description=(
        "Queries the Wikipedia REST API for the first paragraph of the most "
        "relevant article. Returns a user-friendly message on failure."
    ),
)
async def fact_check_endpoint(request: FactCheckRequest) -> FactCheckResponse:
    """Fetch a Wikipedia summary for the given query."""
    result = fact_check(request.query)
    return FactCheckResponse(query=request.query, result=result)


# ---------------------------------------------------------------------------
# Endpoint 3: Full pipeline — themes → starters → auto-log
# ---------------------------------------------------------------------------


@router.post(
    "/generate-conversation",
    response_model=ConversationResponse,
    summary="Generate conversation starters (full pipeline)",
    description=(
        "Orchestrates the full AI pipeline: "
        "(1) extracts event themes via DistilBERT, "
        "(2) generates conversation starters via GPT-2, "
        "(3) automatically persists the session to conversation history."
    ),
)
async def generate_conversation(request: EventRequest) -> ConversationResponse:
    """
    Full pipeline endpoint:
    1. Extract themes from event description (DistilBERT)
    2. Generate conversation starters (GPT-2)
    3. Auto-log the session to conversation history
    """
    try:
        # Step 1 — Theme extraction
        themes = extract_event_themes(request.description)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Theme extraction failed: {exc}",
        ) from exc

    try:
        # Step 2 — Conversation starter generation
        starters = generate_topics(themes, request.user_profile.interests)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Conversation generation failed: {exc}",
        ) from exc

    # Step 3 — Auto-log (non-blocking; log failure should not fail the request)
    try:
        log_conversation(
            {
                "user_name": request.user_profile.name,
                "interests": request.user_profile.interests,
                "event_description": request.description,
                "themes": themes,
                "starters": starters,
            }
        )
    except Exception:
        # Log failure is swallowed so the user still gets their response.
        pass

    return ConversationResponse(themes=themes, starters=starters)


# ---------------------------------------------------------------------------
# Endpoint 4: Feedback logging
# ---------------------------------------------------------------------------


@router.post(
    "/feedback",
    summary="Submit feedback on a conversation starter",
    description="Records a like or dislike action against a specific starter suggestion.",
)
async def submit_feedback(request: FeedbackRequest) -> dict:
    """Persist a like/dislike feedback event."""
    try:
        log_feedback(request.suggestion, request.action)
        return {"status": "ok", "message": "Feedback recorded."}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record feedback: {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# Endpoint 5: History retrieval
# ---------------------------------------------------------------------------


@router.get(
    "/history",
    summary="Retrieve conversation history",
    description="Returns all past conversation sessions stored on disk.",
)
async def get_history() -> list:
    """Load and return all stored conversation sessions."""
    return load_history()


# ---------------------------------------------------------------------------
# Endpoint 6: Feedback retrieval
# ---------------------------------------------------------------------------


@router.get(
    "/feedback",
    summary="Retrieve all logged feedback",
    description="Returns all recorded feedback items stored on disk.",
)
async def get_feedback() -> list:
    """Load and return all stored feedback entries."""
    return load_feedback()

