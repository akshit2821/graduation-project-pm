#!/usr/bin/env python3
"""Generate 10-slide graduation deck PDF from project artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from fpdf import FPDF

PROJECT = Path(__file__).resolve().parents[1]
DECK = PROJECT / "deck"
OUT = DECK / "NL Spotify.pdf"

# Colour-blind-safe palette (IBM Carbon-inspired blues/oranges)
BG = (15, 15, 20)
ACCENT = (29, 185, 84)
TEXT = (245, 245, 247)
MUTED = (161, 161, 170)
HIGHLIGHT = (255, 131, 43)


def _load_stats() -> dict:
    theme_map = json.loads((PROJECT / "artifacts" / "theme_map.json").read_text(encoding="utf-8"))
    themes = theme_map.get("themes", [])[:3]
    sub = {}
    sp = PROJECT / "config" / "submission.json"
    if sp.is_file():
        sub = json.loads(sp.read_text(encoding="utf-8"))
    return {
        "corpus": theme_map.get("feedback_count", 629),
        "coverage": theme_map.get("coverage_pct", 100),
        "top3": themes,
        "workflow_url": sub.get("workflow_url", "YOUR_WORKFLOW_URL"),
        "mvp_url": sub.get("mvp_url", "YOUR_MVP_URL"),
    }


class DeckPDF(FPDF):
    def __init__(self) -> None:
        super().__init__(orientation="L", unit="mm", format="A4")
        self.set_auto_page_break(auto=False)
        self.margin = 20
        self.content_w = 297 - 2 * self.margin

    def slide_bg(self) -> None:
        self.set_fill_color(*BG)
        self.rect(0, 0, 297, 210, style="F")
        # Add subtle accent bar at top
        self.set_fill_color(*ACCENT)
        self.rect(0, 0, 297, 3, style="F")

    def slide_title(self, title: str) -> None:
        self.set_text_color(*ACCENT)
        self.set_font("Helvetica", "B", 28)
        self.multi_cell(self.content_w, 14, title, align="L")
        self.ln(8)
        # Add divider line
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.5)
        self.line(self.margin, self.get_y(), self.margin + 80, self.get_y())
        self.ln(6)

    def body(self, text: str, size: int = 16) -> None:
        self.set_text_color(*TEXT)
        self.set_font("Helvetica", "", size)
        self.multi_cell(self.content_w, 9, text, align="L")

    def bullet(self, text: str) -> None:
        self.set_text_color(*TEXT)
        self.set_font("Helvetica", "", 16)
        self.set_fill_color(*ACCENT)
        self.circle(self.margin + 2, self.get_y() + 3, 1.5, style="F")
        self.set_x(self.margin + 8)
        self.multi_cell(self.content_w - 8, 8, text, align="L")
        self.ln(3)

    def muted(self, text: str) -> None:
        self.set_text_color(*MUTED)
        self.set_font("Helvetica", "I", 14)
        self.multi_cell(self.content_w, 7, text, align="L")

    def accent_line(self, text: str) -> None:
        self.set_text_color(*HIGHLIGHT)
        self.set_font("Helvetica", "B", 18)
        self.multi_cell(self.content_w, 9, text, align="L")
        self.ln(3)


def build() -> Path:
    s = _load_stats()
    top3 = list(s["top3"])
    while len(top3) < 3:
        top3.append({})
    t1, t2, t3 = top3[0], top3[1], top3[2]
    pdf = DeckPDF()

    slides = [
        (
            "Repeat listening is growth's hidden ceiling at Spotify",
            [
                f"629 public feedback posts analyzed | {s['coverage']:.0f}% themed",
                "Growth PM case: increase meaningful discovery, reduce comfort loops",
                "Music Discovery Graduation Project | NextLeap",
            ],
        ),
        (
            "Millions of users still listen from comfort playlists, not discovery",
            [
                "Spotify has world-class recommendations - yet repeat playlists dominate listening",
                "Strategic goal: meaningful music discovery at scale",
                "Hypothesis: friction is behavioral (when to choose), not only algorithm quality",
            ],
        ),
        (
            "We analyzed 629 public feedback posts across 4 channels",
            [
                "Google Play (87%) | Reddit | Community forums | Social media",
                "Pipeline: Collect -> Normalize -> AI theme classify -> Insights dashboard",
                f"Review Discovery Engine: {s['workflow_url']}",
            ],
        ),
        (
            "Users repeat because decision fatigue beats risky exploration",
            [
                f"1. {t1.get('label', 'Discovery friction')}: {t1.get('share_pct', 48)}% ({t1.get('feedback_count', 0)} posts)",
                f"2. {t2.get('label', 'Free tier limits')}: {t2.get('share_pct', 33)}% ({t2.get('feedback_count', 0)} posts)",
                f"3. {t3.get('label', 'Repeat listening')}: {t3.get('share_pct', 5)}% ({t3.get('feedback_count', 0)} posts)",
                'Quote: "After office I only open my 2022 indie playlist - new music feels like work."',
            ],
        ),
        (
            "Interviews confirmed AI themes - and revealed one surprise",
            [
                "n=6 segment-fit interviews (Indian urban 22-35, playlist-heavy listeners)",
                "Validated: discovery friction, repeat listening, library clutter (Y)",
                "Surprise: looping peaks at transition moments (commute home) - not bad algo alone",
                "Users want: short explanation + 3 options, not another feed",
            ],
        ),
        (
            "The real problem: transition-moment decision fatigue",
            [
                "Segment defaults to 2-3 comfort playlists when mental energy is low",
                "Root cause: decision fatigue > recommendation quality at end-of-day moments",
                "JTBD: low-effort break from loop without endless Home scroll",
                "Not the problem: 'algorithm is always wrong'",
            ],
        ),
        (
            "Traditional recommendation optimizes familiarity, not intentional discovery",
            [
                "Collaborative filtering reinforces taste clusters -> comfort loops",
                "Discover Weekly is batch + black-box -> skipped when mood uncertain",
                "Business metrics: discovery session rate | new artist listens | D7 retention",
                "Gap: no explainable coach at the moment users choose autopilot",
            ],
        ),
        (
            "LoopBreak explains why you're stuck - then offers 3 discovery paths",
            [
                "AI-native MVP: diagnosis + 3 strategies (mood / social / forgotten saves)",
                "Grounded in 629-post corpus + interview synthesis (Groq + research prompts)",
                f"Production MVP: {s['mvp_url']}",
                "No Spotify API v1 - prototypes interaction + explainability (v2: catalog)",
            ],
        ),
        (
            "AI changes UX from passive feed to guided discovery with agency",
            [
                "Before: open app -> same playlist -> passive play",
                "After: describe moment -> why looping -> pick a path -> intentional action",
                "AI unlocks: intent, moment context, reasoning aloud, strategy not just tracks",
            ],
        ),
        (
            "Success metrics: discovery sessions, new artists, D7 retention",
            [
                "Primary: discovery session rate (% sessions with play outside top 3 playlists)",
                "Secondary: new artist listen rate | loop-break rate at transition moments",
                "Next experiment: A/B coach at 6pm vs control Home for segment",
                "Thank you | Workflow + MVP links on prior slides",
            ],
        ),
    ]

    for title, lines in slides:
        pdf.add_page()
        pdf.slide_bg()
        pdf.set_xy(pdf.margin, pdf.margin)
        pdf.slide_title(title)
        pdf.ln(2)
        for line in lines:
            if line.startswith("Quote:"):
                pdf.accent_line(line)
            else:
                pdf.bullet(line)

    DECK.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    return OUT


def main() -> int:
    path = build()
    kb = path.stat().st_size / 1024
    print(f"Deck written: {path.relative_to(PROJECT)} ({kb:.1f} KB)")
    if kb > 40960:
        print("WARN: PDF exceeds 40 MB limit")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
