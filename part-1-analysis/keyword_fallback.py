#!/usr/bin/env python3
"""Keyword fallback for music discovery themes."""

from __future__ import annotations

THEME_KEYWORDS: dict[str, list[str]] = {
    "discovery_friction": [
        "find new", "discover", "explore", "search", "new music", "new artist", "hard to find",
    ],
    "bad_recommendations": [
        "discover weekly", "daily mix", "recommend", "radio", "algorithm", "suggestion", "mix",
    ],
    "repeat_listening": [
        "same song", "repeat", "playlist", "again", "loop", "familiar", "liked songs", "on repeat",
    ],
    "library_clutter": [
        "library", "saved", "liked songs", "too many", "collection", "browse",
    ],
    "ui_complexity": [
        "ui", "interface", "home screen", "clutter", "navigate", "confusing", "layout",
    ],
    "social_discovery": [
        "friend", "blend", "social", "share", "together", "follow",
    ],
    "podcast_vs_music": [
        "podcast", "podcasts", "episode", "show",
    ],
    "pricing_ads": [
        "ad", "ads", "premium", "free tier", "skip", "subscription", "pay",
    ],
}


def classify_keyword(text: str, title: str = "") -> str:
    blob = f"{title} {text}".lower()
    scores = {tid: 0 for tid in THEME_KEYWORDS}
    for tid, words in THEME_KEYWORDS.items():
        for w in words:
            if w in blob:
                scores[tid] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "discovery_friction"
