#!/usr/bin/env python3
"""Public Review Discovery Engine — Spotify user feedback intelligence."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from ui_helpers import format_window, rating_stars, source_label, theme_label

PROJECT = Path(__file__).resolve().parents[1]
ART = PROJECT / "artifacts"

CSS = """
<style>
  .block-container { padding-top: 1.5rem; max-width: 1100px; }
  .hero { margin-bottom: 1.25rem; }
  .hero h1 { font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem; }
  .hero p { color: #A1A1AA; font-size: 1.05rem; margin: 0; }
  .metric-card {
    background: linear-gradient(145deg, #16161D 0%, #1C1C24 100%);
    border: 1px solid #2A2A35;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    min-height: 96px;
  }
  .metric-card .label { color: #A1A1AA; font-size: 0.82rem; margin-bottom: 0.35rem; }
  .metric-card .value { font-size: 1.65rem; font-weight: 700; color: #F5F5F7; }
  .finding-card {
    background: #16161D;
    border-left: 4px solid #1DB954;
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.75rem;
  }
  .finding-card h4 { margin: 0 0 0.35rem 0; font-size: 1rem; }
  .finding-card p { margin: 0; color: #A1A1AA; font-size: 0.92rem; }
  .research-card {
    background: #16161D;
    border: 1px solid #2A2A35;
    border-radius: 12px;
    padding: 1rem 1.15rem;
    margin-bottom: 1rem;
  }
  .research-card h4 { margin: 0 0 0.5rem 0; font-size: 1.02rem; color: #F5F5F7; }
  .research-card .insight { color: #A1A1AA; font-size: 0.88rem; margin-bottom: 0.65rem; font-style: italic; }
  .research-stat { color: #D4D4D8; font-size: 0.9rem; margin: 0.2rem 0; padding-left: 0.5rem; border-left: 2px solid #1DB954; }
  .research-combined { color: #1ED760; font-size: 0.85rem; margin-top: 0.5rem; }
  .theme-bar-row { margin-bottom: 0.85rem; }
  .theme-bar-label { display: flex; justify-content: space-between; font-size: 0.92rem; margin-bottom: 0.25rem; }
  .theme-bar-track { background: #2A2A35; border-radius: 999px; height: 10px; overflow: hidden; }
  .theme-bar-fill { background: linear-gradient(90deg, #1DB954, #1ED760); height: 10px; border-radius: 999px; }
  .quote-card {
    background: #16161D;
    border: 1px solid #2A2A35;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-bottom: 0.85rem;
  }
  .quote-meta { color: #A1A1AA; font-size: 0.82rem; margin-bottom: 0.5rem; }
  .quote-text { font-size: 1rem; line-height: 1.5; margin: 0; }
  .badge {
    display: inline-block;
    background: #24242E;
    color: #D4D4D8;
    border-radius: 999px;
    padding: 0.15rem 0.55rem;
    font-size: 0.75rem;
    margin-right: 0.35rem;
  }
  .pipeline-step {
    background: #16161D;
    border: 1px solid #2A2A35;
    border-radius: 10px;
    padding: 0.85rem;
    text-align: center;
    min-height: 88px;
  }
  .pipeline-step strong { display: block; margin-bottom: 0.25rem; }
  .pipeline-step span { color: #A1A1AA; font-size: 0.85rem; }
  .footer-note { color: #71717A; font-size: 0.8rem; margin-top: 2rem; text-align: center; }
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  .stApp { background-color: #0E0E10; }
</style>
"""


@st.cache_data
def load_json(name: str):
    path = ART / name
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _theme_lookup(theme_map: dict) -> dict[str, dict]:
    return {t["id"]: t for t in theme_map.get("themes", [])}


def _render_theme_bars(themes: list[dict], highlight_ids: set[str] | None = None) -> None:
    highlight_ids = highlight_ids or set()
    for theme in themes:
        pct = theme.get("share_pct", 0)
        label = theme.get("label") or theme_label(theme.get("id"))
        accent = "#1ED760" if theme.get("id") in highlight_ids else "#1DB954"
        st.markdown(
            f"""
            <div class="theme-bar-row">
              <div class="theme-bar-label">
                <span>{label}</span>
                <span>{pct}% · {theme.get('feedback_count', 0)} posts</span>
              </div>
              <div class="theme-bar-track">
                <div class="theme-bar-fill" style="width:{min(pct, 100)}%; background:{accent};"></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_research_question(q: dict) -> None:
    st.markdown(f'<div class="research-card"><h4>{q["question"]}</h4>', unsafe_allow_html=True)
    if q.get("insight"):
        st.markdown(f'<p class="insight">{q["insight"]}</p>', unsafe_allow_html=True)

    if q.get("themes"):
        for t in q["themes"]:
            if not t:
                continue
            rating = f", avg {t['avg_rating']}/5" if t.get("avg_rating") is not None else ""
            st.markdown(
                f'<p class="research-stat"><strong>{t["label"]}</strong> — '
                f'{t["feedback_count"]} posts ({t["share_pct"]}%){rating}</p>',
                unsafe_allow_html=True,
            )
        if q.get("combined_post_count"):
            st.markdown(
                f'<p class="research-combined">Combined: {q["combined_post_count"]} posts '
                f'({q.get("combined_share_pct", 0)}% of corpus)</p>',
                unsafe_allow_html=True,
            )

    if q["id"] == "q5_segment_diff":
        if q.get("target_segment"):
            st.caption(f"Target segment: {q['target_segment']}")
        for seg in q.get("segments", [])[:8]:
            st.markdown(
                f'<p class="research-stat"><strong>{seg["segment_label"]}</strong> ({seg["count"]} posts) — '
                f'leading theme: {seg["top_theme_label"]} ({seg["top_theme_share_pct"]}%)</p>',
                unsafe_allow_html=True,
            )

    if q["id"] == "q6_unmet_needs":
        st.markdown("**Ranked unmet needs**")
        for t in q.get("top_needs", [])[:5]:
            if t:
                st.markdown(
                    f'<p class="research-stat">{t["label"]} — {t["share_pct"]}% ({t["feedback_count"]} posts)</p>',
                    unsafe_allow_html=True,
                )
        cross = q.get("cross_source_needs", [])
        if cross:
            st.markdown("**Consistent across multiple channels**")
            for row in cross[:5]:
                srcs = ", ".join(row.get("sources", []))
                st.markdown(
                    f'<p class="research-stat">{row["label"]} — {row["feedback_count"]} posts '
                    f'across {row["source_count"]} channels ({srcs})</p>',
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)


def _research_findings(research: dict | None) -> list[tuple[str, str]]:
    if not research:
        return []
    findings = []
    for q in research.get("questions", [])[:3]:
        if q.get("themes"):
            top = q["themes"][0]
            detail = f"{top['share_pct']}% — {top['label']}"
            if q.get("combined_share_pct"):
                detail += f" (combined signal {q['combined_share_pct']}%)"
            findings.append((q["question"], detail))
    return findings


def main() -> None:
    st.set_page_config(
        page_title="Spotify Review Discovery Engine",
        page_icon="🎧",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    theme_map = load_json("theme_map.json")
    source_bd = load_json("source_breakdown.json")
    quotes = load_json("quote_bank.json")
    research = load_json("research_answers.json")

    if not theme_map:
        st.markdown(
            """
            <div class="hero">
              <h1>Spotify Review Discovery Engine</h1>
              <p>Insights dashboard is not available yet. Please check back shortly.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    product = theme_map.get("product", "Spotify")
    count = theme_map.get("feedback_count", 0)
    coverage = theme_map.get("coverage_pct", 0)
    window = format_window(theme_map.get("window"))
    n_sources = len(source_bd.get("sources", {})) if source_bd else 0

    st.markdown(
        f"""
        <div class="hero">
          <h1>{product} Review Discovery Engine</h1>
          <p>Public user feedback analyzed at scale to understand music discovery friction and repeat listening.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="metric-card"><div class="label">Feedback analyzed</div><div class="value">{count:,}</div></div>',
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="metric-card"><div class="label">Themes identified</div><div class="value">{coverage:.0f}%</div></div>',
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="metric-card"><div class="label">Analysis period</div><div class="value" style="font-size:1.15rem">{window}</div></div>',
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f'<div class="metric-card"><div class="label">Channels</div><div class="value">{n_sources}</div></div>',
            unsafe_allow_html=True,
        )

    tab_overview, tab_research, tab_themes, tab_voices, tab_sources = st.tabs(
        ["Overview", "Research answers", "Themes", "User voices", "Sources"]
    )

    with tab_overview:
        st.subheader("Top findings")
        findings = _research_findings(research)
        if findings:
            for title, detail in findings:
                st.markdown(
                    f'<div class="finding-card"><h4>{title}</h4><p>{detail}</p></div>',
                    unsafe_allow_html=True,
                )
        else:
            by_id = _theme_lookup(theme_map)
            for tid in theme_map.get("top3_theme_ids") or []:
                t = by_id.get(tid)
                if t:
                    st.markdown(
                        f'<div class="finding-card"><h4>{t["label"]}</h4>'
                        f'<p>{t["share_pct"]}% of feedback ({t["feedback_count"]} posts)</p></div>',
                        unsafe_allow_html=True,
                    )

        if research and research.get("target_segment"):
            st.caption(f"Target segment: {research['target_segment']}")

        st.subheader("How it works")
        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(
                '<div class="pipeline-step"><strong>Collect</strong><span>App stores, Reddit, forums & social</span></div>',
                unsafe_allow_html=True,
            )
        with s2:
            st.markdown(
                '<div class="pipeline-step"><strong>Analyze</strong><span>Normalize text & classify discovery themes</span></div>',
                unsafe_allow_html=True,
            )
        with s3:
            st.markdown(
                '<div class="pipeline-step"><strong>Insights</strong><span>Rank themes, surface quotes & patterns</span></div>',
                unsafe_allow_html=True,
            )

    with tab_research:
        st.subheader("Six research questions")
        st.caption("Aligned with the graduation problem statement — multi-theme analysis with segment splits.")
        if research and research.get("questions"):
            for q in research["questions"]:
                _render_research_question(q)

            rq = (quotes or {}).get("research_quotes") or []
            if rq:
                st.subheader("Evidence quotes")
                for item in rq:
                    stars = rating_stars(item.get("rating"))
                    meta = f'<span class="badge">{item.get("theme_label", "")}</span>'
                    meta += f'<span class="badge">{item.get("source_label", "")}</span>'
                    if stars:
                        meta += f' <span class="badge">{stars}</span>'
                    st.markdown(
                        f'<div class="quote-card"><div class="quote-meta">{meta}</div>'
                        f'<p class="quote-text"><em>{item.get("research_question", "")}</em></p>'
                        f'<p class="quote-text">"{item.get("text", "")}"</p></div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.info("Research answers not available. Re-run the analysis pipeline.")

    with tab_themes:
        themes = theme_map.get("themes", [])
        top_ids = set(theme_map.get("top3_theme_ids") or [])
        if themes:
            _render_theme_bars(themes, highlight_ids=top_ids)
        else:
            st.info("No theme data available.")

    with tab_voices:
        items = quotes.get("quotes", []) if quotes else []
        if items:
            for q in items:
                label = q.get("theme_label") or theme_label(q.get("theme_id"))
                src = q.get("source_label") or source_label(q.get("source"))
                stars = rating_stars(q.get("rating"))
                meta = f'<span class="badge">{label}</span><span class="badge">{src}</span>'
                if stars:
                    meta += f' <span class="badge">{stars}</span>'
                st.markdown(
                    f'<div class="quote-card"><div class="quote-meta">{meta}</div><p class="quote-text">"{q["text"]}"</p></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No representative quotes available yet.")

    with tab_sources:
        if source_bd and source_bd.get("sources"):
            rows = []
            for key, info in sorted(
                source_bd["sources"].items(), key=lambda x: x[1]["count"], reverse=True
            ):
                rows.append(
                    {
                        "Channel": source_label(key),
                        "Posts": info["count"],
                        "Share": f"{info['pct']}%",
                    }
                )
            st.dataframe(rows, use_container_width=True, hide_index=True)

            by_source = theme_map.get("by_source", {})
            if by_source:
                st.subheader("Top theme by channel")
                for key, info in sorted(by_source.items(), key=lambda x: x[1]["count"], reverse=True):
                    top = theme_label(info.get("top_theme"))
                    st.markdown(f"**{source_label(key)}** — {info['count']} posts · leading theme: *{top}*")
        else:
            st.info("Source breakdown not available.")

    st.markdown(
        '<p class="footer-note">Built from publicly available user feedback · Growth PM research workflow</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
