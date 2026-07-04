# Edge Cases — Music Discovery Graduation Project (Part-wise)

Maps **edge cases** to the same **parts** as [architecture.md](./architecture.md) (§4–§9) and [ROADMAP.md](./ROADMAP.md) so design, implementation, QA, and submission stay aligned.

**Sources:** [problem.md](./problem.md) · [architecture.md](./architecture.md) · [ROADMAP.md](./ROADMAP.md) · [../Milestone-2-Review/edge-cases.md](../Milestone-2-Review/edge-cases.md)

**Legend**

| Priority | Meaning |
|----------|---------|
| **P0** | Must handle correctly for grading, safety, or deliverable rejection (PII, skipped Part 2, broken links, solution before research). |
| **P1** | Should handle gracefully; document in README **Known limitations** if deferred. |
| **P2** | Nice-to-have robustness or polish. |

**Part map (quick)**

| Part | Focus | Edge ID prefixes |
|------|--------|------------------|
| [0](#part-0--product-lock-and-setup) | Spotify/Gaana lock, config, segment | **S**, **C** |
| [1A](#part-1a--multi-source-collection) | Scrape + manual sources | **COL** |
| [1B](#part-1b--normalize-and-ingest) | Unified corpus | **D** |
| [1C](#part-1c--theme-discovery-ai-engine) | Groq classify, themes, insights | **T**, **Q** |
| [1D](#part-1d--review-workflow-deploy) | Streamlit workflow URL | **WF** |
| [2](#part-2--user-research-validation) | 5–6 interviews, validation matrix | **R**, **V** |
| [3](#part-3--problem-definition) | Problem lock, MVP scope | **P** |
| [4](#part-4--ai-native-mvp-loopbreak) | Production agent, grounded AI | **A**, **M** |
| [5](#part-5--submission-and-deck) | PDF, links, deadline | **DEL** |
| [6](#part-6--cross-cutting--end-to-end) | Full pipeline, rubric | **X**, **G** |

---

## Part 0 — Product lock and setup

Corresponds to [architecture.md §1](./architecture.md#1-product-and-business-scope), [ROADMAP Step 0](./ROADMAP.md#step-0--choose-one-product-do-this-first).

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **S1** | **Wrong product** in deck vs corpus (Spotify data, Gaana slides). | Single `config/product.json`; deck, corpus, MVP copy all match. | P0 |
| **S2** | **Both** Spotify and Gaana data mixed in one CSV. | One product per run; separate `data/raw/{product}/` if experimenting. | P0 |
| **S3** | **Competitor app** scraped (wrong package id). | Validate `android_package` / `ios_app_id` in config against store listing. | P1 |
| **S4** | Segment definition **vague** (“all Spotify users”). | Lock `target_segment` in config before Part 2 recruitment. | P0 |
| **S5** | **Skip Part 1** and jump to MVP idea. | Violates [problem.md](./problem.md); state machine blocks Part 3 without `theme_map.json`. | P0 |
| **C1** | `config/product.json` missing theme legend. | Ship 8 discovery `theme_id`s before first classify run. | P0 |
| **C2** | Groq `.env` missing or invalid. | Fall back to keyword classify; log in `ingest_report`; document in README. | P1 |
| **C3** | Repo has **no `.gitignore`** for secrets. | Ignore `.env`, `token.json`, raw interview recordings. | P0 |

**Where handled:** `config/product.json`, README scope, [architecture §3.1 state machine](./architecture.md#31-project-state-machine).

---

## Part 1A — Multi-source collection

Corresponds to [architecture.md §4.2](./architecture.md#42-data-sources-architecture), [ROADMAP §1.2](./ROADMAP.md#12-data-sources--free-collection-methods-in-order).

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **COL1** | **Play Store scraper** rate-limited or blocked. | Retry with backoff; cache raw JSON; supplement with manual export or Kaggle bootstrap. | P1 |
| **COL2** | **App Store scraper** returns empty for India (`in`). | Try `country='in'` then `us`; document country in `ingest_report`; minimum 200 store reviews combined. | P1 |
| **COL3** | **Reddit API** OAuth fails or quota hit. | Fall back to manual CSV (30–50 threads); label `source=reddit`. | P1 |
| **COL4** | **Only one source** collected (Play Store only). | Pipeline completes; deck states gap; aim for ≥3 source types before submit (**architecture §12.1**). | P1 |
| **COL5** | **Forum/social** volume too low (<10 rows). | Document in README; do not fabricate posts. | P1 |
| **COL6** | Scraper pulls **non-review** text (developer replies, spam). | Filter rows where text matches reply patterns; log `dropped_dev_reply`. | P1 |
| **COL7** | **Gaana** corpus mostly Hindi; English filter drops >50%. | Document **D12** limitation; optional Hindi pipeline = P2 stretch; do not silently omit. | P1 |
| **COL8** | **Stale reviews** only (all >1 year old). | Prefer `sort=NEWEST` on Play scrape; log date range in `ingest_report`. | P1 |
| **COL9** | **Duplicate** post across Reddit + forum copy-paste. | Dedup by text hash in normalize; increment `dropped_duplicate`. | P1 |
| **COL10** | **Login-walled** social scrape attempted. | **Reject** — public data only per [problem.md](./problem.md) spirit and architecture hard rules. | P0 |

**Where handled:** `part-1-ingest/scrape_*.py`, manual CSV templates, `artifacts/ingest_report.json`.

---

## Part 1B — Normalize and ingest

Corresponds to [architecture.md §4.3](./architecture.md#43-canonical-data-model--feedback_normalizedcsv). Reuses Milestone-2 ingest patterns.

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **D1** | **Schema mismatch** across sources (Reddit has no `rating`). | Allow null `rating` for non-store sources; require `text` + `source` + `date`. | P0 |
| **D2** | **Missing date** on manual forum paste. | Use collection date + flag `date_inferred=true` in report; prefer actual post date when visible. | P1 |
| **D3** | **Rating** unparseable on store review. | Drop row; count in ingest report. | P0 |
| **D4** | **Empty text** (title-only or emoji-only). | Drop; increment `dropped_missing_text`. | P0 |
| **D5** | **PII** in text (email, phone, @handle). | Keep for classify if needed; **redact in quote_bank** and deck; never show usernames in slides. | P0 |
| **D6** | **Emoji-only** or heavy emoji reviews. | Drop or strip per Milestone-2 policy; count `dropped_emoji`. | P1 |
| **D7** | **Non-English** review (Hinglish, Hindi). | Drop for English MVP; count `dropped_non_english`; note in README for Gaana. | P1 |
| **D8** | **Very short text** (“bad app”, “love it”). | Keep for counts; down-rank in quote selection (min word threshold for quotes). | P2 |
| **D9** | Corpus **<800 rows** after filters. | Still proceed if ≥500; README notes volume; broaden scrape before submit if time allows. | P1 |
| **D10** | Corpus **>5,000 rows** slows pipeline. | Full ingest; Groq sample 300–500 via `review_sample.py`; keyword fallback for rest. | P1 |
| **D11** | **Bot/spam** reviews (“promo code”, crypto). | Optional keyword drop list; log count. | P2 |
| **D12** | **Same user** repeated reviews not dedupable. | Dedup identical text only; accept multiple rows from same user if text differs. | P2 |

**Where handled:** `part-1-ingest/normalize.py`, [Milestone-2 text_normalize.py](../Milestone-2-Review/phase-1/1.2-ingest/text_normalize.py).

---

## Part 1C — Theme discovery (AI engine)

Corresponds to [architecture.md §4.4–§4.6](./architecture.md#44-theme-legend-max-8). Answers six research questions in `insight_report.md`.

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **T1** | Review fits **two themes** (repeat + bad reco). | One **primary** `theme_id` per row; tie-break via legend “Includes” rules. | P1 |
| **T2** | LLM invents **invalid theme_id**. | Map to nearest valid or `discovery_friction`; log parse errors. | P0 |
| **T3** | **Groq 403/429** rate limit. | Batch sleep + keyword fallback; hybrid assignments OK; log in `phase1_report.json`. | P1 |
| **T4** | **Coverage <85%** classified. | Re-run failed batches; fail Part 1 gate if still <80%. | P1 |
| **T5** | **Single theme >50%** of corpus. | Valid if data supports; insight report explains concentration; don’t force fake balance. | P1 |
| **T6** | **Theme only in one source** (e.g. social only). | Flag in `source_breakdown.json`; lower confidence in deck narrative. | P1 |
| **T7** | **Reddit skews negative** vs Play Store ratings. | Report segment/source splits; don’t merge without labeling. | P1 |
| **T8** | **Insight report** doesn’t answer all 6 questions. | Block Part 2 start until each question has ≥1 metric or “insufficient data”. | P0 |
| **T9** | **Re-run** classification gives different borderline tags. | Accept ~5–10% drift; stable `theme_id` slugs; document in README. | P2 |
| **T10** | **Pricing/ads** dominates but problem is discovery. | Keep theme; Part 3 narrows to discovery-specific root cause for MVP. | P1 |

### Quotes (Part 1)

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **Q1** | Quote **not substring** of source `text`. | Reject quote in `quote_bank`; re-pick from same theme. | P0 |
| **Q2** | Quote contains **PII** or @username. | Redact before deck/workflow display. | P0 |
| **Q3** | Quote **too long** for slide. | Trim to ≤25 words with ellipsis; full text in quote_bank only. | P1 |
| **Q4** | **Cherry-picked** quotes contradict theme counts. | Prefer pain-first (low rating / high upvotes on Reddit); note selection policy in appendix. | P1 |
| **Q5** | **Same quote** used for two themes. | Allow if text genuinely dual-purpose; prefer unique quotes per top theme. | P2 |

**Where handled:** `part-1-analysis/classify.py`, `aggregate.py`, `artifacts/insight_report.md`, `artifacts/quote_bank.json`.

---

## Part 1D — Review workflow deploy

Corresponds to [architecture.md §4.7](./architecture.md#47-review-analysis-workflow-app-deliverable-1), **Deliverable #1**.

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **WF1** | Streamlit app **localhost only** at submit. | **Fail** deliverable; deploy to Streamlit Cloud / HF Spaces. | P0 |
| **WF2** | Workflow URL **404** or login wall. | Public read; test in incognito before submit. | P0 |
| **WF3** | **Groq key** exposed in frontend code. | Secrets in Streamlit Cloud secrets only; never commit. | P0 |
| **WF4** | App **cold start** timeout on free tier. | Pin minimal deps; bundle precomputed `theme_map.json` (no scrape on load). | P1 |
| **WF5** | “Ask the corpus” returns **hallucinated** stats. | Ground Q&A in loaded JSON/MD; system prompt: cite theme counts only. | P0 |
| **WF6** | Mentor opens workflow on **mobile**; layout broken. | Basic responsive Streamlit layout; test one mobile view. | P2 |
| **WF7** | **Deck slide** missing workflow diagram/link. | Slide 3–4 must include 3-box flow + hyperlink per ROADMAP. | P0 |

**Where handled:** `part-1-workflow/app.py`, Streamlit secrets, deck slide 3.

---

## Part 2 — User research validation

Corresponds to [architecture.md §5](./architecture.md#5-part-2--validate-through-user-research), [problem.md Part 2](./problem.md#part-2--validate-through-user-research).

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **R1** | **<5 interviews** completed. | **Fail** Part 2 gate; do not lock Part 3. | P0 |
| **R2** | Interviewees **don’t match segment** (wrong screener). | Exclude from synthesis; recruit replacement; document screener in deck link. | P0 |
| **R3** | **Leading questions** that only confirm AI themes. | Guide includes neutral probes + “what would disprove this?” | P1 |
| **R4** | **No recording/notes** — can’t cite evidence. | Minimum written notes per participant; quotes in synthesis. | P0 |
| **R5** | **Friend bias** (all close friends). | Accept if segment-fit; diversify recruitment where possible; acknowledge limitation. | P1 |
| **R6** | Participant **no-shows**. | Over-recruit 7–8 to land 5–6; log no-shows. | P1 |
| **R7** | **Hindi interview** but English report only. | Translate key quotes; note language in synthesis. | P1 |
| **R8** | Interviews conducted **before** Part 1 themes ready. | Show theme cards in second half of interview; reorder if needed. | P1 |

### Validation matrix

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **V1** | **All AI themes validated** without nuance. | Suspicious; include ≥1 Partial or refined theme for credibility. | P1 |
| **V2** | **All AI themes rejected** — corpus useless? | Refine legend or segment; re-sample corpus; don’t fake validation. | P0 |
| **V3** | **<3 themes** validated (Y or Partial). | Block Part 3 per [architecture §3.1 invariant](./architecture.md#31-project-state-machine). | P0 |
| **V4** | Interview reveals **new pain** not in Part 1. | Add to synthesis; optional re-tag sample; cite in Part 3 problem. | P1 |
| **V5** | **Surprise insight** not in deck. | Required for strong slide 5; document explicitly. | P1 |
| **V6** | **Participant PII** in synthesis or deck. | Use P1, P2 IDs only; no names/emails in PDF. | P0 |

**Where handled:** `part-2-research/interview_synthesis.md`, Google Form screener, deck slide 5.

---

## Part 3 — Problem definition

Corresponds to [architecture.md §6](./architecture.md#6-part-3--define-the-problem).

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **P1** | Problem statement **too broad** (“improve discovery”). | One narrowed JTBD + root cause; see ROADMAP §3.2 examples. | P0 |
| **P2** | Problem **not tied** to Part 2 quotes. | Every claim links to interview ID or theme stat. | P0 |
| **P3** | **No business case** (metrics missing). | Include discovery session rate / new artist listens / retention framing. | P0 |
| **P4** | **Multiple MVP problems** selected. | `mvp_scope.json` lists **one** primary problem_id. | P0 |
| **P5** | Root cause = **symptom** (“bad UI”) not cause (“decision fatigue after work”). | Reframe using “5 whys” in problem doc. | P1 |
| **P6** | **Misalignment** — MVP solves pricing but research was about Discover Weekly. | Reconcile or change MVP scope before Part 4 build. | P0 |
| **P7** | **Segment size** claimed without proxy. | Use corpus % + screener count; say “directional” if needed. | P1 |

**Where handled:** `part-3-problem/problem_statement.md`, `mvp_scope.json`, deck slide 6.

---

## Part 4 — AI-native MVP (LoopBreak)

Corresponds to [architecture.md §7](./architecture.md#7-part-4--ai-native-mvp-loopbreak), **Deliverable #3**.

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **A1** | MVP gives **generic music tips** (“listen to new genres”). | System prompt injects Part 1 themes + Part 2 quotes; must reference research. | P0 |
| **A2** | MVP **invents** artist/track names as facts. | Frame as strategies/paths, not catalog claims; “e.g.” wording; no fake “Spotify data”. | P0 |
| **A3** | **No explanation** of why user loops (black box). | Response schema requires `why_looping` field. | P0 |
| **A4** | **Traditional reco** not addressed in deck/demo. | Slide 7 + MVP copy explains CF vs intent+explainability. | P0 |
| **A5** | Groq down during **mentor demo**. | Serve cached `sample_responses.json` fallback; banner “demo mode”. | P1 |
| **A6** | User input **empty** or gibberish. | Validate input; prompt for context or show example personas. | P1 |
| **A7** | User input **harmful/off-topic**. | Refuse; redirect to listening context prompt. | P1 |
| **A8** | **Same output** for all personas. | 3 test personas must produce distinct paths in QA. | P1 |
| **M1** | MVP **not deployed** (GitHub only). | **Fail** deliverable; public URL required. | P0 |
| **M2** | MVP URL **requires Spotify login**. | Out of scope v1; no OAuth wall for graders. | P0 |
| **M3** | MVP is **static Figma** only. | Insufficient unless paired with live AI backend link. | P0 |
| **M4** | MVP **duplicates** Part 1 dashboard with no new UX. | Must show coach/agent flow: context → why → 3 paths → action. | P0 |
| **M5** | **Secrets** in public GitHub repo. | Rotate key; use host secrets; scan before push. | P0 |
| **M6** | Production app **sleeping** on free tier. | Wake before submit; or HF Spaces; note in submission email if needed. | P1 |

**Where handled:** `part-4-mvp/app.py`, `prompts/system.md`, Streamlit/HF deploy.

---

## Part 5 — Submission and deck

Corresponds to [problem.md deliverables](./problem.md#final-deliverables), [ROADMAP submission checklist](./ROADMAP.md#submission-checklist-jul-6).

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **DEL1** | **Fellow name** on any slide. | **Violates rules** — remove all names before export. | P0 |
| **DEL2** | **>10 slides** (title counted). | Merge or cut; appendix not counted if separate file — confirm portal rules; stay ≤10 in PDF. | P0 |
| **DEL3** | Slide title **“Problem”** / **“Solution”** only. | Message-first titles per problem.md. | P0 |
| **DEL4** | Font **<14pt** (Slides/PPT). | Increase before PDF export. | P0 |
| **DEL5** | PDF **>40 MB**. | Compress images; link heavy assets instead. | P0 |
| **DEL6** | **Broken hyperlinks** (workflow, MVP, Form). | Test incognito; “anyone with link” access on Google assets. | P0 |
| **DEL7** | **Submit after 3:59 PM IST** Jul 6. | Portal rejects; finish by 3:00 PM buffer. | P0 |
| **DEL8** | **Wrong filename** (not `NL Spotify.pdf`). | Rename to required pattern. | P0 |
| **DEL9** | **Colour-only** chart (red/green) without labels. | Colour-blind-safe palette + direct labels. | P1 |
| **DEL10** | **No metrics** on slides (rubric: data orientation). | Every claim slide has ≥1 number or n=6 interviews. | P0 |
| **DEL11** | Workflow slide **missing** from deck. | Include 1-slide workflow per Part 1 deliverable. | P0 |
| **DEL12** | Google Form / notes **private**. | Share view-only link in deck or appendix note. | P1 |

**Where handled:** `deck/NL Spotify.pdf`, submission portal, [ROADMAP §10-slide outline](./ROADMAP.md#10-slide-deck-outline-pdf-deliverable).

---

## Part 6 — Cross-cutting / end-to-end

| ID | Edge case | Expected behavior | Priority |
|----|-----------|-------------------|----------|
| **X1** | **Solution-first** narrative (MVP before research story). | Deck order: corpus → validation → problem → MVP. | P0 |
| **X2** | **Contradictory** stats between deck and artifacts. | Single source: `theme_map.json`, `ingest_report.json`; regenerate slides if pipeline re-runs. | P0 |
| **X3** | Mentor asks **“why not use Spotify API?”** | README + deck: v2 scope; graduation tests AI UX without catalog dependency. | P1 |
| **X4** | **ChatGPT one-pager** substituted for pipeline. | Workflow URL + artifacts prove repeatable system. | P0 |
| **X5** | **Part 4** built before Part 2 done. | Weak validation story; redo deck narrative or complete interviews. | P0 |
| **G1** | **Happy path E2E** | Collect → normalize → theme → workflow live → 6 interviews → problem → MVP → PDF + 2 links. | P0 |
| **G2** | **AI wrong, human right** | Interview disproves top theme → honest slide 5 → refined Part 3. | P1 |
| **G3** | **Mentor rubric: creativity** | Show LoopBreak UX + research-grounded prompts, not generic chatbot. | P0 |
| **G4** | **Mentor rubric: communication** | 8–10 min rehearsed; one idea per slide; message titles. | P1 |

---

## Part-wise review checklist

| Part | Before marking “done,” verify |
|------|-------------------------------|
| **0** | **S1, S4, S5**; product + segment in config; `.gitignore` secrets **C3** |
| **1A** | **COL10** public only; ≥2 sources started; date range logged **COL8** |
| **1B** | **D1, D4, D5**; `feedback_normalized.csv` exists; ingest_report complete |
| **1C** | **T2, T8**; insight_report answers 6 questions; quotes trace **Q1–Q2** |
| **1D** | **WF1–WF2, WF7**; workflow URL works incognito |
| **2** | **R1, R4, V3**; validation matrix; surprise insight **V5** |
| **3** | **P1, P2, P4**; `mvp_scope.json` single problem |
| **4** | **A1–A4, M1, M4**; MVP URL live; 3 personas distinct **A8** |
| **5** | **DEL1, DEL2, DEL6, DEL7, DEL10, DEL11**; PDF exported |

---

## Traceability to [problem.md](./problem.md)

| Requirement | Parts / edge IDs |
|-------------|------------------|
| Analyze before solution | **S5**, **X1**, **X5** |
| App + Play + Reddit + forums + social | **COL4**, **COL5**, Part 1A |
| Six research questions answered | **T8** |
| 5–6 segment interviews | **R1**, **R2** |
| Root cause + segment + business case | **P1–P3** |
| AI-native MVP in production | **M1**, **M3**, **A1–A4** |
| Why reco insufficient / what AI unlocks | **A4**, deck slide 7 |
| Workflow link + 1 deck slide | **WF7**, **DEL11** |
| 10-slide PDF, no name | **DEL1–DEL4** |
| Accessible hyperlinks | **DEL6**, **DEL12** |
| 70%+ rubric: metrics | **DEL10**, **T5–T7**, **V5** |

---

## Traceability to [architecture.md](./architecture.md)

| Architecture concern | Edge IDs |
|----------------------|----------|
| Research-before-solution pipeline | **S5**, **X1**, **X5**, state machine **V3** |
| Multi-source normalized schema | **D1**, **COL9** |
| Groq cost cap | **D10**, **T3** |
| Grounded quotes | **Q1–Q2**, **WF5** |
| Validation matrix gate | **V3**, **R1** |
| Single MVP problem | **P4**, **P6** |
| LoopBreak response schema | **A3**, **A8** |
| Public deploy URLs | **WF1–WF2**, **M1** |
| No Spotify API v1 | **M2**, **X3** |

---

## Traceability to [ROADMAP.md](./ROADMAP.md)

| ROADMAP milestone | Edge IDs |
|-------------------|----------|
| Step 0 product pick | **S1–S4** |
| Part 1 scrape volumes | **COL1–COL2**, **D9** |
| Streamlit workflow deliverable | **WF1–WF7** |
| Part 2 screener + 6 interviews | **R1–R8**, **V1–V6** |
| Part 3 problem template | **P1–P7** |
| LoopBreak MVP | **A1–A8**, **M1–M6** |
| Jul 6 submission checklist | **DEL1–DEL12** |
| Free tool stack failures | **T3**, **COL1**, **WF4**, **A5** |

---

## Minimum QA matrix (by part)

| Part | One must-pass edge check |
|------|---------------------------|
| 0 | Single product locked (**S1**); didn’t skip Part 1 (**S5**) |
| 1A | No login scraping (**COL10**) |
| 1B | PII redacted in quotes path (**D5**) |
| 1C | Insight report answers 6 questions (**T8**) |
| 1D | Workflow loads incognito (**WF2**) |
| 2 | ≥5 interviews + ≥3 themes validated (**R1**, **V3**) |
| 3 | One MVP problem in scope file (**P4**) |
| 4 | MVP URL public, grounded output (**M1**, **A1**) |
| 5 | PDF ≤10 slides, no name, links work (**DEL1**, **DEL2**, **DEL6**) |

---

## Scripted smoke scenarios (end-to-end)

1. **Happy path:** Scrape Play → normalize → classify → insight report → deploy workflow → screener → 6 interviews → validation matrix → problem doc → deploy LoopBreak → export deck → submit.  
2. **Groq outage:** Classify falls back to keywords (**T3**); MVP shows cached responses (**A5**).  
3. **Fake quote:** Insert paraphrased quote in bank → validation rejects (**Q1**).  
4. **Wrong segment interview:** Screener fail → exclude (**R2**).  
5. **AI theme refuted:** Mark theme **N** in matrix → Part 3 problem shifts (**G2**, **V2**).  
6. **Incognito grader:** Open workflow + MVP + Form links without login (**DEL6**).  
7. **Single source only:** Play Store only → pipeline completes; deck notes gap (**COL4**).  
8. **Large corpus:** 2,000 rows → sample 400 to Groq (**D10**); full counts in theme_map.  
9. **Deck stat audit:** Random theme % on slide 4 matches `theme_map.json` (**X2**).  
10. **Deadline drill:** Export PDF at T-24h; re-test links at T-1h (**DEL7**).

---

## Mentor rubric → edge case coverage

| Rubric parameter | Supporting edge IDs | Evidence in submission |
|------------------|---------------------|-------------------------|
| Presentation / communication | **DEL3**, **G4**, **WF7** | Message titles; workflow slide; rehearsed demo |
| Clarity & depth of thought | **P5**, **V5**, **G2**, **X1** | Validation matrix; surprise insight; honest AI refutation |
| Creativity of solution | **A4**, **M4**, **G3**, **X4** | LoopBreak coach UX; not one-pager ChatGPT |
| Data & metrics orientation | **DEL10**, **T5–T7**, **P7** | Counts, theme %, n=6, business KPIs |

---

## Known limitations (README template)

Copy applicable rows into project `README.md`:

| ID | Limitation text (example) |
|----|---------------------------|
| **COL4** | “Corpus includes Play Store + Reddit only; App Store scrape returned empty for IN.” |
| **COL7** | “English-only pipeline; Gaana Hindi reviews excluded (see dropped_non_english).” |
| **D10** | “Groq classified a stratified sample of N posts; remainder keyword-tagged.” |
| **T9** | “Re-running classification may shift ~5–10% of borderline tags.” |
| **R5** | “Interview sample recruited via personal network; directional not statistically representative.” |
| **M2** | “MVP does not connect to Spotify API; simulates coach UX with research-grounded AI.” |
| **WF4** | “Free Streamlit tier may cold-start; pre-bundled artifacts avoid live scrape.” |

---

## Failure recovery playbook

| Symptom | Likely ID | Recovery |
|---------|-----------|----------|
| Workflow 404 | **WF2** | Redeploy Streamlit; pin commit hash in deck link |
| MVP generic answers | **A1** | Add Part 1/2 excerpts to system prompt; redeploy |
| Interviews don’t match AI | **V2** | Refine segment or theme legend; update slide 5 honestly |
| Groq 429 everywhere | **T3**, **A5** | Keyword classify + cached MVP responses; note in README |
| PDF rejected (size) | **DEL5** | Compress PNGs; move screenshots to linked Doc |
| Grader can’t open Form | **DEL12** | Share “Anyone with link → Viewer” |

---

## Document review

**Structure:** Edge cases align with [architecture.md](./architecture.md) Parts 1–4 + submission pack so you can test **per part** alongside [ROADMAP.md](./ROADMAP.md) weekly tasks.

**Overlap with Milestone-2:** Ingest (**D**), theme (**T**), quote (**Q**), and Groq cap (**D10**) patterns mirror [Milestone-2 edge-cases](../Milestone-2-Review/edge-cases.md) — reuse handlers where code is shared.

**When tradeoffs arise:** Log decision in `decisions/` (planned) and note ID in README Known limitations.
