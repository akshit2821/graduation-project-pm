# Graduation Project Roadmap — Music Discovery (Spotify / Gaana)

**Role:** Growth PM — increase meaningful discovery, reduce repetitive listening  
**Deadline:** **6 July 2026, 3:59 PM IST** (hard cutoff)  
**Results:** 12–15 July 2026  

**Deliverables (all required)**

| # | Deliverable | Format |
|---|-------------|--------|
| 1 | Review Analysis Workflow | Public **link** + **1 slide** in deck explaining it |
| 2 | Thought process deck | **PDF**, **10 slides max**, file name e.g. `NL Spotify.pdf` |
| 3 | AI-native MVP | **Production link** (deployed agent or prototype) |

**Deck rules (strict):** No fellow name · title slide counts in 10 · slide titles = key message (not “Problem”) · min font 14 (Slides/PPT) · hyperlinks must be accessible · PDF < 40 MB · colour-blind-safe palette.

---

## Timeline at a glance

| Week | Dates (approx) | Focus |
|------|----------------|-------|
| **0** | May 23–25 | Pick product · set up repo · data plan |
| **1** | May 26 – Jun 1 | **Part 1** — collect reviews + Reddit · build analysis engine |
| **2** | Jun 2–8 | **Part 1** finish · insight report · workflow URL live |
| **3** | Jun 9–15 | **Part 2** — 5–6 interviews · synthesis |
| **4** | Jun 16–22 | **Part 3** — problem statement · segment · business case |
| **5** | Jun 23–29 | **Part 4** — build + deploy MVP |
| **6** | Jun 30 – Jul 5 | **Deck + PDF** · dry run · fix links/access |
| **D-day** | **Jul 6** | Submit before 3:59 PM IST |

---

## Step 0 — Choose ONE product (do this first)

| Factor | **Spotify** (recommended) | Gaana |
|--------|---------------------------|-------|
| App Store + Play reviews | Very high volume, easy to scrape | Lower volume, more Hindi/Hinglish |
| Reddit / forums | r/spotify, r/truespotify, Community forums | r/gaana sparse; rely on Play reviews + Twitter |
| Interview recruitment (India) | Easy (most users know Spotify) | Easier if you want Hindi-first segment |
| Differentiation in cohort | Common choice — win on insight depth | Less common — win on local segment story |
| Free data tooling | Mature Python scrapers + Kaggle datasets | Play Store scraper + manual forum sweep |

**Recommendation:** Choose **Spotify** unless you already have **5–6 Gaana power-users** lined up for interviews. More free data → stronger Part 1 → stronger Part 3.

**Lock your focus segment early (example):**  
*“Indian urban listeners aged 22–35 who mostly replay playlists and rarely use Discover Weekly meaningfully.”*

Write this in `Graduation-Project/config/product.json` before collecting data.

---

# Part 1 — AI-Powered Review Discovery Engine

**Goal:** Analyze user feedback at scale **before** proposing any product solution.  
**Reuse:** Your [Milestone-2-Review](../Milestone-2-Review/) pipeline (ingest → classify → themes → quotes) — retarget for music discovery questions.

## 1.1 Questions your engine must answer

Map every theme tag to at least one question:

| Research question | Theme IDs to extract (examples) |
|-------------------|----------------------------------|
| Why struggle to discover new music? | `discovery_friction`, `same_songs`, `algorithm_stale` |
| Frustrations with recommendations? | `bad_recommendations`, `discover_weekly_miss`, `radio_repeat` |
| Listening behaviors users want? | `mood_listening`, `workout_focus`, `background_play` |
| Why repeat same content? | `comfort_playlist`, `decision_fatigue`, `skip_risk` |
| Segment differences? | Tag `platform` + `rating` + `language` + infer `segment_hint` |
| Unmet needs across sources? | Cross-source theme counts in `insight_report.json` |

## 1.2 Data sources — free collection methods (in order)

### A. Google Play Store reviews (free, automated)

**Tool:** Python `google-play-scraper` (no API key)

```powershell
pip install google-play-scraper pandas
```

**Target package:** `com.spotify.music` or `com.gaana.android`  
**Volume:** Scrape **500–1,000** recent reviews (free; no cap issue)  
**Fields:** rating, text, date, thumbs up  

