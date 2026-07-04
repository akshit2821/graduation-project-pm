#!/usr/bin/env python3
"""Part 1 orchestrator: collect -> normalize -> classify -> artifacts."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

PART1 = Path(__file__).resolve().parent
PROJECT = PART1.parent
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "part-1-ingest"))
sys.path.insert(0, str(PROJECT / "part-1-analysis"))

from aggregate import (  # noqa: E402
    build_research_answers,
    build_source_breakdown,
    build_theme_map,
    select_quotes,
    select_research_quotes,
    write_insight_report,
)
from classify import classify_all  # noqa: E402
from lib.review_sample import load_sample_config, select_llm_review_ids  # noqa: E402
from normalize import normalize_all  # noqa: E402


def _run_script(rel: str) -> None:
    path = PROJECT / rel
    r = subprocess.run([sys.executable, str(path)], cwd=str(PROJECT))
    if r.returncode != 0:
        print(f"WARN: {rel} exited {r.returncode}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Part 1 — Review Discovery Engine")
    parser.add_argument("--config", type=Path, default=PROJECT / "config" / "product.json")
    parser.add_argument("--skip-scrape", action="store_true")
    parser.add_argument("--use-groq", action="store_true")
    parser.add_argument("--batch-size", type=int, default=25)
    args = parser.parse_args()

    # Part 0 gate
    p0 = subprocess.run([sys.executable, str(PROJECT / "part-0" / "run_part0.py")], cwd=str(PROJECT))
    if p0.returncode != 0:
        print("FAIL: Part 0 checks did not pass")
        return 1

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    slug = cfg["product_slug"]
    raw_dir = PROJECT / "data" / "raw" / slug

    if not args.skip_scrape:
        print("1A Collect — Play Store...")
        _run_script("part-1-ingest/scrape_play.py")
        print("1A Collect — App Store (optional)...")
        _run_script("part-1-ingest/scrape_ios.py")
        print("1A Sample data for reddit/forum/social if missing...")
        _run_script("part-1-ingest/generate_sample_data.py")

    print("1B Normalize...")
    df, ingest_stats = normalize_all(cfg, raw_dir)
    out_csv = PROJECT / "data" / "feedback_normalized.csv"
    df.to_csv(out_csv, index=False)
    ingest_path = PROJECT / "artifacts" / "ingest_report.json"
    ingest_path.write_text(json.dumps(ingest_stats, indent=2, default=str), encoding="utf-8")
    print(f"  {len(df)} normalized rows")

    if len(df) < 100:
        print(f"FAIL: corpus too small ({len(df)} rows); need >= 100")
        return 1

    sample_enabled, max_r, min_r = load_sample_config(cfg)
    llm_ids = None
    sample_meta = {"sampled": False}
    if sample_enabled:
        llm_ids, sample_meta = select_llm_review_ids(df, max_reviews=max_r, min_reviews=min_r)
        if sample_meta.get("sampled"):
            print(f"  LLM sample: {sample_meta['llm_review_count']} groq + {sample_meta['keyword_review_count']} keyword")

    print("1C Classify themes...")
    assignments, cls_meta = classify_all(
        df, batch_size=args.batch_size, force_api=args.use_groq, llm_ids=llm_ids
    )

    artifacts = PROJECT / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    assignments.to_csv(artifacts / "feedback_theme_assignments.csv", index=False)

    theme_map = build_theme_map(assignments, df, cfg, ingest_stats)
    theme_map["llm_provider"] = cls_meta.get("classifier")
    theme_map["llm_model"] = cls_meta.get("model")
    theme_map["llm_sample"] = sample_meta
    (artifacts / "theme_map.json").write_text(json.dumps(theme_map, indent=2), encoding="utf-8")

    source_breakdown = build_source_breakdown(df)
    (artifacts / "source_breakdown.json").write_text(json.dumps(source_breakdown, indent=2), encoding="utf-8")

    research = build_research_answers(assignments, df, theme_map, cfg)
    (artifacts / "research_answers.json").write_text(json.dumps(research, indent=2), encoding="utf-8")

    write_insight_report(research, source_breakdown, artifacts / "insight_report.md")

    quotes = select_quotes(df, assignments, theme_map.get("top3_theme_ids", [])[:3])
    research_quotes = select_research_quotes(df, assignments, research)
    (artifacts / "quote_bank.json").write_text(
        json.dumps({"quotes": quotes, "research_quotes": research_quotes}, indent=2),
        encoding="utf-8",
    )

    sources = set(df["source"].unique())
    coverage = theme_map.get("coverage_pct", 0)
    failures = []
    if len(sources) < 2:
        failures.append("COL4: fewer than 2 source types (warn)")
    if coverage < 80:
        failures.append(f"T4: coverage {coverage}% < 80%")
    if not (artifacts / "insight_report.md").is_file():
        failures.append("T8: insight_report missing")

    report = {
        "status": "pass" if not any("T4" in f or "T8" in f for f in failures) else "warn",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "feedback_count": len(df),
        "source_types": sorted(sources),
        "classification": cls_meta,
        "top3_theme_ids": theme_map.get("top3_theme_ids"),
        "coverage_pct": coverage,
        "failures": failures,
    }
    (artifacts / "part1_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    checkpoint = {
        "status": "pass" if report["status"] == "pass" else report["status"],
        "part0": "pass",
        "part1": report,
        "artifacts": [
            "data/feedback_normalized.csv",
            "artifacts/ingest_report.json",
            "artifacts/theme_map.json",
            "artifacts/source_breakdown.json",
            "artifacts/research_answers.json",
            "artifacts/insight_report.md",
            "artifacts/quote_bank.json",
            "artifacts/feedback_theme_assignments.csv",
        ],
        "next": "Deploy part-1-workflow/app.py to Streamlit Cloud",
    }
    (artifacts / "part1_checkpoint.json").write_text(json.dumps(checkpoint, indent=2), encoding="utf-8")

    print(f"Top 3 themes: {theme_map.get('top3_theme_ids')}")
    print(f"Coverage: {coverage}%")
    print(f"Sources: {sorted(sources)}")
    if failures:
        for f in failures:
            print(f"  NOTE: {f}")
    print(f"Part 1 {checkpoint['status'].upper()} -> artifacts/part1_checkpoint.json")
    return 0 if checkpoint["status"] in ("pass", "warn") else 1


if __name__ == "__main__":
    raise SystemExit(main())
