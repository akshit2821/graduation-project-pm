"""Shared labels and presentation helpers for the public workflow app."""

from __future__ import annotations

SOURCE_LABELS = {
    "play_store": "Google Play",
    "app_store": "App Store",
    "reddit": "Reddit",
    "forum": "Community forums",
    "social": "Social media",
    "web": "Web",
}

THEME_LABELS = {
    "discovery_friction": "Hard to find new music",
    "bad_recommendations": "Recommendations miss the mark",
    "repeat_listening": "Same content on loop",
    "library_clutter": "Library too large to explore",
    "ui_complexity": "UI blocks exploration",
    "social_discovery": "Wants shared discovery",
    "podcast_vs_music": "Podcasts crowd out music",
    "pricing_ads": "Free tier limits exploration",
}


def source_label(key: str | None) -> str:
    if not key:
        return "Unknown"
    return SOURCE_LABELS.get(key, key.replace("_", " ").title())


def theme_label(key: str | None) -> str:
    if not key:
        return "Other"
    return THEME_LABELS.get(key, key.replace("_", " ").title())


def format_window(window: dict | None) -> str:
    if not window:
        return "Recent period"
    start = window.get("start") or ""
    end = window.get("end") or ""
    if start and end:
        try:
            from datetime import datetime

            s = datetime.fromisoformat(str(start)).strftime("%b %Y")
            e = datetime.fromisoformat(str(end)).strftime("%b %Y")
            return f"{s} – {e}"
        except ValueError:
            return f"{start} – {end}"
    return "Recent period"


def rating_stars(rating: int | float | None) -> str:
    if rating is None:
        return ""
    try:
        n = max(0, min(5, int(round(float(rating)))))
    except (TypeError, ValueError):
        return ""
    return "★" * n + "☆" * (5 - n)