**Script location (create):** `Graduation-Project/part-1-ingest/scrape_play.py`

### B. Apple App Store reviews (free, semi-automated)

**Options (pick one):**

| Method | Cost | Effort |
|--------|------|--------|
| **app-store-scraper** (Python) | Free | Medium — may need country code `in` |
| **Manual export** from App Store Connect | Free | Only if you have developer access |
| **Kaggle dataset** “Spotify app reviews” | Free | Fast bootstrap for demo |

**Target:** 300–500 reviews for India (`country='in'`) if using scraper.

### C. Reddit (free)

**Tool:** Public JSON endpoints (no auth for read-only low volume) OR Reddit API free tier

**Subreddits (Spotify):** `r/spotify`, `r/truespotify`, `r/spotifyplaylists`, search `"discover weekly"`, `"same songs"`, `"recommendation"`  

**Method:**

1. Manual: collect **30–50 high-signal posts/comments** (copy title + body + upvotes into CSV)  
2. Semi-auto: Python `PRAW` with free Reddit app credentials (5 min setup at reddit.com/prefs/apps)

**CSV columns:** `source`, `date`, `text`, `upvotes`, `url`, `subreddit`

### D. Community forums (free, manual)

**Spotify:** [Spotify Community — Discover & Recommendations](https://community.spotify.com/t5/Discover/ct-p/Discover)  
**Gaana:** Facebook groups, Twitter/X search `"Gaana" recommendation`  

**Volume:** **20–40 threads** pasted into `forums_raw.csv` (quality > quantity)

### E. Social media (free, manual sample)

Skip paid social listening. Use:

- **Twitter/X search** (logged-in manual copy): 15–20 tweets  
- **YouTube comments** on “Spotify Discover Weekly not working” videos: 10–15 comments  

Label source=`social` in same normalized CSV.

## 1.3 Normalize into one corpus (reuse Milestone-2 pattern)

**Output file:** `Graduation-Project/data/reviews_normalized.csv`

| Column | Notes |
|--------|-------|
| `review_id` | Hash of source + text |
| `source` | `play_store` \| `app_store` \| `reddit` \| `forum` \| `social` |
| `platform` | ios / android / web |
| `date` | ISO date |
| `rating` | 1–5 or null for Reddit |
| `text` | English only for MVP (note Hindi drops in README) |
| `upvotes` | Optional engagement signal |

**Reuse code from:** `Milestone-2-Review/phase-1/1.2-ingest/` (filters: English, no emoji, dedupe)

## 1.4 AI analysis stack (free)

| Step | Tool | Why |
|------|------|-----|
| Theme classification | **Groq** (`llama-3.1-8b-instant`) via existing `lib/llm_client.py` | Free tier; you already wired this |
| Batch size cap | **400 reviews** to Groq + keyword fallback | Same as Milestone-2 `review_sample.py` |
| Optional Q&A | **Streamlit chat** over `insight_report.json` | “Ask the corpus” demo for mentors |
| Workflow automation | **n8n self-hosted** (free) OR single **`run_analysis.py`** | n8n only if you want visual workflow link |
| No paid tools needed | Avoid ChatGPT Plus, Perplexity Pro unless you already have them |

**Theme legend (music discovery — max 8 themes):**

| theme_id | Label |
|----------|-------|
| `discovery_friction` | Hard to find new music |
| `bad_recommendations` | Discover Weekly / Radio misses |
| `repeat_listening` | Same playlists / artists on loop |
| `library_clutter` | Saved music hard to navigate |
| `ui_complexity` | UI prevents exploration |
| `social_discovery` | Wants friends / shared discovery |
| `podcast_vs_music` | Discovery conflated with podcasts |
| `pricing_ads` | Free tier limits exploration |

**Outputs (Part 1 complete when these exist):**

```text
Graduation-Project/
├── data/reviews_normalized.csv
├── artifacts/
│   ├── theme_map.json          # counts, top themes, by source
│   ├── insight_report.md       # answers 6 research questions with numbers
│   ├── quote_bank.json         # verifiable quotes per theme
│   └── source_breakdown.json   # play vs reddit vs forum split
```

## 1.5 Review Analysis Workflow — public link (deliverable #1)

**Easiest free deploy:** **Streamlit Community Cloud**

| Component | Implementation |
|-----------|----------------|
| UI | Upload CSV **or** view pre-loaded Spotify corpus |
| Tabs | Overview · Themes · Quotes · Ask a question |
| Backend | Load `theme_map.json` + Groq for ad-hoc questions |
| URL | `https://your-app.streamlit.app` |

**Alternative:** **Gradio on Hugging Face Spaces** (also free, zero cold-start limits)

**n8n option (if you want “workflow” literally):**

1. Trigger: new row in Google Sheet  
2. Groq classify → append theme  
3. Update Google Sheet summary  
4. Share n8n cloud trial URL **or** Loom walkthrough + exported JSON  

**Minimum bar:** One **clickable public URL** where a mentor can see corpus stats + theme breakdown + sample quotes.

## 1.6 One slide for workflow (inside final deck)

**Slide title example:**  
*“Review Discovery Engine turns 1,200 public feedback posts into 8 themes in under 10 minutes”*

**Diagram (3 boxes):**

```text
[Collect: Play + App Store + Reddit + Forums]
        ↓
[Normalize + Groq theme classify (free tier)]
        ↓
[Streamlit dashboard: themes, quotes, segment splits]
```

Hyperlink the live Streamlit URL on the slide.

---

# Part 2 — Validate Through User Research

**Goal:** 5–6 **primary** interviews with your **chosen segment** — not random users.

## 2.1 Segment (align with Part 1 data)

Example segment definition:

> Spotify users in India, 22–35, listen 5+ hrs/week, **≥60%** listening from saved playlists/liked songs, use Discover Weekly rarely or dismiss it.

## 2.2 Recruitment (free)

| Channel | Action |
|---------|--------|
| Personal network | 3 friends/colleagues who match segment |
| Reddit | DM r/spotify users who posted about “same songs” (polite, short ask) |
| LinkedIn | Post: “15-min paid coffee chat” — use free Google Meet |
| WhatsApp / college groups | Batch message with screener link |

**Screener (Google Form — free):** 5 questions: age, hours/week, % playlists vs new, last time opened Discover Weekly, willing to screen-share listening history (optional).

## 2.3 Interview guide (30 min each)

| Block | Time | Sample questions |
|-------|------|------------------|
| Warm-up | 3 min | Walk me through yesterday’s listening |
| Current behavior | 8 min | When do you replay vs explore? What triggers repeat? |
| Recommendation products | 8 min | Discover Weekly, Radio, Blend — what works/fails? |
| Pain validation | 8 min | Show **2–3 themes from Part 1** — “Does this match your experience?” |
| Ideal outcome | 3 min | What would “meaningful discovery” look like? |

**Record:** Google Meet + manual notes (Otter.ai free tier optional).  
**Output:** `Graduation-Project/part-2-research/interview_synthesis.md`

## 2.4 Synthesis template (required)

For each interview: **Behaviors · Pains · Quotes · Surprises**  
Across all 6:

| Part 1 AI insight | Validated? (Y/N/Partial) | Evidence quote |
|-------------------|--------------------------|----------------|
| Users repeat due to decision fatigue | | |
| Discover Weekly feels stale | | |

**Rule:** At least **3 Part 1 themes** must be validated or refined — show intellectual honesty if AI was wrong.

---

# Part 3 — Define the Problem

**Goal:** One crisp problem statement rooted in **research**, not reviews alone.

## 3.1 Template (fill after Part 2)

```markdown
## Problem statement
[Segment] struggles to [behavior] because [root cause], not because [common misconception].

## Root cause (why)
- Evidence from interviews: ...
- Evidence from review corpus: ... (% theme, N quotes)

## Target segment
- Who: ...
- Size proxy: ... (e.g. % of Play Store reviews mentioning X)
- Job-to-be-done: "When I ..., I want ..., so I ..."

## Why business cares (Spotify Growth)
- Repeat listening → engagement plateau → lower experiment surface for new artists
- Metric hooks: discovery session rate, new artist listen rate, D7 retention on explorers
- Strategic alignment: company goal to increase meaningful discovery
```

## 3.2 Pick ONE problem to solve in MVP

Do **not** solve everything. Example narrowed problems:

| Problem | MVP fit |
|---------|---------|
| “Discover Weekly feels irrelevant” | AI mood + context briefing before playing DW |
| “I default to comfort playlists after work” | AI “transition moment” nudge at 6pm |
| “Too many saved songs, don’t know what to play” | AI resurfacing forgotten library gems |

**Choose the problem with:** strongest interview validation + clearest AI advantage.

---

# Part 4 — AI-Native MVP (deployed to production)

**Goal:** Functional prototype showing **why AI > traditional reco** — live URL required.

## 4.1 What to explain in deck + demo

| Question | Your answer pattern |
|----------|---------------------|
| Why traditional reco insufficient? | Collaborative filtering optimizes familiarity; misses **intent + moment + explainability** |
| What AI unlocks? | Natural language intent, session context, **reasoning aloud**, cold-start for “break loop” moments |
| How UX changes? | User states goal → AI explains 3 paths → user chooses (human agency) |

## 4.2 Recommended MVP (free deploy, high demo value)

**Name:** **LoopBreak — AI Discovery Coach** (working title)

**User flow:**

1. User selects persona (matches your segment) or describes context: *“Friday evening, tired, only playing old Hindi indie playlists”*  
2. AI (Groq) returns:  
   - **Why you’re looping** (1 sentence, grounded in research themes)  
   - **3 discovery paths** (not just tracks — strategies: mood shift, social, forgotten saves)  
   - **One explainable action** (“Try X because Y”)  
3. Optional: paste Discover Weekly frustration → get personalized “fix my feed” tips  

**Tech (all free):**

| Layer | Choice |
|-------|--------|
| Frontend | Streamlit or Gradio |
| LLM | Groq free tier (Milestone 1 `.env`) |
| Prompt context | Inject top themes + quotes from Part 1 (`insight_report.md`) |
| Deploy | **Streamlit Community Cloud** or **Hugging Face Spaces** |
| Domain | Free subdomain provided by host |

**No Spotify API required** for graduation — you’re prototyping **interaction + AI reasoning**, not integrating catalog (mention as v2 in deck).

## 4.3 Alternative MVPs (if LoopBreak feels too simple)

| MVP | Deploy | AI angle |
|-----|--------|----------|
| **Discovery Gap Dashboard** | Streamlit | Visualizes corpus + “your segment” persona simulator |
| **WhatsApp/Telegram bot** | Telegram Bot API + Replit free | Daily “one new discovery challenge” |
| **Figma clickable proto + HF Gradio** | Figma + link | UI in Figma, AI backend on HF |

**Minimum production bar:** URL loads without localhost · mentor can interact without your laptop · no login wall.

## 4.4 Build checklist (Part 4)

- [ ] `app.py` deployed to Streamlit/HF  
- [ ] System prompt cites Part 1 themes (grounded, not generic)  
- [ ] 3 test personas produce distinct outputs  
- [ ] Error handling if Groq rate-limits (cached sample response)  
- [ ] README on GitHub with architecture (public repo or unlisted gist)  
- [ ] Production URL in submission form + hyperlinked in deck  

---

# 10-Slide Deck Outline (PDF deliverable)

**File name:** `NL Spotify.pdf` (or `NL Gaana.pdf`) — **no fellow name anywhere**

| Slide | Title (message-first) | Content |
|-------|----------------------|---------|
| 1 | Repeat listening is growth’s hidden ceiling at Spotify | Title + one stat from Part 1 |
| 2 | Millions of users still listen from comfort playlists, not discovery | Company context + strategic goal |
| 3 | We analyzed 1,000+ public feedback posts across 4 sources | Source breakdown chart + link to workflow |
| 4 | Users repeat because decision fatigue beats risky exploration | Top 3 themes + quotes (Part 1) |
| 5 | Interviews confirmed AI themes — and revealed one surprise | Part 2 synthesis table |
| 6 | The real problem: [your narrowed problem statement] | Segment + root cause + JTBD |
| 7 | Traditional recommendation optimizes familiarity, not intentional discovery | Why reco fails + business metrics |
| 8 | LoopBreak uses AI to explain why you’re stuck — then offers 3 paths | MVP screenshot + production link |
| 9 | AI changes UX from passive feed to guided discovery with agency | Before/after flow |
| 10 | Success metrics: discovery session rate, new artist listens, D7 retention | KPI tree + next experiment |

**Slide 3 or 4** must include the **Review Workflow** mini-diagram + hyperlink (Part 1 deliverable).

**Design (colour-blind safe):** Use [IBM Carbon](https://carbon-design-system.github.io/carbon-charts/?path=/story/getting-started--get-started) blues/oranges, avoid red/green only pairs · min font **14pt**.

---

# Free Tool Stack Summary

| Need | Tool | Cost |
|------|------|------|
| Play Store scrape | `google-play-scraper` | Free |
| App Store scrape | `app-store-scraper` / Kaggle | Free |
| Reddit | PRAW or manual CSV | Free |
| LLM | Groq (Milestone 1 `.env`) | Free tier |
| Analysis pipeline | Reuse Milestone-2 Python phases | Free |
| Workflow UI | Streamlit | Free |
| MVP host | Streamlit Cloud / Hugging Face Spaces | Free |
| Interviews | Google Meet + Google Form screener | Free |
| Deck | Google Slides → Export PDF | Free |
| Diagrams | Excalidraw / Google Drawings | Free |
| Repo | GitHub public | Free |

**Avoid for budget:** paid social listening, Spotify Web API (paid dev complexity), UserTesting.com, ChatGPT Team.

---

# Submission Checklist (Jul 6)

## Links (test in incognito before submit)

- [ ] Review Analysis Workflow URL loads  
- [ ] MVP production URL loads  
- [ ] Google Form / interview notes shared (view access for anyone with link)  
- [ ] GitHub repo public (if linked)  

## PDF deck

- [ ] Exactly **10 slides** (title counts)  
- [ ] **No fellow name** on any slide  
- [ ] Slide titles = messages, not labels  
- [ ] Min font 14pt  
- [ ] Hyperlinks work  
- [ ] File **< 40 MB**  
- [ ] Named `NL Spotify.pdf` (or Gaana)  

## Content quality (mentor rubric)

- [ ] Part 1 → Part 2 → Part 3 → Part 4 logical thread  
- [ ] Numbers on slides (review counts, theme %, interview n=6)  
- [ ] AI insight validated + one refined/disproved  
- [ ] MVP demonstrates **why AI**, not just chatbot wrapper  
- [ ] Business metrics tied to discovery goal  

---

# Reuse from Your Previous Work

| Milestone-2 asset | Graduation use |
|-------------------|----------------|
| `phase-1` ingest + normalize | Part 1 corpus pipeline |
| `phase-2` Groq classify + theme_map | Part 1 theme engine |
| `lib/llm_client.py` + `review_sample.py` | Free LLM + cap |
| `phase-3` quote selection | Part 1 quote bank |
| Streamlit from Milestone 1 | Part 1 dashboard + Part 4 MVP shell |
| Interview synthesis discipline | Part 2 template |

**New repo folder (recommended):** `Graduation-Project/` with parts 1–4 subfolders — keep Milestone-2 intact as reference.

---

# Week-by-week execution (copy to calendar)

| Day | Task |
|-----|------|
| **May 23–24** | Pick Spotify/Gaana · create theme legend · scrape Play Store 500 reviews |
| **May 25–27** | App Store + Reddit + forum manual pull · normalize CSV |
| **May 28–30** | Run Groq classification · write `insight_report.md` |
| **May 31–Jun 2** | Deploy Streamlit Review Engine · workflow URL live |
| **Jun 3–8** | Screener live · schedule 6 interviews |
| **Jun 9–15** | Conduct interviews · synthesis doc |
| **Jun 16–18** | Problem statement + pick MVP scope |
| **Jun 19–25** | Build LoopBreak MVP · deploy production |
| **Jun 26–30** | Draft 10 slides · insert workflow slide + links |
| **Jul 1–4** | Peer review deck · font/link/PDF checks |
| **Jul 5** | Final dry run · backup PDF export |
| **Jul 6 by 3:00 PM** | Submit (30 min buffer before 3:59 PM IST) |

---

# Decision log (fill as you go)

| Date | Decision | Rationale |
|------|----------|-----------|
| | Product: Spotify / Gaana | |
| | Segment definition | |
| | Top problem for MVP | |
| | MVP name + URL | |
| | Deck file name | |

---

**Next action today:** Pick **Spotify or Gaana**, run Play Store scrape for 500 reviews, fork ingest scripts from Milestone-2 into `Graduation-Project/part-1-ingest/`.
