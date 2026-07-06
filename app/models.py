"""
models.py
---------
Pydantic data schemas that form the backbone of all data exchange
between the frontend and backend. FastAPI uses these models for
automatic request validation, serialization, and Swagger documentation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class UserProfile(BaseModel):
    """Represents the end-user's profile used to personalise suggestions."""

    name: str = Field(..., min_length=1, description="Full name of the user")
    interests: List[str] = Field(
        ..., min_length=1, description="List of professional interests or expertise areas"
    )


class EventRequest(BaseModel):
    """Payload sent when the user submits an event description for analysis."""

    description: str = Field(
        ...,
        min_length=10,
        description="Detailed description of the networking event",
    )
    user_profile: UserProfile = Field(
        ..., description="Profile of the user attending the event"
    )


class ThemeResponse(BaseModel):
    """Response containing the top themes extracted from an event description."""

    themes: List[str] = Field(
        ..., description="Top-3 themes identified by DistilBERT zero-shot classifier"
    )


class ConversationRequest(BaseModel):
    """
    Direct request to generate conversation starters given pre-extracted
    themes and user interests.
    """

    themes: List[str] = Field(..., description="Pre-extracted event themes")
    interests: List[str] = Field(..., description="User's professional interests")


class ConversationResponse(BaseModel):
    """
    Full pipeline response containing both the extracted themes and
    the generated conversation starters.
    """

    themes: List[str] = Field(..., description="Themes extracted from the event description")
    starters: List[str] = Field(
        ..., description="AI-generated conversation starter suggestions"
    )


class FactCheckRequest(BaseModel):
    """Payload for a Wikipedia fact-verification request."""

    query: str = Field(
        ..., min_length=2, description="Topic or claim to look up on Wikipedia"
    )


class FactCheckResponse(BaseModel):
    """Response containing the Wikipedia summary for the queried topic."""

    query: str = Field(..., description="The original query string")
    result: str = Field(..., description="Wikipedia extract or error message")


class FeedbackRequest(BaseModel):
    """Captures explicit user feedback on a single conversation starter."""

    suggestion: str = Field(
        ..., description="The exact conversation starter text that was rated"
    )
    action: str = Field(
        ...,
        pattern="^(like|dislike)$",
        description="User action: 'like' or 'dislike'",
    )
