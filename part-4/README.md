# Part 4 — LoopBreak MVP

**Status:** Implemented — research-grounded AI coach with Groq + offline fallback.

---

## Run locally

```powershell
cd "E:\PM Fellowship\Project-cursor\Graduation-Project"
streamlit run part-4-mvp/app.py
```

Optional: check **Use Groq AI** if `Milestone 1/.env` has `LLM_API_KEY`. Without it, research fixtures still work.

## Verify

```powershell
python part-4/run_part4.py
```

## Deploy (Deliverable #3)

Streamlit Cloud → main file `part-4-mvp/app.py` · add `LLM_API_KEY` in secrets (optional).

**Prerequisite:** Part 3 PASS
