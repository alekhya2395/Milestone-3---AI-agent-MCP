#!/usr/bin/env python3
"""Normalize reviews: English only, >6 words, no emojis, PII stripped.

Reads:  data/raw/*.csv (preferred) or data/reviews/reviews-raw.json
Writes: data/processed/normalized-reviews.json  — good reviews for analysis
        data/reviews/reviews.json               — same good reviews (main file)
        data/reviews/reviews-raw.json           — full raw archive (from CSV)
        data/processed/normalization-summary.json

Rules (see docs/decision.md DEC-016):
  - Keep reviews with MORE than 6 words (minimum 7) in title + text
  - Strip emojis; drop if too short after strip
  - English language only
  - Strip PII from text fields
"""

from __future__ import annotations

import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "raw"
REVIEWS_DIR = ROOT / "data" / "reviews"
OUT_DIR = ROOT / "data" / "processed"

MIN_WORDS = 7  # more than 6 words

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


def load_from_csv() -> list[dict]:
    rows: list[dict] = []
    for pattern in ("appstore-reviews-*.csv", "playstore-reviews-*.csv"):
        for path in sorted(RAW_DIR.glob(pattern)):
            with path.open(encoding="utf-8", newline="") as f:
                rows.extend(csv.DictReader(f))
    return rows


def load_reviews() -> list[dict]:
    csv_rows = load_from_csv()
    if csv_rows:
        return csv_rows

    raw_json = REVIEWS_DIR / "reviews-raw.json"
    if raw_json.exists():
        data = json.loads(raw_json.read_text(encoding="utf-8"))
        return data.get("reviews", [])

    combined = REVIEWS_DIR / "reviews.json"
    if combined.exists():
        data = json.loads(combined.read_text(encoding="utf-8"))
        reviews = data.get("reviews", [])
        if len(reviews) > 15000:
            print("ERROR: No CSV found and reviews.json looks like raw data.", file=sys.stderr)
            print("Run fetch-reviews.py first.", file=sys.stderr)
            sys.exit(1)
        return reviews

    print("ERROR: No review data in data/raw/ or data/reviews/", file=sys.stderr)
    sys.exit(1)


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
        "rating": row.get("rating", ""),
        "title": title,
        "text": text,
        "version": row.get("version", ""),
        "country": row.get("country", ""),
        "source": row.get("source", ""),
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    try:
        from langdetect import DetectorFactory  # noqa: F401
    except ImportError:
        print("ERROR: pip install langdetect", file=sys.stderr)
        sys.exit(1)

    reviews = load_reviews()
    print(f"Loaded {len(reviews):,} raw reviews")

    # Archive full raw set once (from CSV)
    if load_from_csv():
        write_json(
            REVIEWS_DIR / "reviews-raw.json",
            {
                "product": "Zomato",
                "archived_at": datetime.now(timezone.utc).isoformat(),
                "total_count": len(reviews),
                "note": "Unfiltered export; use reviews.json for good reviews only",
                "reviews": reviews,
            },
        )
        print(f"Archived raw -> {REVIEWS_DIR / 'reviews-raw.json'}")

    kept: list[dict] = []
    stats = {
        "total_in": len(reviews),
        "kept": 0,
        "dropped_word_count": 0,
        "dropped_non_english": 0,
        "dropped_empty_after_clean": 0,
        "rules": {
            "min_words": MIN_WORDS,
            "english_only": True,
            "strip_emojis": True,
            "strip_pii": True,
        },
    }

    for row in reviews:
        title = strip_emojis(str(row.get("title") or ""))
        text = strip_emojis(str(row.get("text") or ""))

        if word_count(title, text) <= 6:
            stats["dropped_word_count"] += 1
            continue
        if not is_english(title, text):
            stats["dropped_non_english"] += 1
            continue

        normalized = normalize_row(row)
        if normalized is None:
            stats["dropped_empty_after_clean"] += 1
            continue
        kept.append(normalized)

    stats["kept"] = len(kept)
    stats["by_platform"] = {
        "ios": sum(1 for r in kept if r.get("platform") == "ios"),
        "android": sum(1 for r in kept if r.get("platform") == "android"),
    }
    stats["generated_at"] = datetime.now(timezone.utc).isoformat()

    good_payload = {
        "product": "Zomato",
        "generated_at": stats["generated_at"],
        "total_count": len(kept),
        "note": "Good reviews only: English, >6 words, no emojis, PII stripped",
        "counts": stats["by_platform"],
        "reviews": kept,
    }

    write_json(OUT_DIR / "normalized-reviews.json", {"count": len(kept), "reviews": kept})
    write_json(REVIEWS_DIR / "reviews.json", good_payload)
    write_json(OUT_DIR / "normalization-summary.json", stats)

    # Platform splits (good only)
    ios = [r for r in kept if r.get("platform") == "ios"]
    android = [r for r in kept if r.get("platform") == "android"]
    write_json(REVIEWS_DIR / "appstore-reviews.json", {"count": len(ios), "reviews": ios})
    write_json(REVIEWS_DIR / "playstore-reviews.json", {"count": len(android), "reviews": android})

    print(f"\nKept {len(kept):,} good reviews")
    print(f"  Dropped (<=6 words): {stats['dropped_word_count']:,}")
    print(f"  Dropped (non-English): {stats['dropped_non_english']:,}")
    print(f"  iOS: {stats['by_platform']['ios']:,}  Android: {stats['by_platform']['android']:,}")
    print(f"\nGood reviews -> data/reviews/reviews.json")
    print(f"Processed   -> data/processed/normalized-reviews.json")


if __name__ == "__main__":
    main()
