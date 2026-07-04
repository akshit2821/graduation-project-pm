#!/usr/bin/env python3
"""Classify feedback via Groq (batched) with keyword fallback."""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import pandas as pd

ANALYSIS = Path(__file__).resolve().parent
PROJECT = ANALYSIS.parent
sys.path.insert(0, str(PROJECT))

from lib.llm_client import api_enabled, chat_completion, env_file_path, get_llm_model  # noqa: E402
from keyword_fallback import classify_keyword  # noqa: E402

VALID_THEMES = {
    "discovery_friction",
    "bad_recommendations",
    "repeat_listening",
    "library_clutter",
    "ui_complexity",
    "social_discovery",
    "podcast_vs_music",
    "pricing_ads",
}

JSONL_RE = re.compile(
    r'\{\s*"(?:feedback_id|review_id)"\s*:\s*"[^"]+"\s*,\s*"theme_id"\s*:\s*"[^"]+"\s*\}'
)


def _load_prompt_header() -> str:
    return (ANALYSIS / "prompts" / "classify_themes.md").read_text(encoding="utf-8")


def _parse_jsonl(content: str) -> list[dict]:
    rows = []
    for m in JSONL_RE.finditer(content):
        try:
            obj = json.loads(m.group(0))
            fid = obj.get("feedback_id") or obj.get("review_id")
            tid = obj.get("theme_id")
            if fid and tid in VALID_THEMES:
                rows.append({"feedback_id": fid, "theme_id": tid})
        except json.JSONDecodeError:
            continue
    if rows:
        return rows
    for line in content.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
            fid = obj.get("feedback_id") or obj.get("review_id")
            tid = obj.get("theme_id")
            if fid and tid in VALID_THEMES:
                rows.append({"feedback_id": fid, "theme_id": tid})
        except json.JSONDecodeError:
            continue
    return rows


def _batch_df(df: pd.DataFrame, size: int) -> list[pd.DataFrame]:
    return [df.iloc[i : i + size] for i in range(0, len(df), size)]


def _format_batch(batch: pd.DataFrame) -> str:
    lines = []
    for _, r in batch.iterrows():
        rating = r["rating"]
        lines.append(
            json.dumps(
                {
                    "feedback_id": r["feedback_id"],
                    "rating": int(rating) if pd.notna(rating) else None,
                    "source": str(r.get("source", "")),
                    "title": str(r.get("title", ""))[:80],
                    "text": str(r["text"])[:400],
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(lines)


def classify_batch_groq(batch: pd.DataFrame, prompt_header: str, *, force_api: bool) -> list[dict]:
    user = prompt_header + "\n" + _format_batch(batch)
    content = chat_completion(
        [
            {"role": "system", "content": "You output JSON Lines only. No markdown."},
            {"role": "user", "content": user},
        ],
        temperature=0.0,
        max_tokens=2048,
        force_api=force_api,
    )
    parsed = _parse_jsonl(content)
    by_id = {r["feedback_id"]: r["theme_id"] for r in parsed}
    out = []
    for _, r in batch.iterrows():
        fid = r["feedback_id"]
        tid = by_id.get(fid)
        if tid not in VALID_THEMES:
            tid = classify_keyword(str(r["text"]), str(r.get("title", "")))
        out.append({"feedback_id": fid, "theme_id": tid})
    return out


def classify_all(
    feedback: pd.DataFrame,
    *,
    batch_size: int = 25,
    force_api: bool = False,
    llm_ids: set[str] | None = None,
) -> tuple[pd.DataFrame, dict]:
    prompt_header = _load_prompt_header()
    use_groq = api_enabled(force=force_api)

    if llm_ids is not None:
        groq_df = feedback[feedback["feedback_id"].astype(str).isin(llm_ids)].copy()
        kw_df = feedback[~feedback["feedback_id"].astype(str).isin(llm_ids)].copy()
    else:
        groq_df = feedback
        kw_df = feedback.iloc[0:0].copy()

    all_rows: list[dict] = []
    batches = _batch_df(groq_df, batch_size)
    groq_batches = 0
    groq_errors: list[str] = []

    for batch in batches:
        if use_groq and len(batch) > 0:
            try:
                rows = classify_batch_groq(batch, prompt_header, force_api=force_api)
                groq_batches += 1
                time.sleep(2.5)
            except RuntimeError as e:
                groq_errors.append(str(e)[:200])
                rows = [
                    {
                        "feedback_id": r["feedback_id"],
                        "theme_id": classify_keyword(str(r["text"]), str(r.get("title", ""))),
                    }
                    for _, r in batch.iterrows()
                ]
        else:
            rows = [
                {
                    "feedback_id": r["feedback_id"],
                    "theme_id": classify_keyword(str(r["text"]), str(r.get("title", ""))),
                }
                for _, r in batch.iterrows()
            ]
        all_rows.extend(rows)

    if len(kw_df) > 0:
        all_rows.extend(
            {
                "feedback_id": r["feedback_id"],
                "theme_id": classify_keyword(str(r["text"]), str(r.get("title", ""))),
            }
            for _, r in kw_df.iterrows()
        )

    df = pd.DataFrame(all_rows)
    meta = {
        "classifier": "groq" if groq_batches > 0 else "keyword_fallback",
        "model": get_llm_model() if groq_batches > 0 else None,
        "env_file": str(env_file_path()),
        "groq_batches": groq_batches,
        "groq_errors": groq_errors[:5],
        "llm_review_count": len(groq_df),
        "keyword_review_count": len(kw_df),
    }
    return df, meta
