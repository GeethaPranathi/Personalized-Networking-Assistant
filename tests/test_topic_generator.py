"""
tests/test_topic_generator.py
-----------------------------
Unit tests for the topic_generator service.

The GPT-2 pipeline is mocked so tests run instantly without
downloading or loading any model weights.
"""

from unittest.mock import patch


class TestGenerateTopics:
    """Tests for generate_topics()."""

    @patch("app.services.topic_generator._generator")
    def test_returns_list_of_starters(self, mock_gen):
        """Should return a list of strings."""
        mock_gen.return_value = [
            {
                "generated_text": (
                    "I am attending a networking event focused on artificial intelligence, healthcare. "
                    "My professional interests include data science, fintech. "
                    "Here are three conversation starters I could use:\n"
                    "1. What projects are you working on in AI?\n"
                    "2. How do you see blockchain changing healthcare?\n"
                    "3. Have you tried any new ML frameworks lately?\n"
                )
            }
        ]

        from app.services.topic_generator import generate_topics

        result = generate_topics(
            themes=["artificial intelligence", "healthcare"],
            interests=["data science", "fintech"],
        )

        assert isinstance(result, list)
        assert len(result) >= 1
        for item in result:
            assert isinstance(item, str)
            assert len(item) > 0

    @patch("app.services.topic_generator._generator")
    def test_returns_maximum_three_starters(self, mock_gen):
        """Should never return more than 3 starters."""
        mock_gen.return_value = [
            {
                "generated_text": (
                    "I am attending a networking event focused on blockchain. "
                    "My professional interests include finance. "
                    "Here are three conversation starters I could use:\n"
                    "1. Starter one here\n"
                    "2. Starter two here\n"
                    "3. Starter three here\n"
                    "4. Starter four should be ignored\n"
                    "5. Starter five should also be ignored\n"
                )
            }
        ]

        from app.services.topic_generator import generate_topics

        result = generate_topics(["blockchain"], ["finance"])
        assert len(result) <= 3

    @patch("app.services.topic_generator._generator")
    def test_fallback_when_no_usable_lines(self, mock_gen):
        """Should return a fallback starter when GPT-2 produces no clean output."""
        # Simulate GPT-2 producing only whitespace after the prompt
        mock_gen.return_value = [
            {
                "generated_text": (
                    "I am attending a networking event focused on sustainability. "
                    "My professional interests include green energy. "
                    "Here are three conversation starters I could use:\n"
                    "1."
                )
            }
        ]

        from app.services.topic_generator import generate_topics

        result = generate_topics(["sustainability"], ["green energy"])
        assert len(result) >= 1
        assert isinstance(result[0], str)

    @patch("app.services.topic_generator._generator")
    def test_themes_and_interests_appear_in_prompt(self, mock_gen):
        """The pipeline should be called with a prompt containing the themes and interests."""
        mock_gen.return_value = [
            {
                "generated_text": (
                    "I am attending a networking event focused on cybersecurity. "
                    "My professional interests include cloud computing. "
                    "Here are three conversation starters I could use:\n"
                    "1. Starter about security\n"
                )
            }
        ]

        from app.services.topic_generator import generate_topics

        generate_topics(["cybersecurity"], ["cloud computing"])

        call_args = mock_gen.call_args
        prompt_used: str = call_args[0][0]
        assert "cybersecurity" in prompt_used
        assert "cloud computing" in prompt_used
