#!/usr/bin/env python3
"""Scrape Google Play reviews for configured Android package."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]


def scrape_play(package: str, count: int, lang: str = "en", country: str = "in") -> pd.DataFrame:
    from google_play_scraper import Sort, reviews

    batch, token = reviews(
        package,
        lang=lang,
        country=country,
        sort=Sort.NEWEST,
        count=min(count, 200),
    )
    rows = batch
    while token and len(rows) < count:
        need = min(200, count - len(rows))
        batch, token = reviews(
            package,
            lang=lang,
            country=country,
            sort=Sort.NEWEST,
            count=need,
            continuation_token=token,
        )
        rows.extend(batch)

    out = []
    for r in rows[:count]:
        out.append(
            {
                "source": "play_store",
                "platform": "android",
                "date": r.get("at"),
                "rating": r.get("score"),
                "title": "",
                "text": r.get("content") or "",
                "upvotes": r.get("thumbsUpCount", 0),
                "url": "",
            }
        )
    return pd.DataFrame(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=PROJECT / "config" / "product.json")
    parser.add_argument("--count", type=int, default=None)
    args = parser.parse_args()

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    package = cfg["stores"]["android"]["package"]
    target = args.count or cfg["data_sources"]["play_store"]["target_rows"]

    print(f"Scraping Play Store: {package} (target={target})...")
    df = scrape_play(package, target)
    out_dir = PROJECT / "data" / "raw" / cfg["product_slug"] / "play"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "play_reviews.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
