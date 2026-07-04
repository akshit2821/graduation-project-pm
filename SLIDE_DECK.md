# Graduation Deck — 10 Slides (Draft)

**Product:** Groww (LIP Challenge 4)  
**Solution:** Weekly App Review Pulse — AI agent pipeline + MCP delivery  
**Use this file as copy-paste source for Google Slides.**

---

## Slide 1 — Title

**Title:** Weekly App Review Pulse — From 198 Reviews to a 2-Minute Decision Brief  
**Subtitle:** Graduation Project | NextLeap PM Fellowship  
**Your name + date**

**Speaker note (communication):** Open with the outcome, not the tech.  
*“Every week, product teams drown in store reviews. We built a repeatable pipeline that turns 10 weeks of public reviews into one page leadership can act on—in under 2 minutes to read.”*

---

## Slide 2 — The Problem (Clarity & depth)

**Headline:** Reviews are free signal—but teams read them too late, or not at all

| Pain | Impact |
|------|--------|
| High volume, noisy text | PMs skim star ratings, miss root causes |
| No weekly ritual | Regressions (payments, KYC) surface after churn |
| Manual synthesis | Doesn’t scale; quotes get invented in slide decks |

**Core question (from problem statement):**  
*How might we convert 8–12 weeks of App Store + Play reviews into a scannable weekly note—with real user voice and clear next steps—without exposing PII?*

**Speaker note:** Frame as **decision latency**, not “sentiment analysis.”

---

## Slide 3 — Users & Scope (Clarity)

**Who we serve**

| Audience | Weekly need |
|----------|-------------|
| Product / Growth | What to fix first |
| Support | What users are complaining about |
| Leadership | Health pulse without reading 200 comments |

**Scope locked**

- **Sources:** App Store + Google Play (public exports only)
- **Window:** 10 weeks (2026-03-03 → 2026-05-12)
- **Output:** ≤250-word pulse, 3 themes, 3 quotes, 3 actions
- **Delivery:** Google Doc + Gmail draft via **MCP** (not custom Google APIs in code)

---

## Slide 4 — Solution Overview (Creativity)

**Headline:** Agent pipeline with a hard MCP boundary—not a one-time ChatGPT summary

```text
CSV ingest → theme discovery (Groq) → pulse + validation → MCP publish
```

**What makes it creative**

| Choice | Why |
|--------|-----|
| **≤5 themes, top 3 in note** | Forces PM tradeoffs, not laundry lists |
| **Quote traceability** | Every quote maps to `review_id` in CSV |
| **Validation gate** | Phase 4 blocked until `pulse_validation.json` = pass |
| **MCP-only delivery** | Auditable tool calls for Doc + draft |
| **Free-tier Groq cap** | Stratified 300–500 sample + keyword fallback |

**Visual:** Screenshot or simplified diagram from `architecture.md` §3.

---

## Slide 5 — Data & Ingest (Metrics)

**Headline:** 198 normalized reviews, zero PII columns

| Metric | Value |
|--------|-------|
| Raw rows in | 223 (iOS 122 + Android 101) |
| After filters | **198** reviews |
| Window | 10 weeks |
| English-only drops | 1 |
| Emoji drops | 1 |
| Duplicate drops | 14 |
| Platform split | iOS 108 (55%) · Android 90 (45%) |

**Rating distribution (data-driven prioritization)**

| Stars | Count | Share |
|-------|-------|-------|
| 1★ | 33 | 17% |
| 2★ | 16 | 8% |
| 3★ | 85 | 43% |
| 4★ | 24 | 12% |
| 5★ | 40 | 20% |

**Insight:** Neutral 3★ reviews dominate—theme clustering matters more than average star score.

---

## Slide 6 — Themes & Pulse Output (Metrics + depth)

**Headline:** Top 3 themes by volume—and lowest avg rating wins attention

| Rank | Theme | Share | Avg rating |
|------|-------|-------|------------|
| 1 | Payments & add money | 26.3% | 3.4 |
| 2 | Support & reliability | 21.2% | **2.88** |
| 3 | KYC & verification | 20.7% | **2.66** |

**Sample pulse excerpt (real quotes, redacted)**

- *"Amount debited but not credited to bank account."*
- *"Keeps logging me out after latest update."*
- *"PAN upload keeps failing even with clear photo."*

**Recommended actions (testable, not generic)**

1. UPI retry + explicit error codes — payments  
2. Hotfix portfolio crashes + known-issues banner — support  
3. In-app KYC status timeline — kyc  

**Visual:** Screenshot of `pulse_draft.md` or Google Doc after Phase 4.

---

## Slide 7 — MCP Delivery (Creativity + communication)

**Headline:** Publish through MCP—human approves, agent executes

| Step | Tool | Output |
|------|------|--------|
| 1 | Google Docs MCP | Weekly pulse Doc (primary artifact) |
| 2 | Gmail MCP | Draft to stakeholder with Doc link |
| 3 | Manifest | `delivery_manifest.json` audit trail |

**MCP server:** Local FastAPI server (`mcp-server/`) — Docs append + Gmail draft  
**Safety:** Draft only (no auto-send); OAuth test-user gated

**Speaker note:** Emphasize **auditability**—reviewers can see tool names in transcript, not hidden scripts.

---

## Slide 8 — Quality Gates & Tradeoffs (Depth)

**Blocking validators before publish**

| Check | Pass criteria |
|-------|---------------|
| Word count | Body ≤ 250 words |
| PII | No email, handles, long digit runs |
| Quotes | Substring match to source CSV |
| Structure | 3 themes, 3 quotes, 3 actions |

**Known tradeoffs (shows depth)**

| Tradeoff | Decision |
|----------|----------|
| Groq free tier | Sample max 400 reviews; keyword fallback for rest |
| English heuristic | Fast filter; edge Hinglish may drop |
| Synthetic demo data | Pipeline proven; swap real exports for submission |

**Eval coverage:** Phases 0–3 signed off in `evals/TRACKING.md`

---

## Slide 9 — Success Metrics & Next Steps (Metrics)

**How we’d measure success in production**

| Metric | Target | Rationale |
|--------|--------|-----------|
| Time to weekly pulse | < 30 min operator time | Repeatable weekly ritual |
| Theme stability week-over-week | Top 3 overlap ≥ 2 | Signal vs noise |
| Low-star share on top theme | Track WoW delta | Early regression detection |
| Validation pass rate | 100% before MCP | Fail closed |
| Stakeholder read-through | Pulse used in weekly sync | Adoption, not vanity |

**Next:** Real store exports · Phase 4 live Doc URL · weekly automation script

---

## Slide 10 — Close (Communication)

**Headline:** A weekly ritual product teams can actually run

**Three takeaways**

1. **Decision-ready** — 3 themes, 3 quotes, 3 actions, not a sentiment blob  
2. **Grounded** — Every quote traceable; PII stripped at ingest  
3. **Repeatable & auditable** — Same pipeline every `week_of`; MCP delivery logged  

**Thank you — questions?**

---

## Appendix (optional, not counted in 9–10)

- Architecture diagram (full)
- ADR list (`decisions/001`–`008`)
- MCP smoke test screenshot
- Repo structure one-pager

---

## Rehearsal checklist

- [ ] 8–10 minutes total; no slide > 90 seconds  
- [ ] Every claim on slides 5–6 has a number from artifacts  
- [ ] Demo link ready (Google Doc URL after Phase 4)  
- [ ] Prepared answer: “Why MCP instead of googleapis in Python?”  
- [ ] Prepared answer: “How do you know quotes aren’t hallucinated?”
