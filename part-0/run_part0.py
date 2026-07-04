#!/usr/bin/env python3
"""Part 0 verification — product lock, docs, config, edge-case gates."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PART0 = Path(__file__).resolve().parent
PROJECT = PART0.parent

REQUIRED_FILES = [
    PROJECT / "config" / "product.json",
    PROJECT / "docs" / "PII_POLICY.md",
    PROJECT / "docs" / "THEME_GUIDE.md",
    PROJECT / "docs" / "DATA_SOURCES.md",
    PART0 / "SCOPE.md",
    PART0 / "KNOWN_LIMITATIONS.md",
    PROJECT / "lib" / "llm_client.py",
    PROJECT / "lib" / "review_sample.py",
    PROJECT / ".gitignore",
    PROJECT / "requirements.txt",
]

VALID_THEMES = {
    "discovery_friction",
    "bad_recommendations",
    "repeat_listening",
    "library_clutter",
    "ui_complexity",
    "social_discovery",
    "podcast_vs_music",
    "pricing_ads",
}

SPOTIFY_ANDROID = "com.spotify.music"
GAANA_ANDROID = "com.gaana.android"


def _check_gitignore() -> list[str]:
    failures = []
    gi = PROJECT / ".gitignore"
    text = gi.read_text(encoding="utf-8")
    for needle in (".env", "token.json", "credentials.json"):
        if needle not in text:
            failures.append(f"C3: .gitignore missing {needle}")
    return failures


def _check_no_secrets_in_repo() -> list[str]:
    failures = []
    pattern = re.compile(r"sk-[a-zA-Z0-9]{20,}|GOCSPX-[a-zA-Z0-9_-]+")
    for path in PROJECT.rglob("*"):
        if not path.is_file():
            continue
        if ".venv" in path.parts or path.suffix in {".pyc", ".pdf"}:
            continue
        if path.name in {".gitignore", "run_part0.py"}:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if pattern.search(content):
            failures.append(f"Secret-like pattern in {path.relative_to(PROJECT)}")
    return failures


def _validate_config(cfg: dict) -> list[str]:
    failures = []
    name = (cfg.get("product_name") or "").strip()
    slug = (cfg.get("product_slug") or "").strip()
    if not name or not slug:
        failures.append("S1: product_name and product_slug required")

    if slug not in ("spotify", "gaana"):
        failures.append(f"S1: product_slug must be spotify or gaana, got {slug!r}")

    segment = cfg.get("target_segment") or {}
    if not (segment.get("description") or "").strip():
        failures.append("S4: target_segment.description required")

    themes = cfg.get("theme_seed_ids") or []
    if not themes:
        failures.append("C1: theme_seed_ids empty")
    if len(themes) > 8:
        failures.append(f"C1: theme_seed_ids max 8, got {len(themes)}")
    invalid = set(themes) - VALID_THEMES
    if invalid:
        failures.append(f"C1: invalid theme ids: {sorted(invalid)}")

    android_pkg = (cfg.get("stores") or {}).get("android", {}).get("package", "")
    if slug == "spotify" and android_pkg != SPOTIFY_ANDROID:
        failures.append(f"S3: Spotify android package must be {SPOTIFY_ANDROID}")
    if slug == "gaana" and android_pkg != GAANA_ANDROID:
        if slug == "gaana":
            failures.append(f"S3: Gaana android package must be {GAANA_ANDROID}")

    sample = cfg.get("llm_review_sample") or {}
    max_r = int(sample.get("max_reviews", 400))
    min_r = int(sample.get("min_reviews", 300))
    if not (300 <= max_r <= 500):
        failures.append(f"llm_review_sample.max_reviews must be 300-500, got {max_r}")
    if min_r > max_r:
        failures.append("llm_review_sample.min_reviews > max_reviews")

    if not cfg.get("deck_filename"):
        failures.append("deck_filename missing (e.g. NL Spotify.pdf)")

    return failures


def main() -> int:
    failures: list[str] = []

    missing = [p for p in REQUIRED_FILES if not p.is_file()]
    for p in missing:
        failures.append(f"Missing file: {p.relative_to(PROJECT)}")

    for sub in (
        PROJECT / "data" / "raw" / "spotify",
        PROJECT / "artifacts",
        PROJECT / "decisions",
    ):
        if not sub.is_dir():
            failures.append(f"Missing directory: {sub.relative_to(PROJECT)}")

    cfg_path = PROJECT / "config" / "product.json"
    cfg = {}
    if cfg_path.is_file():
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            failures.extend(_validate_config(cfg))
        except json.JSONDecodeError as e:
            failures.append(f"Invalid product.json: {e}")

    if (PROJECT / ".gitignore").is_file():
        failures.extend(_check_gitignore())

    failures.extend(_check_no_secrets_in_repo())

    # Groq env optional at Part 0 (C2)
    sys.path.insert(0, str(PROJECT))
    groq_status = "unknown"
    try:
        from lib.llm_client import api_enabled, env_file_path, get_llm_api_key

        env_path = env_file_path()
        if not env_path.is_file():
            groq_status = "env_file_missing"
        elif not get_llm_api_key():
            groq_status = "no_api_key"
        elif api_enabled():
            groq_status = "ready"
        else:
            groq_status = "deterministic_mode"
    except Exception as e:
        groq_status = f"error:{e}"

    out = PROJECT / "artifacts" / "part0_checkpoint.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": "pass" if not failures else "fail",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "product": cfg.get("product_name"),
        "product_slug": cfg.get("product_slug"),
        "segment_locked": bool((cfg.get("target_segment") or {}).get("description")),
        "theme_count": len(cfg.get("theme_seed_ids") or []),
        "groq_status": groq_status,
        "checks": {
            "files_present": not missing,
            "config_valid": not any(f.startswith(("S", "C1", "S3", "S4")) for f in failures),
            "gitignore_secrets": not any(f.startswith("C3") for f in failures),
            "no_committed_secrets": not any("Secret-like" in f for f in failures),
        },
        "failures": failures,
        "next": "Part 1A — scrape Play Store (part-1-ingest/scrape_play.py)",
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if failures:
        print("Part 0 FAIL")
        for f in failures:
            print(f"  - {f}")
        print(f"Wrote {out.relative_to(PROJECT)}")
        return 1

    print("Part 0 PASS")
    print(f"  Product: {cfg.get('product_name')} ({cfg.get('product_slug')})")
    print(f"  Themes: {len(cfg.get('theme_seed_ids', []))}")
    print(f"  Groq: {groq_status}")
    print(f"  Checkpoint: {out.relative_to(PROJECT)}")
    print("Next: Part 1 — multi-source collection (see docs/DATA_SOURCES.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
