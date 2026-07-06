"""
tests/test_event_analyzer.py
----------------------------
Unit tests for the event_analyzer service.

The DistilBERT pipeline is mocked so tests run instantly without
downloading or loading any model weights.
"""

from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_classifier_output(labels: list[str], scores: list[float]) -> dict:
    """Build a response that mimics the Hugging Face zero-shot pipeline."""
    return {
        "labels": labels,
        "scores": scores,
        "sequence": "test sequence",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestExtractEventThemes:
    """Tests for extract_event_themes()."""

    @patch("app.services.event_analyzer._classifier")
    def test_returns_top_three_themes(self, mock_clf):
        """Should return exactly 3 themes from the classifier output."""
        mock_clf.return_value = _make_classifier_output(
            labels=["artificial intelligence", "healthcare", "blockchain", "education"],
            scores=[0.9, 0.7, 0.5, 0.3],
        )

        from app.services.event_analyzer import extract_event_themes

        result = extract_event_themes("An AI healthcare summit.")
        assert len(result) == 3
        assert result[0] == "artificial intelligence"
        assert result[1] == "healthcare"
        assert result[2] == "blockchain"

    @patch("app.services.event_analyzer._classifier")
    def test_uses_custom_labels_when_provided(self, mock_clf):
        """Should pass custom candidate labels through to the pipeline."""
        custom_labels = ["robotics", "quantum computing"]
        mock_clf.return_value = _make_classifier_output(
            labels=["robotics", "quantum computing"],
            scores=[0.8, 0.6],
        )

        from app.services.event_analyzer import extract_event_themes

        result = extract_event_themes("A robotics conference.", custom_labels)

        # Verify the pipeline was called with the custom labels
        call_kwargs = mock_clf.call_args
        assert call_kwargs[1]["candidate_labels"] == custom_labels

        assert "robotics" in result

    @patch("app.services.event_analyzer._classifier")
    def test_uses_default_labels_when_none_provided(self, mock_clf):
        """Should use the built-in default label set when no labels are given."""
        from app.services.event_analyzer import _DEFAULT_LABELS

        mock_clf.return_value = _make_classifier_output(
            labels=_DEFAULT_LABELS[:3],
            scores=[0.9, 0.8, 0.7],
        )

        from app.services.event_analyzer import extract_event_themes

        extract_event_themes("A general tech event.")

        call_kwargs = mock_clf.call_args
        assert call_kwargs[1]["candidate_labels"] == _DEFAULT_LABELS

    @patch("app.services.event_analyzer._classifier")
    def test_returns_list_of_strings(self, mock_clf):
        """Result should be a list of plain strings."""
        mock_clf.return_value = _make_classifier_output(
            labels=["finance", "sustainability", "leadership"],
            scores=[0.88, 0.72, 0.55],
        )

        from app.services.event_analyzer import extract_event_themes

        result = extract_event_themes("A sustainability finance event.")
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    @patch("app.services.event_analyzer._classifier")
    def test_handles_single_label_output(self, mock_clf):
        """Should return only what the pipeline gives, up to 3."""
        mock_clf.return_value = _make_classifier_output(
            labels=["education"],
            scores=[0.95],
        )

        from app.services.event_analyzer import extract_event_themes

        result = extract_event_themes("An education conference.")
        assert len(result) == 1
        assert result[0] == "education"
