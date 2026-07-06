"""
history_logger.py
-----------------
Provides persistent storage for conversation sessions using a simple
JSON append pattern.

Design decisions:
- pathlib.Path is used throughout for cross-platform file-path handling
  (works identically on Windows, macOS, and Linux).
- The read-modify-write pattern ensures data integrity for single-process use.
- A timestamp is always injected by the logger (not the caller) so that
  history entries are consistently formatted regardless of what the caller
  passes in.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# Resolve path relative to the project root regardless of cwd.
_HISTORY_FILE = Path(__file__).parent.parent.parent / "data" / "conversation_history.json"


def log_conversation(data: dict) -> None:
    """
    Append a conversation session to the persistent history file.

    A UTC ISO-8601 timestamp is automatically added to the entry under
    the key ``"timestamp"``.

    Parameters
    ----------
    data : dict
        Conversation data to persist. Typically includes themes, starters,
        event description, and user profile information.
    """
    # Inject timestamp — always in UTC for consistency across timezones.
    entry = {**data, "timestamp": datetime.now(timezone.utc).isoformat()}

    history = _load_raw()
    history.append(entry)

    _HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_HISTORY_FILE, "w", encoding="utf-8") as fh:
        json.dump(history, fh, indent=2, ensure_ascii=False)


def load_history() -> list[dict]:
    """
    Load all stored conversation sessions.

    Returns
    -------
    list[dict]
        All persisted entries, or an empty list if no history exists yet.
    """
    return _load_raw()


def _load_raw() -> list[dict]:
    """Internal helper: read the JSON file or return an empty list."""
    if not _HISTORY_FILE.exists():
        return []
    try:
        with open(_HISTORY_FILE, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return []
