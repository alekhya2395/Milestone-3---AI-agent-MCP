#!/usr/bin/env python3
"""Validate Phase 2 artifacts (T2.x checks)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_lib import LLM_CORPUS_CAP, contains_pii, validate_review_schema, word_count

ROOT = Path(__file__).resolve().parents[3]

ARTIFACTS = {
    "normalized": ROOT / "data" / "processed" / "normalized-reviews.json",
    "llm_corpus": ROOT / "data" / "processed" / "reviews-for-llm.json",
    "reviews": ROOT / "data" / "reviews" / "reviews.json",
    "norm_summary": ROOT / "data" / "processed" / "normalization-summary.json",
    "ingestion": ROOT / "data" / "processed" / "ingestion-summary.json",
}

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002700-\U000027BF"
    "\U0001F600-\U0001F64F"
    "\U00002600-\U000026FF"
    "]+",
    flags=re.UNICODE,
)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def ok(msg: str) -> None:
    print(f"OK: {msg}")


def load_json(path: Path) -> dict:
    if not path.exists():
        fail(f"missing {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    errors: list[str] = []

    for name, path in ARTIFACTS.items():
        if not path.exists():
            errors.append(f"missing artifact: {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    norm_data = load_json(ARTIFACTS["normalized"])
    llm_data = load_json(ARTIFACTS["llm_corpus"])
    reviews_data = load_json(ARTIFACTS["reviews"])
    summary = load_json(ARTIFACTS["norm_summary"])
    ingestion = load_json(ARTIFACTS["ingestion"])

    norm_reviews = norm_data.get("reviews", [])
    llm_reviews = llm_data.get("reviews", [])
    main_reviews = reviews_data.get("reviews", [])

    ok(f"normalized-reviews.json: {len(norm_reviews):,} reviews")
    ok(f"reviews-for-llm.json: {len(llm_reviews):,} reviews (cap {LLM_CORPUS_CAP})")

    if len(llm_reviews) > LLM_CORPUS_CAP:
        errors.append(f"LLM corpus exceeds cap: {len(llm_reviews)} > {LLM_CORPUS_CAP}")
    if summary.get("llm_corpus_count") != len(llm_reviews):
        errors.append("llm_corpus_count mismatch in normalization-summary.json")
    if len(main_reviews) != len(norm_reviews):
        errors.append("reviews.json count != normalized-reviews.json count")

    cap = llm_data.get("llm_corpus_cap", LLM_CORPUS_CAP)
    if len(llm_reviews) > cap:
        errors.append(f"reviews-for-llm.json exceeds llm_corpus_cap ({cap})")

    if ingestion.get("phase") != 2:
        errors.append("ingestion-summary.json phase != 2")

    sample = norm_reviews[:200] if len(norm_reviews) > 200 else norm_reviews
    for i, r in enumerate(sample):
        for err in validate_review_schema(r):
            errors.append(f"schema[{i}]: {err}")
        combined = f"{r.get('title', '')} {r.get('text', '')}"
        if word_count(r.get("title", ""), r.get("text", "")) <= 6:
            errors.append(f"review[{i}] has <=6 words after normalize")
        if EMOJI_RE.search(combined):
            errors.append(f"review[{i}] contains emoji")
        if contains_pii(combined):
            errors.append(f"review[{i}] may contain PII")

    if summary.get("date_range", {}).get("min") and summary.get("date_range", {}).get("max"):
        ok(f"date range: {summary['date_range']['min']} .. {summary['date_range']['max']}")
    else:
        errors.append("missing date_range in normalization-summary.json")

    if errors:
        print("\nValidation failed:")
        for e in errors[:20]:
            print(f"  - {e}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")
        sys.exit(1)

    print("\nPhase 2 validation passed.")


if __name__ == "__main__":
    main()
