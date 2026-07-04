#!/usr/bin/env python3
"""Synthetic Spotify discovery feedback for offline demo (reddit/forum/social + backup play)."""

from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]

SAMPLES = {
    "discovery_friction": [
        ("Hard to explore", "I never find new artists unless friends send links."),
        ("Search useless", "Search only shows artists I already know."),
    ],
    "bad_recommendations": [
        ("Discover Weekly miss", "Discover Weekly keeps recommending the same indie artists."),
        ("Daily mix repeat", "Daily Mix plays the same 20 songs every day."),
    ],
    "repeat_listening": [
        ("Same playlist loop", "I only listen to my 2019 playlist on repeat."),
        ("Comfort listening", "After work I always play familiar songs, never explore."),
    ],
    "library_clutter": [
        ("Too many liked songs", "I have 2000 liked songs and cannot browse them."),
        ("Saved music graveyard", "My library is huge but I play the same 10 tracks."),
    ],
    "ui_complexity": [
        ("Home cluttered", "Home screen is podcasts and shortcuts, hard to find new music."),
        ("Navigation", "Too many tabs, I give up looking for something fresh."),
    ],
    "social_discovery": [
        ("Want friend picks", "Wish I could see what close friends discover weekly."),
        ("Blend dead", "Blend with friends never updates with new artists."),
    ],
    "podcast_vs_music": [
        ("Podcasts dominate", "Home feed pushes podcasts when I want music discovery."),
    ],
    "pricing_ads": [
        ("Ads break flow", "Free tier ads make me skip back to old playlists."),
        ("Skip limit", "Hit skip limit and just replay old favorites."),
    ],
}

REDDIT_EXTRA = [
    ("Discover Weekly stale", "Anyone else get the same Discover Weekly vibe for months?", "reddit"),
    ("Repeat listening", "I realized 80 percent of my hours are Liked Songs only.", "reddit"),
    ("Recommendation rant", "Radio for an artist plays same 15 tracks on loop.", "reddit"),
]

FORUM_EXTRA = [
    ("Algorithm", "How do I reset recommendations? Stuck in a loop."),
    ("New music", "Cannot find new releases that match my taste."),
]


def _dates(n: int) -> list:
    base = datetime.now(timezone.utc).date()
    return [base - timedelta(days=random.randint(1, 120)) for _ in range(n)]


def generate_play_backup(n: int = 150) -> pd.DataFrame:
    themes = list(SAMPLES.keys())
    rows = []
    for i in range(n):
        theme = random.choice(themes)
        title, text = random.choice(SAMPLES[theme])
        rows.append(
            {
                "source": "play_store",
                "platform": "android",
                "date": _dates(1)[0],
                "rating": random.choice([1, 2, 3, 3, 4, 5]),
                "title": title,
                "text": text,
                "upvotes": random.randint(0, 50),
                "url": "",
            }
        )
    return pd.DataFrame(rows)


def generate_manual(source: str, platform: str, items: list, n: int) -> pd.DataFrame:
    dates = _dates(n)
    rows = []
    for i in range(n):
        if i < len(items):
            if len(items[i]) == 3:
                title, text, src = items[i]
            else:
                title, text = items[i][0], items[i][1]
                src = source
        else:
            theme = random.choice(list(SAMPLES.keys()))
            title, text = random.choice(SAMPLES[theme])
            src = source
        rows.append(
            {
                "source": src,
                "platform": platform,
                "date": dates[i],
                "rating": pd.NA,
                "title": title,
                "text": text,
                "upvotes": random.randint(1, 200),
                "url": f"https://example.com/{source}/{i}",
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=PROJECT / "config" / "product.json")
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    slug = cfg["product_slug"]
    raw = PROJECT / "data" / "raw" / slug

    play_path = raw / "play" / "play_reviews.csv"
    if not play_path.is_file() or len(pd.read_csv(play_path)) < 50:
        raw.joinpath("play").mkdir(parents=True, exist_ok=True)
        df = generate_play_backup(200)
        df.to_csv(play_path, index=False)
        print(f"Generated play backup: {len(df)} rows")

    reddit_path = raw / "reddit" / "reddit_posts.csv"
    if not reddit_path.is_file():
        raw.joinpath("reddit").mkdir(parents=True, exist_ok=True)
        items = [(t, x, "reddit") for t, x, _ in REDDIT_EXTRA]
        for theme, pairs in SAMPLES.items():
            for title, text in pairs[:1]:
                items.append((title, text, "reddit"))
        df = generate_manual("reddit", "web", items, 40)
        df.to_csv(reddit_path, index=False)
        print(f"Generated reddit sample: {len(df)} rows")

    forum_path = raw / "forum" / "forums_raw.csv"
    if not forum_path.is_file() or forum_path.stat().st_size < 100:
        raw.joinpath("forum").mkdir(parents=True, exist_ok=True)
        items = [(t, x, "forum") for t, x in FORUM_EXTRA]
        df = generate_manual("forum", "web", items, 25)
        df.to_csv(forum_path, index=False)
        print(f"Generated forum sample: {len(df)} rows")

    social_path = raw / "social" / "social_raw.csv"
    if not social_path.is_file() or social_path.stat().st_size < 100:
        raw.joinpath("social").mkdir(parents=True, exist_ok=True)
        df = generate_manual("social", "web", [], 15)
        df.to_csv(social_path, index=False)
        print(f"Generated social sample: {len(df)} rows")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
