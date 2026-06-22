"""Phase 3 pulse generation helpers."""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PHASE2_SCRIPTS = ROOT / "phases" / "phase-02-review-ingestion" / "scripts"
sys.path.insert(0, str(PHASE2_SCRIPTS))
sys.path.insert(0, str(ROOT / "phases" / "shared"))

from product_config import THEME_KEYWORDS, THEME_VOCABULARY  # noqa: E402
from review_lib import contains_pii, word_count  # noqa: E402

THEME_VOCABULARY = THEME_VOCABULARY  # re-export
THEME_KEYWORDS = THEME_KEYWORDS

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_SAMPLE_SIZE = 120
MAX_REVIEW_CHARS = 320  # ~80 tokens

SEVERITY_WEIGHT = {"1": 3.0, "2": 2.5, "3": 1.0, "4": 0.5, "5": 0.3}


def severity_weight(rating: str) -> float:
    return SEVERITY_WEIGHT.get(str(rating), 1.0)


def truncate_text(title: str, text: str, max_chars: int = MAX_REVIEW_CHARS) -> str:
    combined = f"{title} {text}".strip()
    if len(combined) <= max_chars:
        return combined
    return combined[: max_chars - 3].rstrip() + "..."


def sort_for_selection(r: dict) -> tuple:
    return (r.get("date") or "", word_count(r.get("title", ""), r.get("text", "")))


def select_groq_sample(reviews: list[dict], size: int = GROQ_SAMPLE_SIZE) -> list[dict]:
    if len(reviews) <= size:
        return sorted(reviews, key=sort_for_selection, reverse=True)

    by_rating: dict[str, list[dict]] = defaultdict(list)
    for r in reviews:
        by_rating[str(r.get("rating") or "")].append(r)
    for group in by_rating.values():
        group.sort(key=sort_for_selection, reverse=True)

    low = [r for k in ("1", "2") for r in by_rating.get(k, [])]
    mid = by_rating.get("3", [])
    high = [r for k in ("4", "5") for r in by_rating.get(k, [])]

    n_low = int(size * 0.50)
    n_mid = int(size * 0.20)
    n_high = size - n_low - n_mid

    selected: list[dict] = []
    seen: set[int] = set()

    def take(pool: list[dict], n: int) -> None:
        for r in pool:
            if len(selected) >= size or n <= 0:
                break
            rid = id(r)
            if rid in seen:
                continue
            selected.append(r)
            seen.add(rid)
            n -= 1

    take(low, n_low)
    take(mid, n_mid)
    take(high, n_high)

    if len(selected) < size:
        for r in sorted(reviews, key=sort_for_selection, reverse=True):
            if len(selected) >= size:
                break
            if id(r) not in seen:
                selected.append(r)
                seen.add(id(r))

    selected.sort(key=sort_for_selection, reverse=True)
    return selected[:size]


def classify_theme(title: str, text: str) -> str:
    combined = f"{title} {text}".lower()
    scores: dict[str, int] = {t: 0 for t in THEME_VOCABULARY}
    for theme, keywords in THEME_KEYWORDS.items():
        for kw in keywords:
            if kw in combined:
                scores[theme] += 1
    best = max(scores, key=lambda t: scores[t])
    if scores[best] == 0:
        return "App UX & bugs"
    return best


def corpus_stats(reviews: list[dict]) -> dict:
    ratings = Counter(str(r.get("rating") or "") for r in reviews)
    platforms = Counter(str(r.get("platform") or "") for r in reviews)
    dates = sorted(d for d in (r.get("date") or "" for r in reviews) if d)
    low_star = sum(1 for r in reviews if str(r.get("rating")) in ("1", "2"))
    return {
        "total": len(reviews),
        "date_range": {"min": dates[0] if dates else None, "max": dates[-1] if dates else None},
        "by_rating": dict(sorted(ratings.items())),
        "by_platform": dict(platforms),
        "low_star_pct": round(100 * low_star / len(reviews), 1) if reviews else 0,
        "avg_rating": round(
            sum(int(r.get("rating") or 3) for r in reviews) / len(reviews), 2
        )
        if reviews
        else 0,
    }


def apply_groq_assignments(
    reviews: list[dict],
    assignments: list[dict],
    sample_reviews: list[dict],
) -> dict[int, str]:
    """Map sample index -> theme from Groq; returns id(review) -> theme for sample."""
    theme_by_id: dict[int, str] = {}
    for item in assignments:
        idx = item.get("id")
        theme = item.get("theme", "")
        if theme not in THEME_VOCABULARY:
            continue
        if isinstance(idx, int) and 0 <= idx < len(sample_reviews):
            theme_by_id[id(sample_reviews[idx])] = theme
    return theme_by_id


def rank_themes(
    reviews: list[dict],
    groq_themes: dict[int, str] | None = None,
) -> list[dict]:
    scores: dict[str, float] = {t: 0.0 for t in THEME_VOCABULARY}
    counts: Counter[str] = Counter()

    for r in reviews:
        rid = id(r)
        if groq_themes and rid in groq_themes:
            theme = groq_themes[rid]
        else:
            theme = classify_theme(r.get("title", ""), r.get("text", ""))
        w = severity_weight(str(r.get("rating")))
        scores[theme] += w
        counts[theme] += 1

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        {
            "rank": i + 1,
            "theme": theme,
            "score": round(score, 2),
            "review_count": counts[theme],
        }
        for i, (theme, score) in enumerate(ranked)
    ]


def pick_quotes(reviews: list[dict], theme: str, n: int = 3) -> list[dict]:
    candidates = []
    for r in reviews:
        assigned = classify_theme(r.get("title", ""), r.get("text", ""))
        if assigned != theme:
            continue
        text = (r.get("text") or r.get("title") or "").strip()
        if not text or contains_pii(text):
            continue
        if word_count("", text) < 7:
            continue
        candidates.append(r)

    candidates.sort(
        key=lambda r: (
            severity_weight(str(r.get("rating"))),
            word_count(r.get("title", ""), r.get("text", "")),
        ),
        reverse=True,
    )
    return candidates[:n]


def pulse_word_count(markdown: str) -> int:
    """Count words in pulse body (exclude title line)."""
    lines = markdown.strip().splitlines()
    body = "\n".join(lines[1:]) if lines else markdown
    return len(re.findall(r"[A-Za-z0-9']+", body))


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
