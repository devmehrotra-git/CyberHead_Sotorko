"""Conservative, script-only language routing helpers."""

from __future__ import annotations

import unicodedata
import re

_COMMON_ENGLISH_WORDS = {
    "a", "an", "and", "are", "before", "check", "for", "from", "hello", "is", "message", "please", "review", "send", "the", "this", "to", "your",
}


def has_meaningful_bengali_script(text: str, *, minimum_letters: int = 4, minimum_ratio: float = 0.25) -> bool:
    """Return true only for a substantial Bengali-script signal.

    This intentionally does not identify Banglish or Hindi. It counts Bengali
    Unicode letters against all letters, so a stray Bengali character in an
    otherwise English message is not enough to change the analyzer path.
    """
    bengali_letters = 0
    total_letters = 0
    for character in text:
        if not unicodedata.category(character).startswith("L"):
            continue
        total_letters += 1
        if "\u0980" <= character <= "\u09ff":
            bengali_letters += 1
    return bengali_letters >= minimum_letters and bengali_letters / max(total_letters, 1) >= minimum_ratio


def is_probably_english(text: str) -> bool:
    """Conservatively recognize common English prose for auto routing."""
    if has_meaningful_bengali_script(text) or any("\u0900" <= character <= "\u097f" for character in text):
        return False
    words = set(re.findall(r"[a-z]+", text.casefold()))
    return len(words & _COMMON_ENGLISH_WORDS) >= 2
