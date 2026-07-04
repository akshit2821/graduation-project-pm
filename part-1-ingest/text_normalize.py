"""English-only and no-emoji filtering + text normalization."""

from __future__ import annotations

import re
import unicodedata

_EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\u200d\uFE0F"
    "]",
    flags=re.UNICODE,
)

_NON_LATIN_SCRIPT_RE = re.compile(
    "[\u0900-\u097F\u0980-\u09FF\u4E00-\u9FFF\u0600-\u06FF\u0400-\u04FF]",
    flags=re.UNICODE,
)

_WORDISH_RE = re.compile(r"[A-Za-z0-9]+")


def contains_emoji(text: str) -> bool:
    return bool(text and _EMOJI_RE.search(text))


def normalize_review_text(text: str) -> str:
    if not text:
        return ""
    t = unicodedata.normalize("NFKC", str(text))
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u201c", '"').replace("\u201d", '"')
    t = t.replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", t).strip()


def english_score(text: str) -> float:
    t = normalize_review_text(text)
    if not t:
        return 0.0
    letters = [c for c in t if c.isalpha()]
    if not letters:
        return 0.0
    latin = sum(1 for c in letters if "A" <= c <= "z")
    return latin / len(letters)


def is_english_review(title: str, text: str, *, min_ratio: float = 0.85) -> bool:
    combined = f"{title} {text}".strip()
    if not combined:
        return False
    if _NON_LATIN_SCRIPT_RE.search(combined) and len(_NON_LATIN_SCRIPT_RE.findall(combined)) >= 3:
        return False
    if english_score(combined) < min_ratio:
        return False
    words = _WORDISH_RE.findall(text or title)
    if len(words) < 2 and len((text or "").split()) < 3:
        return False
    return True


def passes_text_filters(
    title: str,
    text: str,
    *,
    english_only: bool = True,
    allow_emojis: bool = False,
    min_english_ratio: float = 0.85,
) -> tuple[bool, str]:
    title_n = normalize_review_text(title)
    text_n = normalize_review_text(text)
    combined = f"{title_n} {text_n}"
    if not allow_emojis and contains_emoji(combined):
        return False, "emoji"
    if english_only and not is_english_review(title_n, text_n, min_ratio=min_english_ratio):
        return False, "non_english"
    if not text_n.strip():
        return False, "empty_after_normalize"
    return True, ""
