#!/usr/bin/env python3
"""Part 3 verification — problem statement + MVP scope."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
PROBLEM_DIR = PROJECT / "part-3-problem"

REQUIRED_MD = PROBLEM_DIR / "problem_statement.md"
REQUIRED_JSON = PROBLEM_DIR / "mvp_scope.json"

MD_SECTIONS = [
    "Problem (one sentence)",
    "Root cause",
    "Target segment",
    "Why solving this matters",
]

JSON_REQUIRED_KEYS = [
    "problem_id",
    "segment",
    "hypothesis",
    "success_metrics",
    "mvp_features_in",
    "grounding_artifacts",
]


def main() -> int:
    failures: list[str] = []

    for ck, name in [
        (PROJECT / "artifacts" / "part1_checkpoint.json", "Part 1"),
        (PROJECT / "artifacts" / "part2_checkpoint.json", "Part 2"),
    ]:
        if not ck.is_file():
            failures.append(f"{name} checkpoint missing")
        else:
            data = json.loads(ck.read_text(encoding="utf-8"))
            if data.get("status") not in ("pass", "warn"):
                failures.append(f"{name} not pass")

    if not REQUIRED_MD.is_file():
        failures.append("Missing part-3-problem/problem_statement.md")
    else:
        text = REQUIRED_MD.read_text(encoding="utf-8")
        for sec in MD_SECTIONS:
            if sec not in text:
                failures.append(f"problem_statement.md missing section: {sec}")
        if "decision fatigue" not in text.lower() and "transition" not in text.lower():
            failures.append("Problem must reference transition moment / decision fatigue (Part 2 insight)")
        if "Job-to-be-done" not in text and "job-to-be-done" not in text.lower():
            failures.append("Missing JTBD in problem_statement.md")

    scope = {}
    if not REQUIRED_JSON.is_file():
        failures.append("Missing part-3-problem/mvp_scope.json")
    else:
        scope = json.loads(REQUIRED_JSON.read_text(encoding="utf-8"))
        for key in JSON_REQUIRED_KEYS:
            if key not in scope:
                failures.append(f"mvp_scope.json missing key: {key}")
        if scope.get("problem_id") != "transition_moment_coach":
            failures.append("problem_id should be transition_moment_coach")
        metrics = scope.get("success_metrics", [])
        if not metrics or len(metrics) < 2:
            failures.append("Need at least 2 success_metrics in mvp_scope.json")

    out = PROJECT / "artifacts" / "part3_checkpoint.json"
    payload = {
        "status": "pass" if not failures else "fail",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "problem_id": scope.get("problem_id"),
        "mvp_name": scope.get("mvp_name"),
        "checks": {
            "part1_prerequisite": (PROJECT / "artifacts" / "part1_checkpoint.json").is_file(),
            "part2_prerequisite": (PROJECT / "artifacts" / "part2_checkpoint.json").is_file(),
            "problem_statement": REQUIRED_MD.is_file(),
            "mvp_scope": REQUIRED_JSON.is_file(),
        },
        "failures": failures,
        "next": "Part 4 — build and deploy part-4-mvp/app.py (LoopBreak)",
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if failures:
        print("Part 3 FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("Part 3 PASS")
    print(f"  Problem: {scope.get('problem_id')}")
    print(f"  MVP: {scope.get('mvp_name')}")
    print(f"  Checkpoint: {out.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
