#!/usr/bin/env python3
"""Merge data/raw/*.csv review exports into data/reviews/reviews.json."""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "phases" / "shared"))
from product_config import PRODUCT_NAME  # noqa: E402

RAW_DIR = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "reviews"


def load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    ios_files = sorted(RAW_DIR.glob("appstore-reviews-*.csv"))
    play_files = sorted(RAW_DIR.glob("playstore-reviews-*.csv"))

    if not ios_files and not play_files:
        print(f"No CSV files in {RAW_DIR}. Run fetch-reviews.py first.")
        return

    ios = load_csv(ios_files[-1]) if ios_files else []
    android = load_csv(play_files[-1]) if play_files else []
    all_reviews = ios + android

    # Sort newest first
    all_reviews.sort(key=lambda r: r.get("date") or "", reverse=True)

    export_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    payload = {
        "product": PRODUCT_NAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_count": len(all_reviews),
        "counts": {
            "ios": len(ios),
            "android": len(android),
        },
        "sources": {
            "ios_csv": ios_files[-1].name if ios_files else None,
            "android_csv": play_files[-1].name if play_files else None,
        },
        "reviews": all_reviews,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "reviews.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # Platform-specific copies
    if ios:
        (OUT_DIR / "appstore-reviews.json").write_text(
            json.dumps({"count": len(ios), "reviews": ios}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if android:
        (OUT_DIR / "playstore-reviews.json").write_text(
            json.dumps({"count": len(android), "reviews": android}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"Wrote {len(all_reviews):,} reviews -> {out_path}")
    print(f"  iOS: {len(ios):,}  Android: {len(android):,}")


if __name__ == "__main__":
    main()
