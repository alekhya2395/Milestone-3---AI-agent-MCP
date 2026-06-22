#!/usr/bin/env python3
"""Build llm-input-bundle.json from reviews-for-llm.json (Phase 3)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pulse_lib import (
    GROQ_SAMPLE_SIZE,
    THEME_VOCABULARY,
    corpus_stats,
    select_groq_sample,
    truncate_text,
    utc_now_iso,
)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "phases" / "shared"))
from product_config import PRODUCT_NAME  # noqa: E402

LLM_CORPUS = ROOT / "data" / "processed" / "reviews-for-llm.json"
OUT = ROOT / "data" / "processed" / "llm-input-bundle.json"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sample-size", type=int, default=GROQ_SAMPLE_SIZE)
    args = p.parse_args()

    if not LLM_CORPUS.exists():
        print(f"ERROR: Missing {LLM_CORPUS}. Run Phase 2 first.", file=sys.stderr)
        sys.exit(1)

    data = json.loads(LLM_CORPUS.read_text(encoding="utf-8"))
    reviews = data.get("reviews", [])
    sample = select_groq_sample(reviews, size=args.sample_size)

    groq_reviews = []
    for i, r in enumerate(sample):
        groq_reviews.append(
            {
                "id": i,
                "platform": r.get("platform"),
                "date": r.get("date"),
                "rating": r.get("rating"),
                "text": truncate_text(r.get("title", ""), r.get("text", "")),
            }
        )

    bundle = {
        "product": PRODUCT_NAME,
        "generated_at": utc_now_iso(),
        "corpus_stats": corpus_stats(reviews),
        "theme_vocabulary": THEME_VOCABULARY,
        "groq_sample_size": len(groq_reviews),
        "groq_sample": groq_reviews,
        "source_file": "data/processed/reviews-for-llm.json",
        "source_count": len(reviews),
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT} ({len(groq_reviews)} Groq sample reviews, stats on {len(reviews)})")


if __name__ == "__main__":
    main()
