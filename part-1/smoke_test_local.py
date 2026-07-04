#!/usr/bin/env python3
"""Quick local smoke test for Part 1 artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ART = PROJECT / "artifacts"


def main() -> int:
    checks: list[tuple[str, bool]] = []

    p1_path = ART / "part1_checkpoint.json"
    checks.append(("part1_checkpoint exists", p1_path.is_file()))
    p1 = json.loads(p1_path.read_text(encoding="utf-8"))
    checks.append(("Part 1 status pass", p1.get("status") == "pass"))

    ra_path = ART / "research_answers.json"
    checks.append(("research_answers.json exists", ra_path.is_file()))
    ra = json.loads(ra_path.read_text(encoding="utf-8"))
    checks.append(("6 research questions", len(ra.get("questions", [])) == 6))
    checks.append(("corpus >= 100", ra.get("corpus_size", 0) >= 100))

    by_id = {q["id"]: q for q in ra.get("questions", [])}
    for qid in ("q1_discovery_struggle", "q2_reco_frustration", "q3_listening_behavior", "q4_repeat_causes"):
        checks.append((f"{qid} has themes", len(by_id.get(qid, {}).get("themes", [])) >= 2))
    checks.append(("Q5 segment slices", len(by_id.get("q5_segment_diff", {}).get("segments", [])) >= 3))
    checks.append(("Q6 cross-source needs", len(by_id.get("q6_unmet_needs", {}).get("cross_source_needs", [])) >= 1))

    qb = json.loads((ART / "quote_bank.json").read_text(encoding="utf-8"))
    checks.append(("theme quotes", len(qb.get("quotes", [])) >= 3))
    checks.append(("research quotes", len(qb.get("research_quotes", [])) >= 4))

    # App imports
    sys.path.insert(0, str(PROJECT / "part-1-workflow"))
    try:
        import app as workflow_app  # noqa: F401

        checks.append(("Streamlit app imports", True))
    except Exception:
        checks.append(("Streamlit app imports", False))

    print("=== Local smoke test ===")
    failed = []
    for name, ok in checks:
        mark = "PASS" if ok else "FAIL"
        print(f"  {mark}: {name}")
        if not ok:
            failed.append(name)
    print(f"Overall: {'PASS' if not failed else 'FAIL'}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
