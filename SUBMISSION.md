# Submission guide — 6 July 2026, 3:59 PM IST

## What you submit

| # | Deliverable | File / link |
|---|-------------|-------------|
| 1 | Review Analysis Workflow | `config/submission.json` → `workflow_url` |
| 2 | Thought process deck | `deck/NL Spotify.pdf` |
| 3 | AI MVP | `config/submission.json` → `mvp_url` |

---

## Step 1 — GitHub (required for Streamlit Cloud)

```powershell
cd "E:\PM Fellowship\Project-cursor\Graduation-Project"
git init
git add .
git commit -m "Graduation project: Spotify music discovery Parts 0-4"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

Ensure `artifacts/` is committed (needed for Review Engine dashboard).

---

## Step 2 — Streamlit Cloud deploy

1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
2. **Recommended (one URL, both deliverables):**
   - Repo: your GitHub repo
   - Branch: `main`
   - **Main file path:** `Home.py`
   - Pages: `pages/1_Review_Discovery_Engine.py`, `pages/2_LoopBreak_MVP.py`
3. **Optional secrets** (LoopBreak Groq): Settings → Secrets:

```toml
LLM_API_KEY = "your-groq-key"
```

4. Copy the `.streamlit.app` URL into `config/submission.json`:

```json
"unified_portal_url": "https://YOUR-APP.streamlit.app",
"workflow_url": "https://YOUR-APP.streamlit.app/Review_Discovery_Engine",
"mvp_url": "https://YOUR-APP.streamlit.app/LoopBreak_MVP"
```

*(Exact page URLs may vary — use sidebar page links from the deployed app.)*

**Alternative:** Deploy `part-1-workflow/app.py` and `part-4-mvp/app.py` as two separate Streamlit apps.

---

## Step 3 — Rebuild deck with live URLs

```powershell
python deck/build_deck.py
```

---

## Step 4 — Final verification

```powershell
python run_submission_check.py
python run_check_parts_0_4.py
```

Test every hyperlink in **incognito** before upload.

---

## Step 5 — Submit

Upload `deck/NL Spotify.pdf` per fellowship portal instructions. Include workflow + MVP links in the form or deck as required.

**Deck rules:** No fellow name · 10 slides max · title slide counts · min 14pt font · PDF < 40 MB · colour-blind-safe palette.

---

## Quick local preview

```powershell
streamlit run Home.py
python deck/build_deck.py
```
