#!/usr/bin/env python3
"""Combined gate: Part 0 + Part 1 + Part 2 + Part 3."""

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
]


def _run(name: str, script: Path, extra: list[str] | None = None) -> tuple[bool, str]:
    cmd = [sys.executable, str(script)] + (extra or [])
    r = subprocess.run(cmd, cwd=str(PROJECT), capture_output=True, text=True)
    ok = r.returncode == 0
    tail = (r.stdout or r.stderr or "").strip().splitlines()
    summary = tail[-1] if tail else f"exit {r.returncode}"
    return ok, summary


def main() -> int:
    results: dict[str, dict] = {}
    all_ok = True

    for entry in PART_SCRIPTS:
        name, script = entry[0], entry[1]
        extra = entry[2] if len(entry) > 2 else None
        if not script.is_file():
            results[name] = {"ok": False, "error": "script missing"}
            all_ok = False
            continue
        ok, summary = _run(name, script, extra)
        results[name] = {"ok": ok, "summary": summary}
        all_ok = all_ok and ok

    ck_files = {
        "part0": PROJECT / "artifacts" / "part0_checkpoint.json",
        "part1": PROJECT / "artifacts" / "part1_checkpoint.json",
        "part2": PROJECT / "artifacts" / "part2_checkpoint.json",
        "part3": PROJECT / "artifacts" / "part3_checkpoint.json",
    }
    checkpoints = {}
    for k, p in ck_files.items():
        if p.is_file():
            checkpoints[k] = json.loads(p.read_text(encoding="utf-8"))

    combined = {
        "status": "pass" if all_ok else "fail",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parts": results,
        "checkpoints": {k: v.get("status") for k, v in checkpoints.items()},
        "pipeline_ready_for_part4": all_ok,
        "summary": {
            "product": checkpoints.get("part0", {}).get("product"),
            "feedback_count": checkpoints.get("part1", {}).get("part1", {}).get("feedback_count"),
            "interviews": checkpoints.get("part2", {}).get("interview_count"),
            "problem_id": checkpoints.get("part3", {}).get("problem_id"),
            "mvp_name": checkpoints.get("part3", {}).get("mvp_name"),
        },
    }

    out = PROJECT / "artifacts" / "pipeline_checkpoint_0_3.json"
    out.write_text(json.dumps(combined, indent=2), encoding="utf-8")

    print("=== Pipeline check (Parts 0–3) ===")
    for name, res in results.items():
        mark = "PASS" if res.get("ok") else "FAIL"
        print(f"  {name}: {mark} — {res.get('summary', res.get('error'))}")
    print(f"Combined: {'PASS' if all_ok else 'FAIL'} -> {out.relative_to(PROJECT)}")
    if all_ok:
        print("Ready for Part 4 (LoopBreak MVP)")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
