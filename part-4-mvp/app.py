#!/usr/bin/env python3
"""LoopBreak — AI Discovery Coach (Part 4 MVP)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

MVP = Path(__file__).resolve().parent
sys.path.insert(0, str(MVP))
sys.path.insert(0, str(MVP.parent))

from coach import PERSONAS, generate_coach_response  # noqa: E402

CSS = """
<style>
  .block-container { padding-top: 1.5rem; max-width: 900px; }
  .hero h1 { font-size: 2rem; font-weight: 700; }
  .hero p { color: #A1A1AA; }
  .diagnosis {
    background: #16161D;
    border-left: 4px solid #1DB954;
    border-radius: 8px;
    padding: 1rem 1.1rem;
    margin: 1rem 0;
  }
  .path-card {
    background: #16161D;
    border: 1px solid #2A2A35;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    min-height: 120px;
  }
  .path-card h4 { margin: 0 0 0.4rem 0; color: #1ED760; }
  .action-box {
    background: linear-gradient(145deg, #1a2e1f 0%, #16161D 100%);
    border: 1px solid #1DB954;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-top: 1rem;
  }
  .tag { font-size: 0.75rem; color: #71717A; }
</style>
"""

TAG_LABELS = {
    "mood_shift": "Mood shift",
    "social": "Social discovery",
    "forgotten_save": "Forgotten saves",
    "new_artist": "New artist",
}


def main() -> None:
    st.set_page_config(page_title="LoopBreak", page_icon="🔁", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hero">
          <h1>LoopBreak</h1>
          <p>AI discovery coach for transition moments — explains why you're looping, then offers three paths forward.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        persona = st.selectbox(
            "Persona preset",
            options=[""] + list(PERSONAS.keys()),
            format_func=lambda x: "Custom only" if x == "" else x.replace("_", " ").title(),
        )
    with col2:
        default = PERSONAS.get(persona, "") if persona else ""
        context = st.text_area(
            "Your moment",
            value=default,
            height=100,
            placeholder="e.g. Friday 6pm, tired, only playing my old indie playlist…",
        )

    use_groq = st.checkbox("Use Groq AI (requires API key)", value=True, help="AI-powered responses using Groq. Uncheck to use cached sample responses.")
    if st.button("Break the loop", type="primary", use_container_width=True):
        if not context.strip() and not persona:
            st.warning("Describe your listening moment or pick a persona.")
        else:
            with st.spinner("Thinking…"):
                try:
                    result = generate_coach_response(
                        context,
                        persona_id=persona or None,
                        force_api=use_groq,
                    )
                    st.session_state["loopbreak_result"] = result
                except Exception as e:
                    st.error(str(e))

    result = st.session_state.get("loopbreak_result")
    if result:
        src = result.get("source", "")
        st.caption(f"Response via {src.replace('_', ' ')}")

        st.markdown("### Why you're looping")
        st.markdown(f'<div class="diagnosis">{result["why_looping"]}</div>', unsafe_allow_html=True)

        st.markdown("### Three discovery paths")
        cols = st.columns(3)
        for i, path in enumerate(result.get("discovery_paths", [])[:3]):
            tag = TAG_LABELS.get(path.get("action_tag", ""), path.get("action_tag", ""))
            with cols[i]:
                st.markdown(
                    f'<div class="path-card"><h4>{path.get("title", "Path")}</h4>'
                    f'<p>{path.get("description", "")}</p>'
                    f'<span class="tag">{tag}</span></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("### Recommended next action")
        st.markdown(
            f'<div class="action-box">{result.get("recommended_action", "")}</div>',
            unsafe_allow_html=True,
        )

    with st.expander("How LoopBreak differs from Spotify Home"):
        st.markdown(
            """
            **Traditional reco** ranks familiar tracks from history — great for session length, weak at breaking autopilot.

            **LoopBreak** uses research from 629 public feedback posts + user interviews:
            - Names *why* you're stuck (decision fatigue at transition moments)
            - Offers **strategies**, not an opaque feed
            - Keeps you in control — pick a path, not an algorithm
            """
        )


if __name__ == "__main__":
    main()
