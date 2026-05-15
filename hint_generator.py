"""Generate progressive hints via Google Gemini — one hint per call."""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

MAX_HINTS = 5
DEFAULT_MODEL = "gemini-flash-latest"


@lru_cache(maxsize=1)
def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Add it to a .env file in the project root."
        )
    return genai.Client(api_key=api_key)


def _model() -> str:
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def _scrub_hint(text: str, secret: str) -> str:
    """Remove accidental direct leaks of the secret word."""
    cleaned = text.strip().strip('"').strip("'")
    pattern = re.compile(re.escape(secret), re.IGNORECASE)
    return pattern.sub("-", cleaned)


def generate_hint(
    *,
    secret: str,
    category: str,
    hint_number: int,
    previous_hints: tuple[str, ...],
) -> str:
    """
    Ask Gemini for a single new hint. hint_number is 1-based (1..5).
    """
    prior = "\n".join(f"- {h}" for h in previous_hints) if previous_hints else "(none yet)"
    difficulty = (
        "subtle and clever — avoid obvious giveaways"
        if hint_number <= 2
        else "moderately helpful"
        if hint_number <= 4
        else "the clearest allowed hint without naming the word"
    )

    prompt = (
        "You write hints for a guess-the-word party game. "
        "Never reveal the answer, spell it, rhyme it, or use letter-count clues on hint 1-2. "
        "One short sentence only. No preamble.\n\n"
        f"Category: {category}\n"
        f"Secret word (NEVER output this word): {secret}\n"
        f"Hint number: {hint_number} of {MAX_HINTS}\n"
        f"Difficulty: {difficulty}\n"
        f"Hints already used (do not repeat or paraphrase):\n{prior}\n\n"
        "Return ONLY the hint sentence."
    )

    try:
        response = _client().models.generate_content(
            model=_model(),
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.85,
                max_output_tokens=120,
            ),
        )
    except genai_errors.ClientError as exc:
        if exc.code == 429:
            raise RuntimeError(
                "Gemini quota exceeded. Wait a minute or try GEMINI_MODEL=gemini-flash-latest in .env."
            ) from exc
        raise RuntimeError(f"Gemini API error: {exc}") from exc

    raw = (response.text or "").strip()
    if not raw:
        raise RuntimeError("Gemini returned an empty hint.")
    return _scrub_hint(raw, secret)
