# Part 0 — Product lock and setup

**Status:** Implemented — run verifier before Part 1.

Locks **Spotify**, target segment, 8 discovery themes, data-source plan, and repo hygiene.

---

## Artifacts

| File | Purpose |
|------|---------|
| [../config/product.json](../config/product.json) | Product, segment, store IDs, themes, LLM cap |
| [SCOPE.md](./SCOPE.md) | In/out of scope |
| [KNOWN_LIMITATIONS.md](./KNOWN_LIMITATIONS.md) | Documented gaps |
| [../docs/PII_POLICY.md](../docs/PII_POLICY.md) | Privacy rules |
| [../docs/THEME_GUIDE.md](../docs/THEME_GUIDE.md) | 8 theme legend |
| [../docs/DATA_SOURCES.md](../docs/DATA_SOURCES.md) | Part 1 collection plan |
| [../lib/llm_client.py](../lib/llm_client.py) | Groq client (Milestone 1 `.env`) |
| [../artifacts/part0_checkpoint.json](../artifacts/part0_checkpoint.json) | Verifier output |

---

## Run

```powershell
cd "E:\PM Fellowship\Project-cursor\Graduation-Project"
python part-0/run_part0.py
```

**Pass criteria (edge-cases S1–S5, C1–C3):**

- [x] Single product in `product.json` (Spotify)  
- [x] `target_segment.description` filled  
- [x] 8 valid `theme_seed_ids`  
- [x] Android package `com.spotify.music`  
- [x] `.gitignore` covers `.env`, tokens  
- [x] Required docs present  

Groq env optional at Part 0 (**C2**); warning only if missing.

---

## Checkpoint

- [ ] `part0_checkpoint.json` → `"status": "pass"`  
- [ ] ADR [001](../decisions/001-spotify-product-lock.md) accepted  

**Next:** [Part 1 — ingest](../docs/DATA_SOURCES.md)
