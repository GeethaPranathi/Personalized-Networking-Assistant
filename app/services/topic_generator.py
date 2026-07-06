"""
topic_generator.py
------------------
Handles conversation starter generation using GPT-2 Small via the Hugging
Face Transformers pipeline API.

GPT-2 Small was chosen because it runs efficiently on standard CPU hardware
(no GPU required), integrates cleanly via the pipeline abstraction, and
produces sufficiently natural, punchy conversation openers for professional
networking contexts.

Design decisions:
- Pipeline loaded once at module level to avoid per-request model loading.
- set_seed(42) provides reproducible outputs for the same input, which is
  invaluable for debugging, testing, and consistent user experience.
- Prompt engineering guides GPT-2 toward producing conversation starters
  rather than arbitrary prose.
"""

from transformers import pipeline, set_seed

# ---------------------------------------------------------------------------
# Module-level pipeline initialisation (loaded once at application startup)
# ---------------------------------------------------------------------------
_generator = pipeline("text-generation", model="gpt2")

# Fix the random seed for reproducibility across runs.
set_seed(42)


def generate_topics(themes: list[str], interests: list[str]) -> list[str]:
    """
    Generate three professional conversation starters tailored to the given
    event themes and user interests.

    Parameters
    ----------
    themes : list[str]
        Top themes extracted from the event description (via DistilBERT).
    interests : list[str]
        The user's professional interest areas from their profile.

    Returns
    -------
    list[str]
        A list of up to three cleaned conversation starter strings.
    """
    themes_str = ", ".join(themes)
    interests_str = ", ".join(interests)

    # Structured natural-language prompt that guides GPT-2 toward the desired
    # output format — short, first-person, professional conversation openers.
    prompt = (
        f"I am attending a networking event focused on {themes_str}. "
        f"My professional interests include {interests_str}. "
        f"Here are three conversation starters I could use:\n"
        f"1."
    )

    # max_new_tokens guarantees the model has headroom to generate output tokens
    # regardless of how long the input prompt is.
    # num_return_sequences=1 returns a single generation run.
    output = _generator(
        prompt,
        max_new_tokens=100,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.85,
        top_p=0.92,
        pad_token_id=50256,  # GPT-2's EOS token used as padding
    )

    generated_text: str = output[0]["generated_text"]

    # Post-processing: extract the generated portion after the prompt,
    # split by newline, strip bullet markers, and return the first 3 items.
    generated_portion = generated_text[len(prompt) - 2 :]  # include "1."
    lines = generated_portion.strip().split("\n")

    starters: list[str] = []
    for line in lines:
        # Strip leading numbering (e.g. "1.", "2.", "-", "*") and whitespace.
        cleaned = line.strip().lstrip("0123456789.-*) ").strip()
        if cleaned:
            starters.append(cleaned)
        if len(starters) == 3:
            break

    # Guarantee at least one fallback if generation produced no usable lines.
    if not starters:
        starters = [
            f"What's your take on the latest developments in {themes[0]}?"
        ]

    return starters
