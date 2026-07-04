# Deck — NL Spotify.pdf

**Deliverable #2:** 10-slide thought process deck (PDF, max 10 slides, no fellow name).

## Generate / refresh

```powershell
python deck/build_deck.py
```

Reads live stats from `artifacts/theme_map.json` and URLs from `config/submission.json`.

**After deploying Streamlit:** update URLs in `config/submission.json`, then re-run `build_deck.py` so slides 3 and 8 show real links.

## Output

- `deck/NL Spotify.pdf` (landscape A4, colour-blind-safe dark theme, 15pt+ body text)

## Optional

Rebuild in Google Slides using content in [ROADMAP.md](../ROADMAP.md) § 10-Slide Deck Outline, then export as `NL Spotify.pdf`.
