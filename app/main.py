"""
main.py
-------
FastAPI application entry point.

Intentionally minimal — follows the principle of doing one thing well:
1. Creates the FastAPI application instance with metadata for Swagger docs.
2. Registers the conversation router (all business-logic endpoints).
3. Exposes a GET / health-check endpoint for load-balancer and monitoring use.

The health-check endpoint is a production best practice: it lets external
systems quickly verify the API is running before attempting any business-logic
calls, without triggering any expensive AI model inference.
"""

from fastapi import FastAPI

from app.routers.conversation import router as conversation_router

# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Personalized Network Assistant API",
    description=(
        "AI-powered API that extracts professional themes from networking event "
        "descriptions, generates tailored conversation starters using GPT-2, "
        "and verifies facts via Wikipedia. Built with FastAPI + Hugging Face."
    ),
    version="1.0.0",
    contact={
        "name": "Network Assistant Team",
    },
    license_info={
        "name": "MIT",
    },
)

# ---------------------------------------------------------------------------
# Router registration
# ---------------------------------------------------------------------------
app.include_router(conversation_router)


# ---------------------------------------------------------------------------
# Health-check endpoint
# ---------------------------------------------------------------------------
@app.get("/", tags=["Health"], summary="Health check")
async def root() -> dict:
    """
    Returns a simple status message confirming the API is running.

    This endpoint is intentionally lightweight — it performs no AI inference
    or file I/O, making it suitable for use by load balancers and uptime
    monitors.
    """
    return {
        "status": "ok",
        "message": "Personalized Network Assistant API is running.",
        "docs": "/docs",
    }
