#!/usr/bin/env python3
"""Fetch public Zomato reviews from App Store (RSS) and Google Play (google-play-scraper).

Outputs CSV files to data/raw/ for Phase 2 ingestion.
Uses public endpoints only — no store login required.
"""

from __future__ import annotations

import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "raw"

# Milestone 1 product — Zomato
PRODUCT = "Zomato"
APP_STORE_ID = "434613896"
PLAY_PACKAGE = "com.application.zomato"
COUNTRY = "in"  # India — primary Zomato market

EXPORT_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def fetch_app_store_reviews(max_pages: int = 10) -> list[dict]:
    """App Store customer reviews via public RSS (max ~500 reviews)."""
    rows: list[dict] = []
    for page in range(1, max_pages + 1):
        url = (
            f"https://itunes.apple.com/{COUNTRY}/rss/customerreviews/"
            f"id={APP_STORE_ID}/sortby=mostrecent/page={page}/json"
        )
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                break
            raise

        entries = data.get("feed", {}).get("entry", [])
        if not entries:
            break
        # First entry on page 1 can be app metadata, not a review
        for entry in entries:
            if "im:rating" not in entry:
                continue
            title = entry.get("title", {}).get("label", "")
            text = entry.get("content", {}).get("label", "")
            rating = entry.get("im:rating", {}).get("label", "")
            updated = entry.get("updated", {}).get("label", "")
            version = entry.get("im:version", {}).get("label", "")
            rows.append(
                {
                    "platform": "ios",
                    "date": updated[:10] if updated else "",
                    "rating": rating,
                    "title": title,
                    "text": text,
                    "version": version,
                    "source": f"appstore-rss-{EXPORT_DATE}",
                }
            )
    return rows


def fetch_play_store_reviews(target_count: int = 500) -> list[dict]:
    """Google Play reviews via google-play-scraper (public)."""
    try:
        from google_play_scraper import Sort, reviews
    except ImportError:
        print("ERROR: pip install google-play-scraper", file=sys.stderr)
        sys.exit(1)

    rows: list[dict] = []
    token = None
    batch = 200

    while len(rows) < target_count:
        batch_result, token = reviews(
            PLAY_PACKAGE,
            lang="en",
            country=COUNTRY,
            sort=Sort.NEWEST,
            count=min(batch, target_count - len(rows)),
            continuation_token=token,
        )
        if not batch_result:
            break
        for r in batch_result:
            rows.append(
                {
                    "platform": "android",
                    "date": r.get("at", "").strftime("%Y-%m-%d") if r.get("at") else "",
                    "rating": r.get("score", ""),
                    "title": "",
                    "text": r.get("content", "") or "",
                    "version": r.get("reviewCreatedVersion", "") or "",
                    "source": f"playstore-scraper-{EXPORT_DATE}",
                }
            )
        if token is None:
            break

    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["platform", "date", "rating", "title", "text", "version", "source"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    print(f"Fetching {PRODUCT} reviews (country={COUNTRY})...")

    print("  App Store RSS...")
    ios_rows = fetch_app_store_reviews()
    ios_path = RAW_DIR / f"appstore-reviews-{EXPORT_DATE}.csv"
    write_csv(ios_path, ios_rows)
    print(f"    -> {len(ios_rows)} reviews -> {ios_path.name}")

    print("  Google Play...")
    android_rows = fetch_play_store_reviews(target_count=500)
    play_path = RAW_DIR / f"playstore-reviews-{EXPORT_DATE}.csv"
    write_csv(play_path, android_rows)
    print(f"    -> {len(android_rows)} reviews -> {play_path.name}")

    summary = {
        "product": PRODUCT,
        "export_date": EXPORT_DATE,
        "country": COUNTRY,
        "app_store_id": APP_STORE_ID,
        "play_package": PLAY_PACKAGE,
        "ios_count": len(ios_rows),
        "android_count": len(android_rows),
        "ios_date_range": _date_range(ios_rows),
        "android_date_range": _date_range(android_rows),
        "sources": {
            "ios": f"https://itunes.apple.com/{COUNTRY}/rss/customerreviews/id={APP_STORE_ID}/json",
            "android": f"https://play.google.com/store/apps/details?id={PLAY_PACKAGE}",
        },
    }
    summary_path = RAW_DIR / f"export-summary-{EXPORT_DATE}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"  Summary -> {summary_path.name}")
    print("Done.")


def _date_range(rows: list[dict]) -> dict:
    dates = sorted(d for d in (r.get("date") or "" for r in rows) if d)
    return {"min": dates[0] if dates else None, "max": dates[-1] if dates else None}


if __name__ == "__main__":
    main()
