#!/usr/bin/env python3
"""Stratified feedback sampling for Groq classification (free-tier cost control)."""

from __future__ import annotations

import pandas as pd

DEFAULT_MIN_REVIEWS = 300
DEFAULT_MAX_REVIEWS = 400
ABSOLUTE_MAX = 500


def _id_column(df: pd.DataFrame) -> str:
    if "feedback_id" in df.columns:
        return "feedback_id"
    if "review_id" in df.columns:
        return "review_id"
    raise ValueError("DataFrame needs feedback_id or review_id column")


def clamp_llm_cap(value: int, *, min_reviews: int = DEFAULT_MIN_REVIEWS) -> int:
    lo = max(1, min_reviews)
    hi = ABSOLUTE_MAX
    return max(lo, min(int(value), hi))


def select_llm_review_ids(
    reviews: pd.DataFrame,
    *,
    max_reviews: int = DEFAULT_MAX_REVIEWS,
    min_reviews: int = DEFAULT_MIN_REVIEWS,
    seed: int = 42,
) -> tuple[set[str], dict]:
    """Pick up to max_reviews for Groq; stratified by rating + platform/source."""
    cap = clamp_llm_cap(max_reviews, min_reviews=min_reviews)
    id_col = _id_column(reviews)
    total = len(reviews)
    meta: dict = {
        "total_reviews": total,
        "max_reviews": cap,
        "min_reviews": min_reviews,
        "sampled": False,
        "seed": seed,
        "llm_review_count": total,
        "keyword_review_count": 0,
    }

    if total == 0:
        return set(), meta

    if total <= cap:
        return set(reviews[id_col].astype(str).tolist()), meta

    meta["sampled"] = True
    df = reviews.copy()
    df[id_col] = df[id_col].astype(str)
    df["_rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(3).astype(int).clip(1, 5)
    if "platform" in df.columns:
        df["_platform"] = df["platform"].fillna("unknown").astype(str)
    elif "source" in df.columns:
        df["_platform"] = df["source"].fillna("unknown").astype(str)
    else:
        df["_platform"] = "unknown"
    df["_strata"] = df["_rating"].astype(str) + "|" + df["_platform"].astype(str)

    strata_counts = df["_strata"].value_counts()
    quotas = (strata_counts / total * cap).round().astype(int)
    while int(quotas.sum()) > cap:
        quotas[quotas.idxmax()] -= 1
    while int(quotas.sum()) < cap:
        quotas[quotas.idxmin()] += 1

    picked: list[pd.DataFrame] = []
    for stratum, quota in quotas.items():
        sub = df[df["_strata"] == stratum]
        n = min(int(quota), len(sub))
        if n > 0:
            picked.append(sub.sample(n=n, random_state=seed))

    sample = pd.concat(picked, ignore_index=True)
    if len(sample) > cap:
        sample = sample.sample(n=cap, random_state=seed)
    elif len(sample) < cap:
        remaining = df[~df[id_col].isin(sample[id_col])]
        need = cap - len(sample)
        if need > 0 and len(remaining) > 0:
            extra = remaining.sample(n=min(need, len(remaining)), random_state=seed)
            sample = pd.concat([sample, extra], ignore_index=True)

    llm_ids = set(sample[id_col].tolist())
    meta["llm_review_count"] = len(llm_ids)
    meta["keyword_review_count"] = total - len(llm_ids)
    meta["strata"] = {
        str(k): int(v) for k, v in sample["_strata"].value_counts().to_dict().items()
    }
    return llm_ids, meta


def load_sample_config(cfg: dict) -> tuple[bool, int, int]:
    block = cfg.get("llm_review_sample") or {}
    enabled = block.get("enabled", True)
    max_reviews = clamp_llm_cap(
        int(block.get("max_reviews", DEFAULT_MAX_REVIEWS)),
        min_reviews=int(block.get("min_reviews", DEFAULT_MIN_REVIEWS)),
    )
    min_reviews = int(block.get("min_reviews", DEFAULT_MIN_REVIEWS))
    return enabled, max_reviews, min_reviews
