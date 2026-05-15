"""Secret words with categories — hints are generated at runtime by the LLM."""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WordEntry:
    word: str
    category: str


WORDS: tuple[WordEntry, ...] = (
    WordEntry("python", "Technology"),
    WordEntry("ocean", "Nature"),
    WordEntry("guitar", "Music"),
    WordEntry("eclipse", "Science"),
    WordEntry("castle", "Places"),
    WordEntry("volcano", "Nature"),
    WordEntry("piano", "Music"),
    WordEntry("diamond", "Objects"),
    WordEntry("rocket", "Science"),
    WordEntry("penguin", "Animals"),
    WordEntry("tornado", "Weather"),
    WordEntry("library", "Places"),
    WordEntry("planet", "Science"),
    WordEntry("cookie", "Food"),
    WordEntry("dragon", "Fantasy"),
    WordEntry("camera", "Technology"),
    WordEntry("forest", "Nature"),
    WordEntry("puzzle", "Games"),
    WordEntry("thunder", "Weather"),
    WordEntry("butterfly", "Animals"),
    WordEntry("keyboard", "Technology"),
    WordEntry("rainbow", "Nature"),
    WordEntry("elephant", "Animals"),
    WordEntry("telescope", "Science"),
    WordEntry("sandwich", "Food"),
    WordEntry("compass", "Objects"),
    WordEntry("dolphin", "Animals"),
    WordEntry("lantern", "Objects"),
    WordEntry("treasure", "Fantasy"),
    WordEntry("umbrella", "Objects"),
    WordEntry("wizard", "Fantasy"),
    WordEntry("anchor", "Objects"),
    WordEntry("crystal", "Objects"),
    WordEntry("jungle", "Nature"),
    WordEntry("meteor", "Science"),
    WordEntry("pirate", "Fantasy"),
    WordEntry("robot", "Technology"),
    WordEntry("sunset", "Nature"),
    WordEntry("tunnel", "Places"),
    WordEntry("vampire", "Fantasy"),
    WordEntry("waterfall", "Nature"),
    WordEntry("zeppelin", "Transport"),
)


def pick_random_word() -> WordEntry:
    return random.choice(WORDS)
