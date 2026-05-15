"""AI-hosted Guess The Word — dynamic LLM hints, max 5 per round."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto

from hint_generator import MAX_HINTS, generate_hint
from word_bank import WordEntry, pick_random_word


class Phase(Enum):
    IDLE = auto()
    PLAYING = auto()
    WON = auto()
    LOST = auto()
    GAVE_UP = auto()


_CHEAT_PATTERNS = re.compile(
    r"(tell\s+me\s+(the\s+)?answer|ignore\s+(all\s+)?instructions|"
    r"reveal\s+(the\s+)?word|what\s+is\s+the\s+(secret\s+)?word|"
    r"give\s+me\s+the\s+answer|show\s+me\s+the\s+answer|"
    r"disregard\s+(your\s+)?(rules|instructions))",
    re.IGNORECASE,
)


@dataclass
class GameEngine:
    _entry: WordEntry | None = field(default=None, init=False)
    _phase: Phase = field(default=Phase.IDLE, init=False)
    _hint_count: int = field(default=0, init=False)
    _hints_used: list[str] = field(default_factory=list, init=False)
    _guesses: list[str] = field(default_factory=list, init=False)

    @property
    def secret(self) -> str | None:
        return self._entry.word if self._entry else None

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def guesses(self) -> tuple[str, ...]:
        return tuple(self._guesses)

    @property
    def hints_used(self) -> tuple[str, ...]:
        return tuple(self._hints_used)

    def new_game(self) -> str:
        self._entry = pick_random_word()
        self._phase = Phase.PLAYING
        self._hint_count = 0
        self._hints_used = []
        self._guesses = []
        return self._start_with_first_hint()

    def give_up(self) -> str:
        if not self._entry or self._phase is not Phase.PLAYING:
            return "No active game. Type 'new game' to play!"
        word = self._entry.word
        self._phase = Phase.GAVE_UP
        return self._say(
            f"You gave up! The word was {word} — "
            f"a {self._entry.category.lower()} classic. Type 'new game' for another round!"
        )

    def process_input(self, text: str) -> str:
        raw = text.strip()
        normalized = raw.lower()

        if normalized in {"new game", "newgame", "restart"}:
            return self.new_game()

        if normalized in {"give up", "giveup", "surrender"}:
            return self.give_up()

        if normalized in {"hint", "another hint"}:
            if self._phase is not Phase.PLAYING or not self._entry:
                return "Start a round with 'new game' first!"
            if self._hints_used:
                return self._say(f"Latest clue:\nHint {self._hint_count}: {self._hints_used[-1]}")
            return self._say("No hint yet — start with 'new game'!")

        if not raw:
            return self._say("Take a guess, or type 'new game' / 'give up'.")

        if _CHEAT_PATTERNS.search(raw):
            return self._say(
                "Nice try! I'm the host — no peeking. "
                "Use the hints and guess the word!"
            )

        if self._phase is not Phase.PLAYING:
            return self._say("Round over. Type 'new game' for a fresh word!")

        if not self._entry:
            return self.new_game()

        self._guesses.append(raw)

        if self._is_correct_guess(raw):
            word = self._entry.word
            self._phase = Phase.WON
            return self._say(
                f"Correct! You got it — {word}! "
                f"({len(self._guesses)} guess{'es' if len(self._guesses) != 1 else ''}, "
                f"{self._hint_count} hint{'s' if self._hint_count != 1 else ''}.) "
                "Type 'new game' to play again!"
            )

        return self._wrong_guess()

    def _wrong_guess(self) -> str:
        assert self._entry is not None
        if self._hint_count >= MAX_HINTS:
            word = self._entry.word
            cat = self._entry.category
            self._phase = Phase.LOST
            return self._say(
                f"Incorrect — and that's all {MAX_HINTS} hints!\n"
                f"The word was {word} ({cat}). "
                f"It's a well-known {cat.lower()} term. "
                "Type 'new game' to try another!"
            )

        try:
            hint = generate_hint(
                secret=self._entry.word,
                category=self._entry.category,
                hint_number=self._hint_count + 1,
                previous_hints=tuple(self._hints_used),
            )
        except Exception as exc:
            return self._say(f"Host error: {exc}")

        self._hint_count += 1
        self._hints_used.append(hint)
        return self._say(f"Incorrect!\nHint {self._hint_count}: {hint}")

    def _start_with_first_hint(self) -> str:
        assert self._entry is not None
        try:
            hint = generate_hint(
                secret=self._entry.word,
                category=self._entry.category,
                hint_number=1,
                previous_hints=(),
            )
        except Exception as exc:
            self._phase = Phase.IDLE
            self._entry = None
            return self._say(f"Cannot start: {exc}")

        self._hint_count = 1
        self._hints_used = [hint]
        cat = self._entry.category
        return self._say(f"Category: {cat}\nHint 1: {hint}")

    @staticmethod
    def _normalize_guess(text: str) -> str:
        return re.sub(r"[^a-z0-9]", "", text.strip().lower())

    def _is_correct_guess(self, text: str) -> bool:
        assert self._entry is not None
        return self._normalize_guess(text) == self._normalize_guess(self._entry.word)

    @staticmethod
    def _say(message: str) -> str:
        return message
