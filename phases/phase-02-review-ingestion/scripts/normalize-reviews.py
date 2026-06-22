#!/usr/bin/env python3
"""Normalize reviews and build Groq-ready LLM corpus (Phase 2).

Reads:  data/raw/*.csv (preferred) or data/reviews/reviews-raw.json
Writes: data/processed/normalized-reviews.json   — full good-review archive
        data/processed/reviews-for-llm.json       — capped corpus (default 1000)
        data/processed/normalization-summary.json
        data/processed/ingestion-summary.json
        data/reviews/reviews.json                 — same as normalized (main file)
        data/reviews/reviews-raw.json             — full raw archive (from CSV)

Rules (DEC-016): English, >6 words, no emojis, PII stripped.
See docs/architecture.md §5.1 for LLM corpus cap.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from review_lib import (
    LLM_CORPUS_CAP,
    date_range,
    filter_by_weeks,
    is_english,
    normalize_row,
    rating_distribution,
    select_llm_corpus,
    strip_emojis,
    word_count,
)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "phases" / "shared"))
from product_config import PRODUCT_NAME  # noqa: E402

RAW_DIR = ROOT / "data" / "raw"
REVIEWS_DIR = ROOT / "data" / "reviews"
OUT_DIR = ROOT / "data" / "processed"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Normalize store reviews (Phase 2)")
    p.add_argument(
        "--weeks",
        type=int,
        default=10,
        help="Date window in weeks (8-12; default 10). Re-filter loaded rows.",
    )
    p.add_argument(
        "--llm-cap",
        type=int,
        default=LLM_CORPUS_CAP,
        help=f"Max reviews in reviews-for-llm.json (default {LLM_CORPUS_CAP})",
    )
    return p.parse_args()


def load_from_csv() -> list[dict]:
    summaries = sorted(RAW_DIR.glob("export-summary-*.json"), reverse=True)
    if summaries:
        summary = json.loads(summaries[0].read_text(encoding="utf-8"))
        files = summary.get("files", {})
        rows: list[dict] = []
        for key in ("ios", "android"):
            name = files.get(key)
            if not name:
                continue
            path = RAW_DIR / name
            if path.is_file():
                with path.open(encoding="utf-8", newline="") as f:
                    rows.extend(csv.DictReader(f))
        if rows:
            return rows

    rows = []
    ios_files = sorted(RAW_DIR.glob("appstore-reviews-*.csv"))
    play_files = sorted(RAW_DIR.glob("playstore-reviews-*.csv"))
    for path in (ios_files[-1:] if ios_files else []) + (play_files[-1:] if play_files else []):
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


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_export_summary() -> dict | None:
    summaries = sorted(RAW_DIR.glob("export-summary-*.json"))
    if not summaries:
        return None
    return json.loads(summaries[-1].read_text(encoding="utf-8"))


def main() -> None:
    try:
        from langdetect import DetectorFactory  # noqa: F401
    except ImportError:
        print("ERROR: pip install langdetect", file=sys.stderr)
        sys.exit(1)

    args = parse_args()
    if not 8 <= args.weeks <= 12:
        print(f"WARNING: --weeks={args.weeks} outside 8-12 range.", file=sys.stderr)

    reviews = load_reviews()
    print(f"Loaded {len(reviews):,} raw reviews")

    if load_from_csv():
        write_json(
            REVIEWS_DIR / "reviews-raw.json",
            {
                "product": PRODUCT_NAME,
                "archived_at": datetime.now(timezone.utc).isoformat(),
                "total_count": len(reviews),
                "note": "Unfiltered export; use normalized output for analysis",
                "reviews": reviews,
            },
        )
        print(f"Archived raw -> {REVIEWS_DIR / 'reviews-raw.json'}")

    in_window = filter_by_weeks(reviews, args.weeks)
    print(f"In {args.weeks}-week window: {len(in_window):,} reviews")

    kept: list[dict] = []
    stats = {
        "total_in": len(reviews),
        "in_window": len(in_window),
        "review_window_weeks": args.weeks,
        "kept": 0,
        "dropped_outside_window": len(reviews) - len(in_window),
        "dropped_word_count": 0,
        "dropped_non_english": 0,
        "dropped_empty_after_clean": 0,
        "llm_corpus_cap": args.llm_cap,
        "llm_corpus_count": 0,
        "rules": {
            "min_words": 7,
            "english_only": True,
            "strip_emojis": True,
            "strip_pii": True,
        },
    }

    for row in in_window:
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
    stats["date_range"] = date_range(kept)
    stats["rating_distribution"] = rating_distribution(kept)
    stats["generated_at"] = datetime.now(timezone.utc).isoformat()

    llm_corpus = select_llm_corpus(kept, cap=args.llm_cap)
    stats["llm_corpus_count"] = len(llm_corpus)
    stats["llm_corpus_rating_distribution"] = rating_distribution(llm_corpus)
    stats["llm_corpus_by_platform"] = {
        "ios": sum(1 for r in llm_corpus if r.get("platform") == "ios"),
        "android": sum(1 for r in llm_corpus if r.get("platform") == "android"),
    }

    generated_at = stats["generated_at"]
    good_payload = {
        "product": PRODUCT_NAME,
        "generated_at": generated_at,
        "total_count": len(kept),
        "review_window_weeks": args.weeks,
        "note": "Good reviews only: English, >6 words, no emojis, PII stripped",
        "counts": stats["by_platform"],
        "reviews": kept,
    }

    llm_payload = {
        "product": PRODUCT_NAME,
        "generated_at": generated_at,
        "total_count": len(llm_corpus),
        "llm_corpus_cap": args.llm_cap,
        "note": "Stratified subset for Phase 3 Groq (local stats + quote pool)",
        "selection": {
            "strategy": "recent_first, ~50% low ratings (1-2★), prefer longer text",
            "source_count": len(kept),
        },
        "counts": stats["llm_corpus_by_platform"],
        "reviews": llm_corpus,
    }

    write_json(OUT_DIR / "normalized-reviews.json", {"count": len(kept), "reviews": kept})
    write_json(OUT_DIR / "reviews-for-llm.json", llm_payload)
    write_json(REVIEWS_DIR / "reviews.json", good_payload)
    write_json(OUT_DIR / "normalization-summary.json", stats)

    export_summary = load_export_summary()
    ingestion = {
        "phase": 2,
        "product": PRODUCT_NAME,
        "generated_at": generated_at,
        "review_window_weeks": args.weeks,
        "raw_export": export_summary,
        "normalization": stats,
        "artifacts": {
            "normalized_reviews": "data/processed/normalized-reviews.json",
            "reviews_for_llm": "data/processed/reviews-for-llm.json",
            "reviews_main": "data/reviews/reviews.json",
            "normalization_summary": "data/processed/normalization-summary.json",
        },
        "handoff_phase_3": {
            "llm_provider": "Groq (llama-3.3-70b-versatile)",
            "llm_corpus_file": "data/processed/reviews-for-llm.json",
            "groq_sample_size": "~120 reviews (built in Phase 3)",
            "groq_calls_per_run": 2,
        },
    }
    write_json(OUT_DIR / "ingestion-summary.json", ingestion)

    ios = [r for r in kept if r.get("platform") == "ios"]
    android = [r for r in kept if r.get("platform") == "android"]
    write_json(REVIEWS_DIR / "appstore-reviews.json", {"count": len(ios), "reviews": ios})
    write_json(REVIEWS_DIR / "playstore-reviews.json", {"count": len(android), "reviews": android})

    dr = stats["date_range"]
    print(f"\nKept {len(kept):,} good reviews ({dr.get('min')} .. {dr.get('max')})")
    print(f"  Dropped (outside window): {stats['dropped_outside_window']:,}")
    print(f"  Dropped (<=6 words): {stats['dropped_word_count']:,}")
    print(f"  Dropped (non-English): {stats['dropped_non_english']:,}")
    print(f"  iOS: {stats['by_platform']['ios']:,}  Android: {stats['by_platform']['android']:,}")
    print(f"\nLLM corpus: {len(llm_corpus):,} reviews (cap {args.llm_cap})")
    print(f"  -> data/processed/reviews-for-llm.json")
    print(f"  -> data/processed/normalized-reviews.json")
    print(f"  -> data/processed/ingestion-summary.json")


if __name__ == "__main__":
    main()
