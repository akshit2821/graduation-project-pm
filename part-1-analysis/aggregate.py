#!/usr/bin/env python3
"""Build theme_map, source_breakdown, insight_report, quote_bank, research_answers."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

THEME_LABELS = {
    "discovery_friction": "Hard to find new music",
    "bad_recommendations": "Recommendation products miss",
    "repeat_listening": "Same content on loop",
    "library_clutter": "Library too large to explore",
    "ui_complexity": "UI blocks exploration",
    "social_discovery": "Wants shared discovery",
    "podcast_vs_music": "Podcasts crowd out music",
    "pricing_ads": "Free tier limits exploration",
}

SOURCE_NAMES = {
    "play_store": "Google Play",
    "app_store": "App Store",
    "reddit": "Reddit",
    "forum": "Community forums",
    "social": "Social media",
    "web": "Web",
}

PLATFORM_NAMES = {
    "android": "Android",
    "ios": "iOS",
    "web": "Web",
}

# Maps each problem-statement research question to relevant themes + narrative hint.
QUESTION_SPECS = [
    {
        "id": "q1_discovery_struggle",
        "question": "Why do users struggle to discover new music?",
        "theme_ids": ["discovery_friction", "library_clutter", "ui_complexity"],
        "insight": "Discovery pain comes from choice overload, cluttered UI, and libraries too large to browse—not only bad picks.",
    },
    {
        "id": "q2_reco_frustration",
        "question": "What are the most common frustrations with recommendations?",
        "theme_ids": ["bad_recommendations", "pricing_ads", "ui_complexity"],
        "insight": "Recommendation frustration includes stale or irrelevant picks, but also ads and UI changes that interrupt exploration.",
    },
    {
        "id": "q3_listening_behavior",
        "question": "What listening behaviors are users trying to achieve?",
        "theme_ids": ["repeat_listening", "social_discovery", "podcast_vs_music"],
        "insight": "Users describe comfort loops, shared discovery with friends, and balancing podcasts vs music—not always seeking novelty.",
    },
    {
        "id": "q4_repeat_causes",
        "question": "What causes users to repeatedly listen to the same content?",
        "theme_ids": ["repeat_listening", "pricing_ads", "library_clutter", "discovery_friction"],
        "insight": "Repeat listening is driven by habit, ad friction when browsing, oversized libraries, and decision fatigue when choosing something new.",
    },
    {
        "id": "q5_segment_diff",
        "question": "Which user segments experience different discovery challenges?",
        "theme_ids": [],
        "insight": "Patterns differ by feedback channel, star rating, and platform—detractors cite ads and loops; promoters still report discovery friction.",
    },
    {
        "id": "q6_unmet_needs",
        "question": "What unmet needs emerge consistently across reviews?",
        "theme_ids": [],
        "insight": "Needs that appear across multiple channels are the strongest signals for product action.",
    },
]


def _format_theme_stat(t: dict | None) -> dict | None:
    if not t:
        return None
    return {
        "theme_id": t["id"],
        "label": t["label"],
        "feedback_count": t["feedback_count"],
        "share_pct": t["share_pct"],
        "avg_rating": t.get("avg_rating"),
    }


def build_theme_map(
    assignments: pd.DataFrame,
    feedback: pd.DataFrame,
    cfg: dict,
    ingest_report: dict | None,
) -> dict:
    valid = set(THEME_LABELS.keys())
    assignments = assignments[assignments["theme_id"].isin(valid)].copy()
    merged = assignments.merge(feedback, on="feedback_id", how="left")
    total = len(feedback)
    assigned = len(assignments)

    themes = []
    for tid in sorted(valid):
        sub = assignments[assignments["theme_id"] == tid]
        count = len(sub)
        if count == 0:
            continue
        m = sub.merge(feedback[["feedback_id", "rating"]], on="feedback_id", how="left")
        ratings = pd.to_numeric(m["rating"], errors="coerce")
        avg = float(ratings.mean()) if ratings.notna().any() else None
        themes.append(
            {
                "id": tid,
                "label": THEME_LABELS[tid],
                "feedback_count": count,
                "share_pct": round(100.0 * count / assigned, 1) if assigned else 0.0,
                "avg_rating": round(avg, 2) if avg is not None and not pd.isna(avg) else None,
                "sample_feedback_ids": sub["feedback_id"].head(3).tolist(),
            }
        )

    themes.sort(key=lambda x: x["feedback_count"], reverse=True)
    top3 = [t["id"] for t in themes[:3]]
    while len(top3) < 3 and themes:
        for t in themes:
            if t["id"] not in top3:
                top3.append(t["id"])
            if len(top3) >= 3:
                break

    by_source = {}
    if len(merged):
        for src, grp in merged.groupby("source"):
            top = grp["theme_id"].value_counts().index[0] if len(grp) else None
            by_source[src] = {
                "count": len(grp),
                "top_theme": top,
                "top_theme_label": THEME_LABELS.get(top, top),
            }

    window = {}
    if ingest_report:
        window = {"start": ingest_report.get("date_min"), "end": ingest_report.get("date_max")}

    return {
        "product": cfg.get("product_name"),
        "window": window,
        "feedback_count": total,
        "assigned_count": assigned,
        "coverage_pct": round(100.0 * assigned / total, 1) if total else 0.0,
        "themes": themes,
        "top3_theme_ids": top3[:3],
        "by_source": by_source,
    }


def build_source_breakdown(feedback: pd.DataFrame) -> dict:
    counts = feedback["source"].value_counts().to_dict()
    total = len(feedback)
    return {
        "total": total,
        "sources": {k: {"count": int(v), "pct": round(100 * v / total, 1)} for k, v in counts.items()},
    }


def _segment_top_theme(sub: pd.DataFrame) -> tuple[str | None, str | None, float]:
    if sub.empty:
        return None, None, 0.0
    top_id = sub["theme_id"].value_counts().index[0]
    share = round(100.0 * (sub["theme_id"] == top_id).sum() / len(sub), 1)
    return top_id, THEME_LABELS.get(top_id, top_id), share


def _build_segment_slices(merged: pd.DataFrame) -> list[dict]:
    slices: list[dict] = []

    for src, grp in merged.groupby("source"):
        top_id, top_label, share = _segment_top_theme(grp)
        slices.append(
            {
                "segment_type": "channel",
                "segment_label": SOURCE_NAMES.get(str(src), str(src).replace("_", " ").title()),
                "count": int(len(grp)),
                "top_theme_id": top_id,
                "top_theme_label": top_label,
                "top_theme_share_pct": share,
            }
        )

    ratings = pd.to_numeric(merged["rating"], errors="coerce")
    merged = merged.copy()
    merged["_rating"] = ratings
    for seg_id, label, lo, hi in [
        ("rating_detractors", "Low ratings (1–2 stars)", 1, 2),
        ("rating_neutral", "Mid ratings (3 stars)", 3, 3),
        ("rating_promoters", "High ratings (4–5 stars)", 4, 5),
    ]:
        sub = merged[merged["_rating"].between(lo, hi)]
        if sub.empty:
            continue
        top_id, top_label, share = _segment_top_theme(sub)
        slices.append(
            {
                "segment_type": "rating_band",
                "segment_id": seg_id,
                "segment_label": label,
                "count": int(len(sub)),
                "top_theme_id": top_id,
                "top_theme_label": top_label,
                "top_theme_share_pct": share,
            }
        )

    if "platform" in merged.columns:
        for plat, grp in merged.groupby("platform"):
            if pd.isna(plat) or str(plat).strip() == "":
                continue
            top_id, top_label, share = _segment_top_theme(grp)
            slices.append(
                {
                    "segment_type": "platform",
                    "segment_label": PLATFORM_NAMES.get(str(plat), str(plat).title()),
                    "count": int(len(grp)),
                    "top_theme_id": top_id,
                    "top_theme_label": top_label,
                    "top_theme_share_pct": share,
                }
            )

    slices.sort(key=lambda x: x["count"], reverse=True)
    return slices


def _cross_source_needs(merged: pd.DataFrame, theme_by_id: dict[str, dict], min_sources: int = 2) -> list[dict]:
    rows = []
    for tid, label in THEME_LABELS.items():
        sub = merged[merged["theme_id"] == tid]
        if sub.empty:
            continue
        sources = sorted(sub["source"].unique().tolist())
        if len(sources) < min_sources:
            continue
        t = theme_by_id.get(tid, {})
        rows.append(
            {
                "theme_id": tid,
                "label": label,
                "feedback_count": int(len(sub)),
                "share_pct": t.get("share_pct", 0),
                "source_count": len(sources),
                "sources": [SOURCE_NAMES.get(s, s) for s in sources],
            }
        )
    rows.sort(key=lambda x: x["feedback_count"], reverse=True)
    return rows


def build_research_answers(
    assignments: pd.DataFrame,
    feedback: pd.DataFrame,
    theme_map: dict,
    cfg: dict,
) -> dict:
    merged = assignments.merge(feedback, on="feedback_id", how="inner")
    theme_by_id = {t["id"]: t for t in theme_map.get("themes", [])}
    assigned = theme_map.get("assigned_count") or len(assignments)
    segment_slices = _build_segment_slices(merged)
    cross_source = _cross_source_needs(merged, theme_by_id)

    questions = []
    for spec in QUESTION_SPECS:
        entry: dict = {
            "id": spec["id"],
            "question": spec["question"],
            "insight": spec["insight"],
        }

        if spec["theme_ids"]:
            theme_stats = []
            combined_count = 0
            for tid in spec["theme_ids"]:
                t = theme_by_id.get(tid)
                if t:
                    theme_stats.append(_format_theme_stat(t))
                    combined_count += t["feedback_count"]
            entry["themes"] = theme_stats
            entry["combined_post_count"] = combined_count
            entry["combined_share_pct"] = round(100.0 * combined_count / assigned, 1) if assigned else 0.0

        if spec["id"] == "q5_segment_diff":
            entry["segments"] = segment_slices
            entry["target_segment"] = cfg.get("target_segment", {}).get("description")

        if spec["id"] == "q6_unmet_needs":
            entry["top_needs"] = [_format_theme_stat(t) for t in theme_map.get("themes", [])[:8]]
            entry["cross_source_needs"] = cross_source

        questions.append(entry)

    return {
        "product": theme_map.get("product"),
        "corpus_size": theme_map.get("feedback_count"),
        "coverage_pct": theme_map.get("coverage_pct"),
        "target_segment": cfg.get("target_segment", {}).get("description"),
        "questions": questions,
    }


def write_insight_report(research: dict, source_breakdown: dict, path: Path) -> None:
    lines = ["# Insight report", ""]
    lines.append(f"**Corpus:** {research.get('corpus_size')} posts")
    lines.append(f"**Coverage:** {research.get('coverage_pct')}% themed")
    if research.get("target_segment"):
        lines.append(f"**Target segment:** {research['target_segment']}")
    lines.append("")

    for q in research.get("questions", []):
        lines.append(f"## {q['question']}")
        if q.get("insight"):
            lines.append(f"*{q['insight']}*")
            lines.append("")

        if q.get("themes"):
            for t in q["themes"]:
                if not t:
                    continue
                line = f"- **{t['label']}**: {t['feedback_count']} posts ({t['share_pct']}%)"
                if t.get("avg_rating") is not None:
                    line += f", avg rating {t['avg_rating']}"
                lines.append(line)
            lines.append(
                f"- *Combined signal:* {q.get('combined_post_count', 0)} posts "
                f"({q.get('combined_share_pct', 0)}% of themed corpus)"
            )

        elif q["id"] == "q5_segment_diff":
            if q.get("target_segment"):
                lines.append(f"- **Target research segment:** {q['target_segment']}")
            for seg in q.get("segments", []):
                lines.append(
                    f"- **{seg['segment_label']}** ({seg['count']} posts): "
                    f"top theme *{seg['top_theme_label']}* ({seg['top_theme_share_pct']}% of segment)"
                )

        elif q["id"] == "q6_unmet_needs":
            lines.append("**Ranked unmet needs (full corpus):**")
            for t in q.get("top_needs", []):
                if t:
                    lines.append(f"- **{t['label']}** — {t['share_pct']}% ({t['feedback_count']} posts)")
            lines.append("")
            lines.append("**Consistent across multiple channels (≥2 sources):**")
            for row in q.get("cross_source_needs", []):
                srcs = ", ".join(row["sources"])
                lines.append(
                    f"- **{row['label']}** — {row['feedback_count']} posts in {row['source_count']} channels ({srcs})"
                )

        lines.append("")

    lines.append("## Source breakdown")
    for src, info in source_breakdown.get("sources", {}).items():
        name = SOURCE_NAMES.get(src, src.replace("_", " ").title())
        lines.append(f"- {name}: {info['count']} ({info['pct']}%)")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def select_quotes(
    feedback: pd.DataFrame,
    assignments: pd.DataFrame,
    top3: list[str],
    max_words: int = 25,
    per_theme: int = 2,
) -> list[dict]:
    merged = assignments.merge(feedback, on="feedback_id", how="inner")
    quotes = []
    for tid in top3:
        pool = merged[merged["theme_id"] == tid].copy()
        if pool.empty:
            continue
        pool["rating"] = pd.to_numeric(pool["rating"], errors="coerce").fillna(3)
        if "upvotes" in pool.columns:
            pool["_score"] = pool["upvotes"].fillna(0)
            pool = pool.sort_values(["rating", "_score"], ascending=[True, False])
        else:
            pain = pool[pool["rating"] <= 3]
            pool = pain if not pain.empty else pool
        for _, row in pool.head(per_theme).iterrows():
            words = str(row["text"]).split()[:max_words]
            quotes.append(
                {
                    "theme_id": tid,
                    "theme_label": THEME_LABELS.get(tid, tid),
                    "source": row.get("source"),
                    "source_label": SOURCE_NAMES.get(
                        str(row.get("source")),
                        str(row.get("source", "")).replace("_", " ").title(),
                    ),
                    "text": " ".join(words),
                    "rating": int(row["rating"]) if pd.notna(row["rating"]) else None,
                }
            )
    return quotes


def select_research_quotes(
    feedback: pd.DataFrame,
    assignments: pd.DataFrame,
    research: dict,
    max_words: int = 28,
) -> list[dict]:
    """One illustrative quote per research question (from mapped themes)."""
    merged = assignments.merge(feedback, on="feedback_id", how="inner")
    seen_text: set[str] = set()
    quotes = []

    for q in research.get("questions", []):
        theme_ids = [t["theme_id"] for t in q.get("themes", []) if t]
        if not theme_ids and q["id"] == "q5_segment_diff":
            theme_ids = ["discovery_friction", "pricing_ads"]
        if not theme_ids and q["id"] == "q6_unmet_needs":
            theme_ids = [t["theme_id"] for t in q.get("top_needs", [])[:2] if t]

        picked = None
        for tid in theme_ids:
            pool = merged[merged["theme_id"] == tid].copy()
            if pool.empty:
                continue
            pool["rating"] = pd.to_numeric(pool["rating"], errors="coerce").fillna(3)
            if "upvotes" in pool.columns:
                pool["_score"] = pool["upvotes"].fillna(0)
                pool = pool.sort_values(["rating", "_score"], ascending=[True, False])
            else:
                pain = pool[pool["rating"] <= 3]
                pool = pain if not pain.empty else pool
            for _, row in pool.iterrows():
                text = " ".join(str(row["text"]).split()[:max_words])
                if text in seen_text:
                    continue
                seen_text.add(text)
                picked = {
                    "research_question_id": q["id"],
                    "research_question": q["question"],
                    "theme_id": tid,
                    "theme_label": THEME_LABELS.get(tid, tid),
                    "source": row.get("source"),
                    "source_label": SOURCE_NAMES.get(
                        str(row.get("source")),
                        str(row.get("source", "")).replace("_", " ").title(),
                    ),
                    "text": text,
                    "rating": int(row["rating"]) if pd.notna(row["rating"]) else None,
                }
                break
            if picked:
                break
        if picked:
            quotes.append(picked)
    return quotes
