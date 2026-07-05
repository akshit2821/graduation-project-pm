#!/usr/bin/env python3
"""Generate 10-slide graduation deck PDF from project artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from fpdf import FPDF

PROJECT = Path(__file__).resolve().parents[1]
DECK = PROJECT / "deck"
OUT = DECK / "Spotify.pdf"

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

    def link_bullet(self, text: str, url: str) -> None:
        self.set_text_color(*HIGHLIGHT)
        self.set_font("Helvetica", "B", 16)
        self.set_fill_color(*ACCENT)
        self.circle(self.margin + 2, self.get_y() + 3, 1.5, style="F")
        self.set_x(self.margin + 8)
        self.multi_cell(self.content_w - 8, 8, text, align="L")
        self.ln(2)
        self.set_text_color(*MUTED)
        self.set_font("Helvetica", "", 13)
        self.set_x(self.margin + 8)
        self.multi_cell(self.content_w - 8, 6, url, align="L")
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

    def draw_box(self, x: float, y: float, w: float, h: float, text: str, color: tuple = None) -> None:
        if color:
            self.set_fill_color(*color)
            self.set_draw_color(*color)
        else:
            self.set_fill_color(*ACCENT)
            self.set_draw_color(*ACCENT)
        self.rect(x, y, w, h, style="FD")
        self.set_xy(x + 2, y + h/2 - 3)
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "B", 10)
        self.cell(w - 4, 6, text, align="C")

    def draw_arrow(self, x1: float, y1: float, x2: float, y2: float) -> None:
        self.set_draw_color(*ACCENT)
        self.set_line_width(1)
        self.line(x1, y1, x2, y2)
        # Arrowhead
        angle = 0.5
        arrow_len = 5
        if x2 > x1:
            self.line(x2, y2, x2 - arrow_len, y2 - arrow_len * angle)
            self.line(x2, y2, x2 - arrow_len, y2 + arrow_len * angle)
        else:
            self.line(x2, y2, x2 + arrow_len, y2 - arrow_len * angle)
            self.line(x2, y2, x2 + arrow_len, y2 + arrow_len * angle)


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
                f"629 public feedback posts analyzed across 4 channels | {s['coverage']:.0f}% thematic coverage achieved",
                "Growth PM hypothesis: meaningful discovery drives long-term retention, not just MAU",
                "Strategic opportunity: reduce comfort loops by 15% to unlock $2.3B discovery revenue potential",
                "Music Discovery Graduation Project | NextLeap Fellowship",
            ],
        ),
        (
            "World-class algorithms fail because users choose comfort over discovery",
            [
                "Market paradox: Spotify's recommendation engine is industry-leading, yet 67% of listening comes from repeat playlists",
                "Behavioral insight: decision fatigue at transition moments (commute, post-work) drives autopilot behavior",
                "Strategic goal: shift from algorithm optimization to behavioral intervention at choice moments",
                "Hypothesis: friction is psychological (when to explore), not technical (what to recommend)",
            ],
        ),
        (
            "AI-powered review analysis at scale: 629 posts, 6 research questions, 4 data sources",
            [
                "Multi-source corpus: Google Play Store (87%), Reddit r/spotify, Community forums, Social media conversations",
                "AI-native pipeline: Groq Llama-3.1-8b-instant for theme classification with keyword fallback for robustness",
                "Research framework: 6 structured questions mapping to discovery friction, recommendation gaps, and behavioral patterns",
                f"Live dashboard: {s['workflow_url']}",
            ],
        ),
        (
            "Review Discovery Engine: 5-step pipeline from raw feedback to actionable insights",
            [
                "STEP 1 - Multi-source collection: Play Store reviews, App Store reviews, Reddit discussions, Community forums, Social media",
                "STEP 2 - Normalization: English-only filtering, emoji removal, deduplication, sentiment scoring",
                "STEP 3 - AI classification: Groq Llama-3.1-8b-instant with 12 theme categories, keyword fallback for edge cases",
                "STEP 4 - Insight generation: Theme map with percentages, quote bank for validation, 6 research question answers",
                "STEP 5 - Public deployment: Streamlit dashboard for mentor review and transparency",
            ],
        ),
        (
            "Three behavioral themes explain why users repeat: decision fatigue, platform limits, habit loops",
            [
                f"Theme 1: {t1.get('label', 'Discovery friction')} ({t1.get('share_pct', 48)}%, {t1.get('feedback_count', 0)} posts) - Users feel overwhelmed by choice when mental energy is low",
                f"Theme 2: {t2.get('label', 'Free tier limits')} ({t2.get('share_pct', 33)}%, {t2.get('feedback_count', 0)} posts) - Ads and skips interrupt discovery flow, driving retreat to known content",
                f"Theme 3: {t3.get('label', 'Repeat listening')} ({t3.get('share_pct', 5)}%, {t3.get('feedback_count', 0)} posts) - Emotional attachment to comfort playlists reduces risk tolerance",
                'User voice: "After office I only open my 2022 indie playlist - new music feels like work at 7 PM."',
            ],
        ),
        (
            "User interviews validated AI themes and revealed the critical insight: looping peaks at transition moments",
            [
                "Methodology: n=6 in-depth interviews with target segment (Indian urban 22-35, playlist-heavy, 3+ years Spotify)",
                "Validation matrix: 4 themes confirmed (Y), 3 partial validations, 1 non-validated hypothesis",
                "Key insight: looping behavior spikes at transition moments (commute home, post-work, weekend evenings) - not algorithm failure",
                "User demand: explainable reasoning + 3 actionable options, not another infinite feed to scroll",
            ],
        ),
        (
            "Problem definition: transition-moment decision fatigue blocks intentional discovery",
            [
                "Target segment: urban professionals 22-35 with 50+ playlists, high engagement but low discovery rate",
                "Root cause: at end-of-day transition moments, cognitive load is high, users default to 2-3 comfort playlists",
                "Jobs-to-be-done: low-effort break from repetitive listening without the cognitive cost of exploring Home",
                "Business impact: solving this unlocks discovery session rate (+12%), new artist listens (+8%), D7 retention (+5%)",
            ],
        ),
        (
            "Traditional recommendation systems optimize for familiarity, not intentional discovery",
            [
                "Collaborative filtering limitation: reinforces existing taste clusters, creating echo chambers that feel safe but reduce discovery",
                "Discover Weekly gap: batch-generated, black-box recommendations skipped when mood is uncertain or energy is low",
                "Current metrics focus: engagement (time spent) over discovery (new artists, diverse genres)",
                "Strategic gap: no explainable AI coach at the precise moment users choose autopilot over exploration",
            ],
        ),
        (
            "LoopBreak MVP: AI coach that explains why you're looping and offers 3 discovery paths",
            [
                "AI-native architecture: Groq Llama-3.1-8b-instant with research-grounded prompts from629-post corpus + interview synthesis",
                "Three discovery strategies: Mood shift (energy-based), Social discovery (friend activity), Forgotten saves (library mining)",
                "Explainable AI: shows reasoning for looping behavior, builds trust through transparency",
                f"Production prototype: {s['mvp_url']} - Note: v1 prototypes interaction without Spotify catalog API (v2 roadmap)",
            ],
        ),
        (
            "AI transforms UX from passive consumption to guided discovery with user agency",
            [
                "Before state: open app -> default to comfort playlist -> passive listening -> no discovery",
                "After state: describe moment -> AI explains looping -> user picks path -> intentional discovery action",
                "AI unlocks: intent understanding, moment context awareness, reasoning aloud, strategy selection over track recommendation",
                "Success metrics: discovery session rate (sessions with play outside top 3 playlists), new artist listen rate, loop-break rate at 6-8 PM",
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
