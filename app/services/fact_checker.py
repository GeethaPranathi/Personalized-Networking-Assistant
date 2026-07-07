"""
fact_checker.py
---------------
Provides quick fact-verification by querying the Wikipedia REST API.

Design philosophy:
- Wikipedia is a publicly accessible, well-maintained knowledge base that
  returns structured JSON data without requiring API keys or authentication.
- Simplicity and reliability are prioritised over sophistication.
- Defensive programming: all network errors, timeouts, and invalid JSON
  responses are caught gracefully so the application never crashes due to
  external API unpredictability.
"""

import urllib.parse
import requests

# Wikipedia REST API endpoint — returns the first paragraph of the most
# relevant article for a given search term.
_WIKIPEDIA_API_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"

# Request timeout in seconds — keeps the API responsive even if Wikipedia
# is slow to respond.
_TIMEOUT_SECONDS = 8


def fact_check(query: str) -> str:
    """
    Fetch the Wikipedia summary extract for the given query string.

    Parameters
    ----------
    query : str
        The topic, person, technology, or claim to look up.

    Returns
    -------
    str
        The plain-text Wikipedia extract for the most relevant article, or
        a user-friendly error message if the lookup fails.
    """
    # Replace spaces with underscores and URL-encode special characters.
    formatted_query = urllib.parse.quote(query.strip().replace(" ", "_"))
    url = _WIKIPEDIA_API_URL.format(formatted_query)

    headers = {
        "User-Agent": "PersonalizedNetworkAssistantBot/1.0.0 (https://github.com/GeethaPranathi/Personalized-Networking-Assistant; pranathi@example.com)"
    }

    try:
        response = requests.get(url, headers=headers, timeout=_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
        extract = data.get("extract", "")
        if extract:
            return extract
        return f"No Wikipedia article found for '{query}'."
    except requests.exceptions.Timeout:
        return "Fact-check request timed out. Please try again."
    except requests.exceptions.HTTPError as exc:
        if exc.response is not None:
            if exc.response.status_code == 404:
                return f"No Wikipedia article found for '{query}'."
            if exc.response.status_code == 429:
                return "Wikipedia rate limit reached. Too many requests. Please try again in a few moments."
        return f"Wikipedia returned an error: {exc}"
    except requests.exceptions.RequestException as exc:
        return f"Network error during fact-check: {exc}"
    except (ValueError, KeyError):
        return "Failed to parse Wikipedia response. Please try again."
