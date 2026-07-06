"""
feedback_logger.py
------------------
Captures explicit user feedback (like / dislike) on individual conversation
starters. Follows the same architectural pattern as history_logger.py but
serves a distinct purpose: building a dataset for future recommendation
improvement and prompt engineering analytics.

Each feedback entry captures:
- The exact suggestion text (enables correlation with specific generated content)
- The user action ('like' or 'dislike')
- A UTC timestamp (for chronological analysis)
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Resolve path relative to the project root regardless of cwd.
_FEEDBACK_FILE = Path(__file__).parent.parent.parent / "data" / "feedback_log.json"


def log_feedback(suggestion: str, action: str) -> None:
    """
    Append a single feedback event to the persistent feedback log.

    Parameters
    ----------
    suggestion : str
        The exact conversation starter text that the user rated.
    action : str
        Either ``'like'`` or ``'dislike'``.
    """
    entry = {
        "suggestion": suggestion,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    feedback = _load_raw()
    feedback.append(entry)

    _FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_FEEDBACK_FILE, "w", encoding="utf-8") as fh:
        json.dump(feedback, fh, indent=2, ensure_ascii=False)


def load_feedback() -> list[dict]:
    """
    Load all stored feedback entries.

    Returns
    -------
    list[dict]
        All persisted feedback entries, or an empty list if none exist yet.
    """
    return _load_raw()


def _load_raw() -> list[dict]:
    """Internal helper: read the JSON file or return an empty list."""
    if not _FEEDBACK_FILE.exists():
        return []
    try:
        with open(_FEEDBACK_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return []
