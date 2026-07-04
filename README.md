# Graduation Project — Music Discovery (Submission)

**Official problem:** Growth PM at Spotify — increase meaningful discovery, reduce repetitive listening.

**Deadline:** 6 July 2026, 3:59 PM IST

---

## Status

| Part | Status | Command |
|------|--------|---------|
| 0–4 | **Done** | `python run_check_parts_0_4.py` |
| Deck PDF | **Done** | `deck/NL Spotify.pdf` |
| Live URLs | **You deploy** | See [SUBMISSION.md](./SUBMISSION.md) |

---

## Submit

1. Deploy **`Home.py`** to Streamlit Cloud → update [config/submission.json](./config/submission.json)
2. Run `python deck/build_deck.py` (embeds URLs)
3. Run `python run_submission_check.py`
4. Upload **`deck/NL Spotify.pdf`**

Full steps: **[SUBMISSION.md](./SUBMISSION.md)**

---

## Local preview

```powershell
pip install -r requirements.txt
streamlit run Home.py
```

Sidebar: Review Discovery Engine · LoopBreak MVP

---

## Docs

| Document | Purpose |
|----------|---------|
| [problem.md](./problem.md) | Official Parts 1–4 |
| [architecture.md](./architecture.md) | System design |
| [ROADMAP.md](./ROADMAP.md) | Timeline + deck outline |
| [SUBMISSION.md](./SUBMISSION.md) | Deploy + submit checklist |

**Do not submit** [SLIDE_DECK.md](./SLIDE_DECK.md) (legacy Groww deck).
