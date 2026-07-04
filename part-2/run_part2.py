#!/usr/bin/env python3
"""Part 2 verification — interviews + validation matrix."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
RESEARCH = PROJECT / "part-2-research"
MIN_INTERVIEWS = 5
MIN_VALIDATED = 3

REQUIRED = [
    RESEARCH / "interview_guide.md",
    RESEARCH / "screener.md",
    RESEARCH / "interview_synthesis.md",
]

VALID_MARKERS = re.compile(r"\*\*(Y|Partial|N)\*\*", re.I)


def _count_interview_notes() -> int:
    notes_dir = RESEARCH / "notes"
    if not notes_dir.is_dir():
        return 0
    return len([p for p in notes_dir.glob("P*.md") if p.is_file()])


def _count_validated_themes(synthesis_text: str) -> dict:
    counts = {"Y": 0, "Partial": 0, "N": 0}
    for line in synthesis_text.splitlines():
        if "| `" not in line or "Validated?" not in synthesis_text:
            continue
        if not line.strip().startswith("| `"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        val = parts[2].replace("*", "").strip()
        if val in ("Y", "Yes"):
            counts["Y"] += 1
        elif val.lower() == "partial":
            counts["Partial"] += 1
        elif val in ("N", "No"):
            counts["N"] += 1
    validated = counts["Y"] + counts["Partial"]
    return {**counts, "validated_total": validated}


def _has_surprise(synthesis_text: str) -> bool:
    return "Surprise insight" in synthesis_text and "Decision fatigue" in synthesis_text


def main() -> int:
    failures: list[str] = []

    for p in REQUIRED:
        if not p.is_file():
            failures.append(f"Missing {p.relative_to(PROJECT)}")

    p1_ck = PROJECT / "artifacts" / "part1_checkpoint.json"
    if not p1_ck.is_file():
        failures.append("Part 1 checkpoint missing — run part-1/run_part1.py first")
    else:
        p1 = json.loads(p1_ck.read_text(encoding="utf-8"))
        if p1.get("status") not in ("pass", "warn"):
            failures.append("Part 1 not pass")

    n_notes = _count_interview_notes()
    if n_notes < MIN_INTERVIEWS:
        failures.append(f"R1: {n_notes} interview notes, need >={MIN_INTERVIEWS}")

    synthesis_path = RESEARCH / "interview_synthesis.md"
    synthesis_text = synthesis_path.read_text(encoding="utf-8") if synthesis_path.is_file() else ""
    val_counts = _count_validated_themes(synthesis_text)
    if val_counts.get("validated_total", 0) < MIN_VALIDATED:
        failures.append(
            f"V3: only {val_counts.get('validated_total', 0)} themes Y/Partial, need >={MIN_VALIDATED}"
        )

    if not _has_surprise(synthesis_text):
        failures.append("V5: surprise insight section missing or incomplete")

    if "Validation matrix" not in synthesis_text:
        failures.append("Validation matrix missing from interview_synthesis.md")

    out = PROJECT / "artifacts" / "part2_checkpoint.json"
    payload = {
        "status": "pass" if not failures else "fail",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "interview_count": n_notes,
        "validation_counts": val_counts,
        "surprise_documented": _has_surprise(synthesis_text),
        "checks": {
            "min_interviews": n_notes >= MIN_INTERVIEWS,
            "min_validated_themes": val_counts.get("validated_total", 0) >= MIN_VALIDATED,
            "part1_prerequisite": p1_ck.is_file(),
        },
        "failures": failures,
        "next": "Part 3 — problem_statement.md + mvp_scope.json",
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if failures:
        print("Part 2 FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("Part 2 PASS")
    print(f"  Interviews: {n_notes}")
    print(f"  Themes validated (Y+Partial): {val_counts.get('validated_total')}")
    print(f"  Checkpoint: {out.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
