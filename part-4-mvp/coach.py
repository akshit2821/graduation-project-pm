"""LoopBreak coach — research-grounded LLM responses with offline fallback."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

MVP = Path(__file__).resolve().parent
PROJECT = MVP.parent
sys.path.insert(0, str(PROJECT))

from lib.llm_client import chat_completion, api_enabled  # noqa: E402

PERSONAS = {
    "post_work": "Friday 6pm, tired after work, only playing my 2022 indie comfort playlist",
    "commute": "Daily commute, autopilot, same driving playlist every day, never open Discover Weekly",
    "library_overwhelm": "1000+ liked songs but I only play the same ten; library feels like a graveyard",
    "free_tier_ads": "Free tier — when ads hit while browsing I go back to what I know",
}


def _read(path: Path, max_chars: int = 2500) -> str:
    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8")
    return text[:max_chars] + ("…" if len(text) > max_chars else "")


def load_research_context() -> str:
    parts = []
    ir = _read(PROJECT / "artifacts" / "insight_report.md", 1800)
    if ir:
        parts.append("### Insight report excerpt\n" + ir)
    syn = _read(PROJECT / "part-2-research" / "interview_synthesis.md", 1200)
    if syn:
        parts.append("### Interview synthesis excerpt\n" + syn)
    tm = PROJECT / "artifacts" / "theme_map.json"
    if tm.is_file():
        data = json.loads(tm.read_text(encoding="utf-8"))
        top = data.get("themes", [])[:5]
        lines = [f"- {t['label']}: {t['share_pct']}%" for t in top]
        parts.append("### Top corpus themes\n" + "\n".join(lines))
    ps = _read(PROJECT / "part-3-problem" / "problem_statement.md", 800)
    if ps:
        parts.append("### Problem focus\n" + ps)
    return "\n\n".join(parts)


def _load_system_prompt() -> str:
    template = (MVP / "prompts" / "system.md").read_text(encoding="utf-8")
    return template.replace("{{RESEARCH_CONTEXT}}", load_research_context())


def _parse_json_response(raw: str) -> dict:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    data = json.loads(text)
    required = ("why_looping", "discovery_paths", "recommended_action")
    for key in required:
        if key not in data:
            raise ValueError(f"Missing key: {key}")
    paths = data["discovery_paths"]
    if not isinstance(paths, list) or len(paths) < 3:
        raise ValueError("discovery_paths must have at least 3 items")
    return data


def _fallback(persona_id: str | None, user_context: str) -> dict:
    fixtures = json.loads((MVP / "fixtures" / "sample_responses.json").read_text(encoding="utf-8"))
    if persona_id:
        for item in fixtures:
            if item.get("persona_id") == persona_id:
                out = {k: v for k, v in item.items() if k != "persona_id"}
                out["source"] = "research_fixture"
                return out
    return {k: v for k, v in fixtures[0].items() if k != "persona_id"} | {
        "source": "research_fixture",
    }


def generate_coach_response(
    user_context: str,
    persona_id: str | None = None,
    *,
    force_api: bool = False,
) -> dict:
    context = user_context.strip() or PERSONAS.get(persona_id or "", "")
    if not context:
        raise ValueError("Provide user context or select a persona")

    if not api_enabled(force=force_api):
        out = _fallback(persona_id, context)
        out["user_context"] = context
        return out

    system = _load_system_prompt()
    user_msg = f"User context:\n{context}\n\nReturn JSON only."
    try:
        raw = chat_completion(
            [{"role": "system", "content": system}, {"role": "user", "content": user_msg}],
            temperature=0.3,
            max_tokens=1024,
            force_api=force_api,
        )
        data = _parse_json_response(raw)
        data["source"] = "groq"
        data["user_context"] = context
        return data
    except Exception:
        out = _fallback(persona_id, context)
        out["user_context"] = context
        out["source"] = "research_fixture_fallback"
        return out
