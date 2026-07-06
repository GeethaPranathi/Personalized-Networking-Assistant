"""
event_analyzer.py
-----------------
Responsible for intelligent theme extraction from event descriptions using
Hugging Face's zero-shot classification pipeline backed by DistilBERT.

The pipeline is instantiated once at module import time (startup) so that
subsequent API calls pay no model-loading cost. This is a deliberate
performance-first design: the heavy one-time cost happens during
application startup, not during user-facing requests.
"""

from transformers import pipeline

# ---------------------------------------------------------------------------
# Module-level pipeline initialisation (loaded once at application startup)
# ---------------------------------------------------------------------------
# "typeform/distilbert-base-uncased-mnli" is a DistilBERT model fine-tuned on
# MultiNLI for zero-shot classification — it achieves the optimal balance
# between inference speed and accuracy for real-time classification tasks.
_classifier = pipeline(
    "zero-shot-classification",
    model="typeform/distilbert-base-uncased-mnli",
)

# Default professional networking themes used when no custom labels are provided.
_DEFAULT_LABELS = [
    "artificial intelligence",
    "healthcare",
    "blockchain",
    "education",
    "sustainability",
    "finance",
    "cybersecurity",
    "entrepreneurship",
    "data science",
    "cloud computing",
    "marketing",
    "leadership",
]


def extract_event_themes(
    description: str,
    candidate_labels: list[str] | None = None,
) -> list[str]:
    """
    Extract the top-3 professional themes from a networking event description.

    Parameters
    ----------
    description : str
        Free-text description of the networking event.
    candidate_labels : list[str] | None
        Optional custom label set. Falls back to ``_DEFAULT_LABELS`` when
        omitted.

    Returns
    -------
    list[str]
        The three highest-scoring theme labels, ordered by confidence score
        (descending).
    """
    labels = candidate_labels if candidate_labels else _DEFAULT_LABELS
    result = _classifier(description, candidate_labels=labels, multi_label=False)
    # result["labels"] is already sorted highest-score first by the pipeline.
    return result["labels"][:3]
