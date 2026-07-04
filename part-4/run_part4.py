#!/usr/bin/env python3
"""Part 4 verification — LoopBreak MVP."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
MVP = PROJECT / "part-4-mvp"


def main() -> int:
    failures: list[str] = []

    p3 = PROJECT / "artifacts" / "part3_checkpoint.json"
    if not p3.is_file():
        failures.append("Part 3 checkpoint missing")
    else:
        data = json.loads(p3.read_text(encoding="utf-8"))
        if data.get("status") != "pass":
            failures.append("Part 3 not pass")

    for rel in (
        "part-4-mvp/app.py",
        "part-4-mvp/coach.py",
        "part-4-mvp/prompts/system.md",
        "part-4-mvp/fixtures/sample_responses.json",
        "part-3-problem/mvp_scope.json",
    ):
        if not (PROJECT / rel).is_file():
            failures.append(f"Missing {rel}")

    sys.path.insert(0, str(MVP))
    sys.path.insert(0, str(PROJECT))
    try:
        from coach import generate_coach_response, load_research_context  # noqa: E402

        ctx = load_research_context()
        if len(ctx) < 200:
            failures.append("Research grounding context too short")
        sample = generate_coach_response("", persona_id="post_work")
        if not sample.get("why_looping") or len(sample.get("discovery_paths", [])) < 3:
            failures.append("Fallback coach response invalid")
    except Exception as e:
        failures.append(f"Coach module error: {e}")

    scope = json.loads((PROJECT / "part-3-problem" / "mvp_scope.json").read_text(encoding="utf-8"))

    out = PROJECT / "artifacts" / "part4_checkpoint.json"
    payload = {
        "status": "pass" if not failures else "fail",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mvp_name": scope.get("mvp_name"),
        "entrypoint": "part-4-mvp/app.py",
        "checks": {
            "part3_prerequisite": p3.is_file(),
            "app_exists": (MVP / "app.py").is_file(),
            "fallback_fixtures": (MVP / "fixtures" / "sample_responses.json").is_file(),
        },
        "failures": failures,
        "next": "Deploy part-4-mvp/app.py to Streamlit Cloud (Deliverable #3)",
    }
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if failures:
        print("Part 4 FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("Part 4 PASS")
    print(f"  MVP: {scope.get('mvp_name')}")
    print(f"  Local: streamlit run part-4-mvp/app.py")
    print(f"  Checkpoint: {out.relative_to(PROJECT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
