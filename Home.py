#!/usr/bin/env python3
"""Graduation submission portal — both deliverables in one Streamlit app."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

PROJECT = Path(__file__).resolve().parent
SUB = PROJECT / "config" / "submission.json"


def _urls() -> dict:
    if SUB.is_file():
        return json.loads(SUB.read_text(encoding="utf-8"))
    return {}


def main() -> None:
    st.set_page_config(page_title="Spotify Music Discovery — Submission", layout="wide", page_icon="🎧")
    cfg = _urls()

    st.title("Music Discovery Graduation Project")
    st.caption("Spotify Growth PM · NextLeap · Parts 1–4")

    st.markdown(
        """
        This portal links both submission deliverables:

        1. **Review Discovery Engine** — AI analysis of 629 public feedback posts
        2. **LoopBreak MVP** — AI discovery coach for transition moments
        """
    )

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Deliverable 1")
        st.markdown("Review Analysis Workflow")
        wf = cfg.get("workflow_url", "")
        if wf and not wf.startswith("REPLACE"):
            st.link_button("Open Review Discovery Engine", wf, use_container_width=True)
        else:
            st.info("Use sidebar: **Review Discovery Engine** (or deploy and set workflow_url in config/submission.json)")
    with c2:
        st.subheader("Deliverable 3")
        st.markdown("LoopBreak AI MVP")
        mvp = cfg.get("mvp_url", "")
        if mvp and not mvp.startswith("REPLACE"):
            st.link_button("Open LoopBreak MVP", mvp, use_container_width=True)
        else:
            st.info("Use sidebar: **LoopBreak MVP** (or deploy and set mvp_url in config/submission.json)")

    st.divider()
    st.markdown("**Deck:** `deck/NL Spotify.pdf` · **Deadline:** 6 July 2026, 3:59 PM IST")
    pdf = PROJECT / "deck" / "NL Spotify.pdf"
    if pdf.is_file():
        st.success(f"Deck found ({pdf.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
