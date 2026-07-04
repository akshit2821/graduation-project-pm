#!/usr/bin/env python3
"""Merge multi-source raw feedback into feedback_normalized.csv."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from text_normalize import normalize_review_text, passes_text_filters

PROJECT = Path(__file__).resolve().parents[1]


def assign_feedback_id(source: str, date_val, text: str) -> str:
    key = f"{source}|{date_val}|{(text or '')[:120]}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def load_csv_paths(raw_dir: Path) -> list[Path]:
    paths = []
    for p in sorted(raw_dir.glob("**/*.csv")):
        if p.name.startswith("_TEMPLATE"):
            continue
        paths.append(p.resolve())
    return paths


def normalize_frame(df: pd.DataFrame, filters: dict) -> tuple[pd.DataFrame, dict]:
    stats = {
        "rows_in": len(df),
        "dropped_missing_text": 0,
        "dropped_emoji": 0,
        "dropped_non_english": 0,
        "dropped_empty_after_normalize": 0,
        "dropped_duplicate": 0,
    }

    required = {"source", "text", "date"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = df.copy()
    df["title"] = df["title"].fillna("") if "title" in df.columns else ""
    df["platform"] = df.get("platform", pd.Series(["web"] * len(df)))
    df["rating"] = df["rating"] if "rating" in df.columns else pd.NA
    df["upvotes"] = df.get("upvotes", 0)
    df["url"] = df.get("url", "")

    df["date"] = pd.to_datetime(df["date"], errors="coerce", utc=True, format="mixed").dt.date
    df = df.dropna(subset=["date"])

    kept = []
    for _, row in df.iterrows():
        title = str(row.get("title") or "")
        text = str(row.get("text") or "")
        ok, reason = passes_text_filters(
            title,
            text,
            english_only=filters.get("english_only", True),
            allow_emojis=filters.get("allow_emojis", False),
            min_english_ratio=filters.get("min_english_ratio", 0.85),
        )
        if not ok:
            if reason == "emoji":
                stats["dropped_emoji"] += 1
            elif reason == "non_english":
                stats["dropped_non_english"] += 1
            else:
                stats["dropped_empty_after_normalize"] += 1
            continue
        text_n = normalize_review_text(text)
        title_n = normalize_review_text(title)
        fid = assign_feedback_id(str(row["source"]), row["date"], text_n)
        kept.append(
            {
                "feedback_id": fid,
                "source": row["source"],
                "platform": row.get("platform", "web"),
                "date": row["date"],
                "rating": row.get("rating"),
                "title": title_n,
                "text": text_n,
                "upvotes": row.get("upvotes", 0),
                "url": row.get("url", ""),
                "language": "en",
            }
        )

    out = pd.DataFrame(kept)
    before = len(out)
    out = out.drop_duplicates(subset=["feedback_id"], keep="first")
    stats["dropped_duplicate"] = int(before - len(out))
    stats["rows_out"] = len(out)
    return out, stats


def normalize_all(cfg: dict, raw_dir: Path) -> tuple[pd.DataFrame, dict]:
    paths = load_csv_paths(raw_dir)
    if not paths:
        raise FileNotFoundError(f"No CSV files under {raw_dir}")

    frames = [pd.read_csv(p) for p in paths]
    combined = pd.concat(frames, ignore_index=True)
    filters = cfg.get("feedback_filters", {})
    df, stats = normalize_frame(combined, filters)

    stats["source_files"] = [str(p.resolve().relative_to(PROJECT.resolve())) for p in paths]
    stats["source_breakdown_in"] = combined["source"].value_counts().to_dict() if "source" in combined.columns else {}
    stats["date_min"] = str(df["date"].min()) if len(df) else None
    stats["date_max"] = str(df["date"].max()) if len(df) else None
    stats["text_filters"] = filters
    return df, stats


def main() -> int:
    cfg = json.loads((PROJECT / "config" / "product.json").read_text(encoding="utf-8"))
    raw_dir = PROJECT / "data" / "raw" / cfg["product_slug"]
    df, stats = normalize_all(cfg, raw_dir)

    out_csv = PROJECT / "data" / "feedback_normalized.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)

    report_path = PROJECT / "artifacts" / "ingest_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(stats, indent=2, default=str), encoding="utf-8")

    print(f"Normalized {stats['rows_out']} rows -> {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
