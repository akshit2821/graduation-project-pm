#!/usr/bin/env python3
"""Cross-check project against architecture, problem.md, edge-cases, ROADMAP."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent


def main() -> int:
    rows: list[tuple[str, str, str, str]] = []  # area, check, status, detail

    def add(area: str, check: str, ok: bool, detail: str, warn: bool = False) -> None:
        if ok:
            st = "PASS"
        elif warn:
            st = "WARN"
        else:
            st = "GAP"
        rows.append((area, check, st, detail))

    # Automated gates
    for script in ("run_check_parts_0_4.py", "run_submission_check.py", "part-1/smoke_test_local.py"):
        r = subprocess.run([sys.executable, str(PROJECT / script)], cwd=str(PROJECT), capture_output=True)
        add("Gates", script, r.returncode == 0, f"exit {r.returncode}")

    # Architecture artifacts
    arch = [
        "artifacts/theme_map.json",
        "artifacts/insight_report.md",
        "artifacts/research_answers.json",
        "artifacts/quote_bank.json",
        "part-2-research/interview_synthesis.md",
        "part-3-problem/problem_statement.md",
        "part-3-problem/mvp_scope.json",
        "part-1-workflow/app.py",
        "part-4-mvp/app.py",
        "part-4-mvp/coach.py",
        "Home.py",
        "deck/NL Spotify.pdf",
    ]
    for f in arch:
        add("Architecture", f, (PROJECT / f).is_file(), "present" if (PROJECT / f).is_file() else "missing")

    # problem.md Part 1 - 6 questions
    ra = json.loads((PROJECT / "artifacts/research_answers.json").read_text(encoding="utf-8"))
    add("problem.md P1", "6 research questions", len(ra.get("questions", [])) == 6, str(len(ra.get("questions", []))))

    # Sources
    sb = json.loads((PROJECT / "artifacts/source_breakdown.json").read_text(encoding="utf-8"))
    n_src = len(sb.get("sources", {}))
    add("problem.md P1", "Multi-source corpus", n_src >= 4, f"{n_src} types: {list(sb['sources'].keys())}")
    add("edge-cases COL2", "App Store reviews", "app_store" in sb.get("sources", {}), "not collected", warn=True)

    # Part 2
    p2 = json.loads((PROJECT / "artifacts/part2_checkpoint.json").read_text(encoding="utf-8"))
    add("problem.md P2", "5-6 interviews", p2.get("interview_count", 0) >= 5, f"n={p2.get('interview_count')}")
    add("edge-cases R5", "Real interviews (not demo)", False, "demo notes — disclose in deck", warn=True)

    # Part 3
    ps = (PROJECT / "part-3-problem/problem_statement.md").read_text(encoding="utf-8")
    add("problem.md P3", "Root cause + segment + business", all(x in ps for x in ("Root cause", "Target segment", "business")), "sections present")

    # Part 4
    sys.path.insert(0, str(PROJECT / "part-4-mvp"))
    try:
        from coach import generate_coach_response  # noqa: E402

        r = generate_coach_response("", persona_id="post_work")
        add("problem.md P4", "LoopBreak 3 paths + action", len(r.get("discovery_paths", [])) >= 3, "coach OK")
    except Exception as e:
        add("problem.md P4", "LoopBreak coach", False, str(e))

    # Deliverables
    sub = json.loads((PROJECT / "config/submission.json").read_text(encoding="utf-8"))
    wf = sub.get("workflow_url", "")
    add("ROADMAP DEL", "Public workflow URL", not str(wf).startswith("REPLACE"), wf or "not deployed", warn=True)
    mvp = sub.get("mvp_url", "")
    add("ROADMAP DEL", "Public MVP URL", not str(mvp).startswith("REPLACE"), mvp or "not deployed", warn=True)

    pdf = PROJECT / "deck" / "NL Spotify.pdf"
    if pdf.is_file():
        kb = pdf.stat().st_size / 1024
        add("ROADMAP DEL", "NL Spotify.pdf", True, f"{kb:.1f} KB")
        try:
            from pypdf import PdfReader

            pages = len(PdfReader(str(pdf)).pages)
            add("ROADMAP DEL", "Deck 10 slides", pages == 10, f"{pages} pages")
        except ImportError:
            add("ROADMAP DEL", "Deck page count", True, "install pypdf to verify", warn=True)
    else:
        add("ROADMAP DEL", "NL Spotify.pdf", False, "missing")

    # Config lock
    cfg = json.loads((PROJECT / "config/product.json").read_text(encoding="utf-8"))
    add("edge-cases S1", "Spotify product lock", cfg.get("product_slug") == "spotify", cfg.get("product_name", ""))
    add("edge-cases S4", "Segment defined", bool(cfg.get("target_segment")), "target_segment in config")

    # Presentation readiness
    blockers = [r for r in rows if r[2] == "GAP"]
    warns = [r for r in rows if r[2] == "WARN"]

    print("=" * 72)
    print("GRADUATION PROJECT CROSS-CHECK")
    print("Refs: architecture.md | edge-cases.md | problem.md | ROADMAP.md")
    print("=" * 72)
    cur = ""
    for area, check, status, detail in rows:
        if area != cur:
            print(f"\n[{area}]")
            cur = area
        print(f"  {status:4}  {check}: {detail}")

    print("\n" + "=" * 72)
    print(f"BLOCKERS (GAP): {len(blockers)}")
    print(f"WARNINGS:       {len(warns)}")
    if not blockers:
        print("PRESENTATION:   READY locally (demo + deck PDF)")
        print("SUBMISSION:     Pending Streamlit deploy + URL update in deck")
    else:
        print("PRESENTATION:   Fix GAP items first")
    print("=" * 72)

    out = PROJECT / "artifacts" / "cross_check_report.json"
    out.write_text(
        json.dumps({"blockers": blockers, "warnings": warns, "rows": rows}, indent=2),
        encoding="utf-8",
    )
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
