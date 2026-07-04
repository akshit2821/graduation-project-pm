# Problem statement — LoopBreak

**Product:** Spotify · **Role:** Growth PM  
**Research basis:** Part 1 corpus (629 posts) + Part 2 interviews (6 participants)  
**MVP:** LoopBreak — AI Discovery Coach (Part 4)

---

## Problem (one sentence)

**Indian urban listeners aged 22–35** who rely on saved playlists struggle to **start meaningful discovery sessions at daily transition moments** (e.g. commute home, end of workday) because **decision fatigue and comfort habits outweigh recommendation feeds**—not because they lack access to new music.

---

## Root cause

### Primary cause
**Decision fatigue at transition moments** — when mental energy is low, users default to 2–3 familiar playlists instead of evaluating Discover Weekly, Home, or a large Liked Songs library.

### Supporting evidence

| Source | Evidence |
|--------|----------|
| **Part 2 interviews** | 6/6 describe “can’t pick” from large library; 5/6 default to same playlists after work; P01, P03, P05 want **short explanation + 3 options**, not another feed |
| **Part 2 surprise insight** | Looping is a **moment-of-day habit**, not only bad algorithms |
| **Part 1 corpus** | Discovery friction **~45–47%** of themed feedback; repeat listening **~5–6%** explicitly tagged; ads/free tier **~31–33%** interrupt browsing (P05, P02, P06) |
| **Validation matrix** | `discovery_friction`, `repeat_listening`, `library_clutter` validated **Y** in interviews |

### Common misconception (what this is *not*)
The problem is **not** “Spotify’s algorithm is always wrong.” Interviews show Discover Weekly is often **ignored or distrusted**, not fine-tuned—users skip the decision entirely and return to comfort loops.

---

## Target segment

| Field | Definition |
|-------|------------|
| **Who** | Indian urban Spotify listeners, 22–35, 5+ hrs/week listening |
| **Behavior** | ≥60% listening from saved playlists or Liked Songs; Discover Weekly opened rarely or dismissed |
| **Moment** | Post-work / commute / “shutdown” transitions when energy for choice is lowest |
| **Size proxy** | Part 1: discovery-friction + repeat-listening themes ≈ **50%+** of public feedback signal; Part 2: 6/6 screener-fit participants match profile |

### Job-to-be-done

> **When** I finish my day and open Spotify,  
> **I want** a low-effort way to break my playlist loop without browsing endlessly,  
> **so I** can discover something new that still fits my mood without it feeling like work.

---

## Why solving this matters (business case)

### Strategic alignment
Spotify’s Growth goal: **increase meaningful music discovery** and **reduce repetitive listening** at scale. Repeat comfort loops cap exposure to new artists and discovery surfaces (Discover Weekly, Radio, Daylists).

### Why now
- Large share of listening still from **repeat playlists** despite world-class reco infrastructure (company context).  
- Part 1 + Part 2 show friction is **behavioral and contextual**, not only ranking quality—a coach-style intervention fits before/alongside feed changes.

### Success metrics (MVP → product)

| Metric | Definition | MVP proxy |
|--------|------------|-----------|
| **Discovery session rate** | % sessions where user plays ≥1 track outside top 3 playlists in 7 days | User selects a LoopBreak path and completes suggested action |
| **New artist listen rate** | % listening hours to artists not in top-50 past 30 days | User accepts a path tagged “new artist” or “forgotten save” |
| **D7 retention on explorers** | Return rate for users who started a discovery session | User returns to LoopBreak within 7 days (prototype: repeat visit) |
| **Loop-break rate** | % transition-moment opens that don’t default to same playlist | Self-reported in demo + path selection |

### Growth hypothesis
If we **explain why the user is looping** and offer **3 grounded discovery paths** at transition moments, users will choose exploration over autopilot—improving discovery sessions without forcing another opaque feed.

---

## MVP scope pointer

Problem locked for Part 4: **`transition_moment_coach`** → see [mvp_scope.json](./mvp_scope.json).

**Out of scope for MVP:** Spotify API integration, full catalog playback, personalized ranking model retraining, podcast discovery, social graph features.

---

## Traceability

| Research | Link |
|----------|------|
| Part 1 insight report | `artifacts/insight_report.md` |
| Part 1 research Q&A | `artifacts/research_answers.json` |
| Part 2 synthesis | `part-2-research/interview_synthesis.md` |
| Product lock | `config/product.json` → `target_segment` |
