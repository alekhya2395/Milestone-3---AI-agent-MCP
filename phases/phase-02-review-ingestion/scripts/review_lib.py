"""Shared review normalization helpers (Phase 2)."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any

MIN_WORDS = 7  # more than 6 words (DEC-016)
LLM_CORPUS_CAP = 1000

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U0001F600-\U0001F64F"
    "\U00002600-\U000026FF"
    "\U0000FE00-\U0000FE0F"
    "\U0000200D"
    "]+",
    flags=re.UNICODE,
)

PII_PATTERNS = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[email]"),
    (re.compile(r"@[A-Za-z0-9_]{2,}"), "[handle]"),
    (re.compile(r"\b\+?\d[\d\s\-()]{8,}\d\b"), "[phone]"),
]

PII_CHECK_RE = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    re.compile(r"@[A-Za-z0-9_]{2,}"),
    re.compile(r"\b\+?\d[\d\s\-()]{8,}\d\b"),
]


def word_count(title: str, text: str) -> int:
    combined = f"{title or ''} {text or ''}".strip()
    return len(re.findall(r"[A-Za-z0-9']+", combined))


def strip_emojis(s: str) -> str:
    cleaned = EMOJI_RE.sub("", s)
    return re.sub(r"\s+", " ", cleaned).strip()


def strip_pii(s: str) -> str:
    out = s
    for pattern, repl in PII_PATTERNS:
        out = pattern.sub(repl, out)
    return re.sub(r"\s+", " ", out).strip()


def contains_pii(s: str) -> bool:
    return any(p.search(s) for p in PII_CHECK_RE)


def is_english(title: str, text: str) -> bool:
    from langdetect import DetectorFactory, detect

    DetectorFactory.seed = 0
    sample = f"{title or ''} {text or ''}".strip()
    if len(sample) < 15:
        letters = re.findall(r"[A-Za-z]", sample)
        return len(letters) >= 10 and len(letters) / max(len(sample), 1) > 0.7
    try:
        return detect(sample) == "en"
    except Exception:
        return False


def filter_by_weeks(rows: list[dict], weeks: int) -> list[dict]:
    cutoff = (datetime.now() - timedelta(weeks=weeks)).strftime("%Y-%m-%d")
    return [r for r in rows if (r.get("date") or "") >= cutoff]


def date_range(rows: list[dict]) -> dict[str, str | None]:
    dates = sorted(d for d in (r.get("date") or "" for r in rows) if d)
    return {"min": dates[0] if dates else None, "max": dates[-1] if dates else None}


def rating_distribution(rows: list[dict]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for r in rows:
        counts[str(r.get("rating") or "unknown")] += 1
    return dict(sorted(counts.items(), key=lambda x: x[0]))


def sort_reviews_for_selection(r: dict) -> tuple:
    return (r.get("date") or "", word_count(r.get("title", ""), r.get("text", "")))


def select_llm_corpus(reviews: list[dict], cap: int = LLM_CORPUS_CAP) -> list[dict]:
    """Cap corpus for Phase 3: recent, stratified by rating, prefer longer text."""
    if len(reviews) <= cap:
        return sorted(reviews, key=sort_reviews_for_selection, reverse=True)

    by_rating: dict[str, list[dict]] = defaultdict(list)
    for r in reviews:
        by_rating[str(r.get("rating") or "")].append(r)

    for group in by_rating.values():
        group.sort(key=sort_reviews_for_selection, reverse=True)

    low = [r for k in ("1", "2") for r in by_rating.get(k, [])]
    mid = by_rating.get("3", [])
    high = [r for k in ("4", "5") for r in by_rating.get(k, [])]

    n_low = int(cap * 0.50)
    n_mid = int(cap * 0.20)
    n_high = cap - n_low - n_mid

    selected: list[dict] = []
    seen: set[int] = set()

    def add_from(pool: list[dict], n: int) -> None:
        for r in pool:
            if len(selected) >= cap or n <= 0:
                break
            rid = id(r)
            if rid in seen:
                continue
            selected.append(r)
            seen.add(rid)
            n -= 1

    add_from(low, n_low)
    add_from(mid, n_mid)
    add_from(high, n_high)

    if len(selected) < cap:
        remainder = sorted(reviews, key=sort_reviews_for_selection, reverse=True)
        for r in remainder:
            if len(selected) >= cap:
                break
            if id(r) not in seen:
                selected.append(r)
                seen.add(id(r))

    selected.sort(key=sort_reviews_for_selection, reverse=True)
    return selected[:cap]


def normalize_row(row: dict) -> dict | None:
    title = strip_emojis(str(row.get("title") or ""))
    text = strip_emojis(str(row.get("text") or ""))

    if word_count(title, text) <= 6:
        return None
    if not is_english(title, text):
        return None

    title = strip_pii(title)
    text = strip_pii(text)
    if not text and not title:
        return None
    if word_count(title, text) <= 6:
        return None

    return {
        "platform": row.get("platform", ""),
        "date": row.get("date", ""),
        "rating": str(row.get("rating", "")),
        "title": title,
        "text": text,
        "version": row.get("version", ""),
        "country": row.get("country", ""),
        "source": row.get("source", ""),
    }


def validate_review_schema(row: dict) -> list[str]:
    errors: list[str] = []
    if row.get("platform") not in ("ios", "android"):
        errors.append(f"invalid platform: {row.get('platform')}")
    if not row.get("date"):
        errors.append("missing date")
    if not (row.get("text") or row.get("title")):
        errors.append("missing text/title")
    return errors
