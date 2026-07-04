#!/usr/bin/env python3
"""Scrape App Store reviews (optional; may return fewer rows for some regions)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

PROJECT = Path(__file__).resolve().parents[1]


def scrape_ios(app_id: str, country: str, count: int) -> pd.DataFrame:
    try:
        from app_store_scraper import AppStore
    except ImportError as e:
        raise RuntimeError("pip install app-store-scraper") from e

    app = AppStore(country=country, app_name="spotify", app_id=str(app_id))
    app.review(how_many=count)
    rows = []
    for r in app.reviews[:count]:
        rows.append(
            {
                "source": "app_store",
                "platform": "ios",
                "date": r.get("date"),
                "rating": r.get("rating"),
                "title": r.get("title") or "",
                "text": r.get("review") or "",
                "upvotes": 0,
                "url": "",
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=PROJECT / "config" / "product.json")
    parser.add_argument("--count", type=int, default=None)
    args = parser.parse_args()

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    ios = cfg["stores"]["ios"]
    target = args.count or cfg["data_sources"]["app_store"]["target_rows"]

    print(f"Scraping App Store: id={ios['app_id']} country={ios.get('country', 'in')}...")
    try:
        df = scrape_ios(ios["app_id"], ios.get("country", "in"), target)
    except Exception as e:
        print(f"WARN App Store scrape failed: {e}")
        return 1

    out_dir = PROJECT / "data" / "raw" / cfg["product_slug"] / "ios"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "ios_reviews.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
