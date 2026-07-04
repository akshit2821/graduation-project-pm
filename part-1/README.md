# Part 1 — AI Review Discovery Engine

**Status:** Implemented

Multi-source ingest → normalize → Groq/keyword themes → artifacts + Streamlit workflow.

---

## Run

```powershell
cd "E:\PM Fellowship\Project-cursor\Graduation-Project"
pip install -r requirements.txt

# Full pipeline (scrape + sample + classify)
python part-1/run_part1.py --use-groq

# Skip live scrape (use existing/raw + samples)
python part-1/run_part1.py --skip-scrape --use-groq
```

## Workflow UI (local)

```powershell
streamlit run part-1-workflow/app.py
```

Production dashboard: themed UI, no internal IDs. Deploy to Streamlit Cloud for **Deliverable #1** — see [part-1-workflow/README.md](../part-1-workflow/README.md).

---

## Outputs

| Artifact | Purpose |
|----------|---------|
| `data/feedback_normalized.csv` | Unified corpus |
| `artifacts/theme_map.json` | Theme counts + top 3 |
| `artifacts/research_answers.json` | All 6 problem-statement research Q&A |
| `artifacts/quote_bank.json` | Verifiable quotes |
| `artifacts/source_breakdown.json` | By-source stats |
| `artifacts/part1_checkpoint.json` | Pass/fail gate |

**Prerequisite:** Part 0 PASS (`python part-0/run_part0.py`)

**Next:** Part 2 — user interviews
