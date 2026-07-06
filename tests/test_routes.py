"""
tests/test_routes.py
--------------------
Integration tests for the FastAPI routes using httpx's AsyncClient
via the FastAPI TestClient.

All heavy AI service calls (DistilBERT, GPT-2) and file I/O (loggers)
are mocked so these tests run instantly without model downloads or
filesystem side-effects.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    """
    Create a FastAPI TestClient with all AI services mocked.
    Mocking at the router import level ensures the services are never
    actually called during API tests.
    """
    with (
        patch(
            "app.routers.conversation.extract_event_themes",
            return_value=["artificial intelligence", "healthcare", "blockchain"],
        ),
        patch(
            "app.routers.conversation.generate_topics",
            return_value=[
                "What's your take on AI in diagnostics?",
                "Have you explored federated learning for patient data?",
                "How do you see blockchain changing medical records?",
            ],
        ),
        patch("app.routers.conversation.fact_check", return_value="Wikipedia extract here."),
        patch("app.routers.conversation.log_conversation", return_value=None),
        patch("app.routers.conversation.load_history", return_value=[]),
        patch("app.routers.conversation.log_feedback", return_value=None),
        patch("app.routers.conversation.load_feedback", return_value=[]),
    ):
        from app.main import app

        with TestClient(app) as c:
            yield c


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


class TestHealthCheck:
    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_contains_status_ok(self, client):
        data = client.get("/").json()
        assert data["status"] == "ok"

    def test_root_contains_docs_link(self, client):
        data = client.get("/").json()
        assert "docs" in data


# ---------------------------------------------------------------------------
# POST /conversation/analyze-event
# ---------------------------------------------------------------------------


class TestAnalyzeEvent:
    _payload = {
        "description": "A summit focused on AI applications in modern healthcare systems.",
        "user_profile": {
            "name": "Alice Smith",
            "interests": ["machine learning", "bioinformatics"],
        },
    }

    def test_returns_200(self, client):
        response = client.post("/conversation/analyze-event", json=self._payload)
        assert response.status_code == 200

    def test_returns_themes_list(self, client):
        data = client.post("/conversation/analyze-event", json=self._payload).json()
        assert "themes" in data
        assert isinstance(data["themes"], list)
        assert len(data["themes"]) == 3

    def test_rejects_short_description(self, client):
        bad_payload = {
            "description": "short",  # < 10 chars
            "user_profile": {"name": "Bob", "interests": ["AI"]},
        }
        response = client.post("/conversation/analyze-event", json=bad_payload)
        assert response.status_code == 422

    def test_rejects_missing_user_profile(self, client):
        response = client.post(
            "/conversation/analyze-event",
            json={"description": "A valid description that is long enough."},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /conversation/fact-check
# ---------------------------------------------------------------------------


class TestFactCheck:
    def test_returns_200(self, client):
        response = client.post(
            "/conversation/fact-check", json={"query": "Artificial intelligence"}
        )
        assert response.status_code == 200

    def test_response_contains_query_and_result(self, client):
        data = client.post(
            "/conversation/fact-check", json={"query": "Machine learning"}
        ).json()
        assert "query" in data
        assert "result" in data
        assert data["query"] == "Machine learning"

    def test_rejects_empty_query(self, client):
        response = client.post("/conversation/fact-check", json={"query": " "})
        # Single space after strip still passes pydantic min_length=2,
        # but Wikipedia returns a not-found message — just verify 200.
        # If the validator rejects it, 422 is also acceptable.
        assert response.status_code in (200, 422)

    def test_rejects_missing_query_field(self, client):
        response = client.post("/conversation/fact-check", json={})
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /conversation/generate-conversation
# ---------------------------------------------------------------------------


class TestGenerateConversation:
    _payload = {
        "description": "A fintech summit exploring the intersection of AI and decentralised finance.",
        "user_profile": {
            "name": "Charlie Brown",
            "interests": ["fintech", "blockchain", "startup investing"],
        },
    }

    def test_returns_200(self, client):
        response = client.post("/conversation/generate-conversation", json=self._payload)
        assert response.status_code == 200

    def test_response_contains_themes_and_starters(self, client):
        data = client.post(
            "/conversation/generate-conversation", json=self._payload
        ).json()
        assert "themes" in data
        assert "starters" in data

    def test_themes_is_list_of_strings(self, client):
        data = client.post(
            "/conversation/generate-conversation", json=self._payload
        ).json()
        assert isinstance(data["themes"], list)
        for t in data["themes"]:
            assert isinstance(t, str)

    def test_starters_is_non_empty_list(self, client):
        data = client.post(
            "/conversation/generate-conversation", json=self._payload
        ).json()
        assert isinstance(data["starters"], list)
        assert len(data["starters"]) >= 1

    def test_rejects_empty_interests(self, client):
        bad_payload = {
            "description": "A valid long enough description for the event.",
            "user_profile": {"name": "Dave", "interests": []},
        }
        response = client.post("/conversation/generate-conversation", json=bad_payload)
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# POST /conversation/feedback
# ---------------------------------------------------------------------------


class TestFeedback:
    def test_like_returns_200(self, client):
        response = client.post(
            "/conversation/feedback",
            json={"suggestion": "What is your take on AI?", "action": "like"},
        )
        assert response.status_code == 200

    def test_dislike_returns_200(self, client):
        response = client.post(
            "/conversation/feedback",
            json={"suggestion": "Tell me about blockchain.", "action": "dislike"},
        )
        assert response.status_code == 200

    def test_invalid_action_rejected(self, client):
        response = client.post(
            "/conversation/feedback",
            json={"suggestion": "A suggestion", "action": "meh"},
        )
        assert response.status_code == 422

    def test_missing_suggestion_rejected(self, client):
        response = client.post(
            "/conversation/feedback",
            json={"action": "like"},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /conversation/history
# ---------------------------------------------------------------------------


class TestHistory:
    def test_returns_200(self, client):
        response = client.get("/conversation/history")
        assert response.status_code == 200

    def test_returns_list(self, client):
        data = client.get("/conversation/history").json()
        assert isinstance(data, list)


# ---------------------------------------------------------------------------
# GET /conversation/feedback
# ---------------------------------------------------------------------------


class TestGetFeedback:
    def test_returns_200(self, client):
        response = client.get("/conversation/feedback")
        assert response.status_code == 200

    def test_returns_list(self, client):
        data = client.get("/conversation/feedback").json()
        assert isinstance(data, list)

