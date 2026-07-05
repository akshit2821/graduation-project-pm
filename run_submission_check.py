#!/usr/bin/env python3
"""Final submission gate — Parts 0-4 + deck + config."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
SUB = PROJECT / "config" / "submission.json"
MAX_PDF_MB = 40

# Read deck filename from config
deck_filename = "Spotify.pdf"
if SUB.is_file():
    sub_data = json.loads(SUB.read_text(encoding="utf-8"))
    deck_filename = sub_data.get("deck_filename", "Spotify.pdf")
DECK = PROJECT / "deck" / deck_filename


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    r = subprocess.run([sys.executable, str(PROJECT / "run_check_parts_0_4.py")], cwd=str(PROJECT))
    if r.returncode != 0:
        failures.append("Parts 0-4 pipeline check failed")

    if not DECK.is_file():
        failures.append(f"Missing deck/{deck_filename} — run: python deck/build_deck.py")
    else:
        mb = DECK.stat().st_size / (1024 * 1024)
        if mb > MAX_PDF_MB:
            failures.append(f"Deck PDF {mb:.1f} MB exceeds {MAX_PDF_MB} MB")

    for path in (
        "Home.py",
        "pages/1_Review_Discovery_Engine.py",
        "pages/2_LoopBreak_MVP.py",
        "part-3-problem/problem_statement.md",
        "part-3-problem/mvp_scope.json",
    ):
        if not (PROJECT / path).is_file():
            failures.append(f"Missing {path}")

    urls = {}
    if SUB.is_file():
        urls = json.loads(SUB.read_text(encoding="utf-8"))
        for key in ("workflow_url", "mvp_url"):
            val = urls.get(key, "")
            if not val or str(val).startswith("REPLACE") or "YOUR_" in str(val):
                warnings.append(f"{key} not set — deploy Streamlit Cloud and update config/submission.json")
    else:
        failures.append("Missing config/submission.json")

    smoke = subprocess.run([sys.executable, str(PROJECT / "part-1" / "smoke_test_local.py")], cwd=str(PROJECT))
    if smoke.returncode != 0:
        warnings.append("Part 1 smoke test failed (non-blocking)")

    out = PROJECT / "artifacts" / "submission_checkpoint.json"
    payload = {
        "status": "pass" if not failures else "fail",
        "submission_ready": not failures and not warnings,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "deadline_ist": urls.get("deadline_ist"),
        "deck": str(DECK.relative_to(PROJECT)) if DECK.is_file() else None,
        "deck_size_kb": round(DECK.stat().st_size / 1024, 1) if DECK.is_file() else None,
        "urls": {k: urls.get(k) for k in ("workflow_url", "mvp_url", "unified_portal_url")},
        "failures": failures,
        "warnings": warnings,
        "submit_checklist": [
            "Update URLs in config/submission.json after deploy",
            "Re-run python deck/build_deck.py with live URLs",
            "Test links in incognito",
            f"Export/upload {deck_filename}",
            "Submit before 6 Jul 2026 3:59 PM IST",
        ],
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print("=== Submission check ===")
    for w in warnings:
        print(f"  WARN: {w}")
    for f in failures:
        print(f"  FAIL: {f}")
    if not failures:
        if warnings:
            print("  BUILD COMPLETE — set deploy URLs then re-build deck")
        else:
            print("  READY TO SUBMIT")
    print(f"  Checkpoint: {out.relative_to(PROJECT)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
