"""
tests/test_fact_checker.py
--------------------------
Unit tests for the fact_checker service.

All HTTP calls to Wikipedia are mocked with unittest.mock so tests run
offline and deterministically.
"""

from unittest.mock import MagicMock, patch

import pytest
import requests


class TestFactCheck:
    """Tests for fact_check()."""

    @patch("app.services.fact_checker.requests.get")
    def test_returns_extract_on_success(self, mock_get):
        """Should return the 'extract' field from the Wikipedia JSON response."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "title": "Artificial intelligence",
            "extract": "Artificial intelligence (AI) is intelligence demonstrated by machines.",
        }
        mock_get.return_value = mock_response

        from app.services.fact_checker import fact_check

        result = fact_check("Artificial intelligence")
        assert "Artificial intelligence" in result
        assert "machines" in result

    @patch("app.services.fact_checker.requests.get")
    def test_returns_not_found_message_on_404(self, mock_get):
        """Should return a user-friendly message when the article does not exist."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        http_error = requests.exceptions.HTTPError(response=mock_response)
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response

        from app.services.fact_checker import fact_check

        result = fact_check("xyzzy_nonexistent_topic_12345")
        assert "No Wikipedia article found" in result or "error" in result.lower()

    @patch("app.services.fact_checker.requests.get")
    def test_returns_timeout_message_on_timeout(self, mock_get):
        """Should return a timeout message when the request times out."""
        mock_get.side_effect = requests.exceptions.Timeout()

        from app.services.fact_checker import fact_check

        result = fact_check("Blockchain")
        assert "timed out" in result.lower() or "timeout" in result.lower()

    @patch("app.services.fact_checker.requests.get")
    def test_returns_network_error_message_on_connection_error(self, mock_get):
        """Should return a network error message on connection failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError("No route to host")

        from app.services.fact_checker import fact_check

        result = fact_check("Python programming language")
        assert "network error" in result.lower() or "error" in result.lower()

    @patch("app.services.fact_checker.requests.get")
    def test_returns_not_found_when_extract_is_empty(self, mock_get):
        """Should return a not-found message when the extract field is empty."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"title": "SomeTopic", "extract": ""}
        mock_get.return_value = mock_response

        from app.services.fact_checker import fact_check

        result = fact_check("SomeTopic")
        assert "No Wikipedia article found" in result

    @patch("app.services.fact_checker.requests.get")
    def test_formats_query_with_underscores_in_url(self, mock_get):
        """Should replace spaces with underscores in the Wikipedia URL."""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "extract": "Machine learning is a field of AI."
        }
        mock_get.return_value = mock_response

        from app.services.fact_checker import fact_check

        fact_check("machine learning")

        called_url: str = mock_get.call_args[0][0]
        assert "machine_learning" in called_url
