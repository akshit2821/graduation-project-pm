#!/usr/bin/env python3
"""Combined gate: Parts 0–4."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent

PART_SCRIPTS = [
    ("part0", PROJECT / "part-0" / "run_part0.py"),
    ("part1", PROJECT / "part-1" / "run_part1.py", ["--skip-scrape"]),
    ("part2", PROJECT / "part-2" / "run_part2.py"),
    ("part3", PROJECT / "part-3" / "run_part3.py"),
    ("part4", PROJECT / "part-4" / "run_part4.py"),
]


def _run(script: Path, extra: list[str] | None = None) -> tuple[bool, str]:
    cmd = [sys.executable, str(script)] + (extra or [])
    r = subprocess.run(cmd, cwd=str(PROJECT), capture_output=True, text=True)
    tail = (r.stdout or r.stderr or "").strip().splitlines()
    return r.returncode == 0, tail[-1] if tail else f"exit {r.returncode}"


def main() -> int:
    results = {}
    all_ok = True
    for entry in PART_SCRIPTS:
        name, script = entry[0], entry[1]
        extra = entry[2] if len(entry) > 2 else None
        ok, summary = _run(script, extra) if script.is_file() else (False, "missing")
        results[name] = {"ok": ok, "summary": summary}
        all_ok &= ok

    cks = {}
    for i in range(5):
        p = PROJECT / "artifacts" / f"part{i}_checkpoint.json"
        if p.is_file():
            cks[f"part{i}"] = json.loads(p.read_text(encoding="utf-8"))

    combined = {
        "status": "pass" if all_ok else "fail",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parts": results,
        "submission_ready_except": [] if all_ok else ["fix failing gates"],
        "remaining_deliverables": [
            "Deploy part-1-workflow/app.py (workflow URL)",
            "Deploy part-4-mvp/app.py (MVP URL)",
            "10-slide deck NL Spotify.pdf",
        ],
        "summary": {
            "mvp": cks.get("part4", {}).get("mvp_name"),
            "problem_id": cks.get("part3", {}).get("problem_id"),
        },
    }
    out = PROJECT / "artifacts" / "pipeline_checkpoint_0_4.json"
    out.write_text(json.dumps(combined, indent=2), encoding="utf-8")

    print("=== Pipeline check (Parts 0–4) ===")
    for name, res in results.items():
        print(f"  {name}: {'PASS' if res['ok'] else 'FAIL'} — {res['summary']}")
    print(f"Combined: {'PASS' if all_ok else 'FAIL'}")
    if all_ok:
        print("Code complete — deploy both Streamlit apps + deck for submission")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
