# Review Discovery Engine — Public dashboard

Production-facing Streamlit app for **Deliverable #1** (workflow link in deck).

## Local run

```powershell
cd "E:\PM Fellowship\Project-cursor\Graduation-Project"
python part-1/run_part1.py --skip-scrape --use-groq
streamlit run part-1-workflow/app.py
```

Open **http://localhost:8501**

## Streamlit Cloud deploy

1. Push repo to GitHub (include `artifacts/` from a successful Part 1 run).
2. [share.streamlit.io](https://share.streamlit.io) → New app.
3. **Main file path:** `part-1-workflow/app.py`
4. **Working directory:** repository root (`Graduation-Project/`).
5. Python 3.10+; dependencies from root `requirements.txt`.

No API keys required — the dashboard reads pre-built artifacts only.

## What reviewers see

| Tab | Content |
|-----|---------|
| Overview | Top findings, pipeline summary, target segment |
| Research answers | **All 6 problem-statement questions** with multi-theme stats |
| Themes | Ranked discovery themes with share bars |
| User voices | Verifiable quotes with channel badges |
| Sources | Channel mix and leading theme per source |

Internal pipeline IDs, LLM config, and dev run instructions are **not** shown in the UI.
