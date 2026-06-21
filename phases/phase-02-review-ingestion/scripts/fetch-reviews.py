#!/usr/bin/env python3
"""Download public Zomato reviews (Milestone 1 product) into data/raw/.

- Google Play: paginate until the review window (default 10 weeks) is covered
- App Store: public RSS feed (up to ~500 reviews per region)

Usage:
  pip install google-play-scraper
  python phases/phase-02-review-ingestion/scripts/fetch-reviews.py
  python phases/phase-02-review-ingestion/scripts/fetch-reviews.py --weeks 12
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Project root: .../MILESTONE 3 - AI AGENT WITH MCP
ROOT = Path(__file__).resolve().parents[3]
RAW_DIR = ROOT / "data" / "raw"

PRODUCT = "Zomato"
APP_STORE_ID = "434613896"
PLAY_PACKAGE = "com.application.zomato"
PLAY_COUNTRY = "in"
APP_STORE_COUNTRIES = ("us", "in", "gb")

USER_AGENT = "Mozilla/5.0 (compatible; WeeklyPulseBot/1.0; +https://github.com)"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch public store reviews for Zomato")
    p.add_argument(
        "--weeks",
        type=int,
        default=10,
        help="Review window in weeks (8-12 per problem statement; default 10)",
    )
    p.add_argument(
        "--max-play-fetches",
        type=int,
        default=300,
        help="Safety cap on Play Store pagination batches (200 reviews each)",
    )
    return p.parse_args()


def fetch_app_store_reviews(countries: tuple[str, ...] = APP_STORE_COUNTRIES) -> list[dict]:
    """App Store customer reviews via public RSS (max ~500 per country)."""
    rows: list[dict] = []
    export_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for country in countries:
        for page in range(1, 11):
            url = (
                f"https://itunes.apple.com/{country}/rss/customerreviews/"
                f"id={APP_STORE_ID}/sortby=mostrecent/page={page}/json"
            )
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code in (400, 404):
                    break
                raise

            entries = data.get("feed", {}).get("entry", [])
            if not entries:
                break
            if isinstance(entries, dict):
                entries = [entries]

            page_rows = 0
            for entry in entries:
                if not isinstance(entry, dict) or "im:rating" not in entry:
                    continue
                updated = entry.get("updated", {}).get("label", "")
                rows.append(
                    {
                        "platform": "ios",
                        "date": updated[:10] if updated else "",
                        "rating": entry.get("im:rating", {}).get("label", ""),
                        "title": entry.get("title", {}).get("label", ""),
                        "text": entry.get("content", {}).get("label", ""),
                        "version": entry.get("im:version", {}).get("label", ""),
                        "country": country,
                        "source": f"appstore-rss-{export_tag}",
                    }
                )
                page_rows += 1
            if page_rows == 0:
                break

    # Deduplicate by date+rating+text prefix
    seen: set[str] = set()
    unique: list[dict] = []
    for r in rows:
        key = f"{r['date']}|{r['rating']}|{r['text'][:80]}"
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def fetch_play_store_reviews(
    weeks: int,
    max_batches: int = 50,
    batch_size: int = 200,
) -> list[dict]:
    """Paginate Google Play reviews until window is covered or data exhausted."""
    try:
        from google_play_scraper import Sort, reviews
    except ImportError:
        print("ERROR: pip install google-play-scraper", file=sys.stderr)
        sys.exit(1)

    export_tag = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cutoff = datetime.now() - timedelta(weeks=weeks)
    rows: list[dict] = []
    token = None
    oldest_seen: datetime | None = None

    for batch_num in range(max_batches):
        batch_result, token = reviews(
            PLAY_PACKAGE,
            lang="en",
            country=PLAY_COUNTRY,
            sort=Sort.NEWEST,
            count=batch_size,
            continuation_token=token,
        )
        if not batch_result:
            break

        batch_added = 0
        hit_cutoff = False
        for r in batch_result:
            at = r.get("at")
            if at is None:
                continue
            if at < cutoff:
                hit_cutoff = True
                continue
            rows.append(
                {
                    "platform": "android",
                    "date": at.strftime("%Y-%m-%d"),
                    "rating": r.get("score", ""),
                    "title": "",
                    "text": (r.get("content") or "").strip(),
                    "version": r.get("reviewCreatedVersion") or "",
                    "country": PLAY_COUNTRY,
                    "source": f"playstore-scraper-{export_tag}",
                }
            )
            batch_added += 1
            if oldest_seen is None or at < oldest_seen:
                oldest_seen = at

        print(f"    batch {batch_num + 1}: +{batch_added} in window (total {len(rows)})")

        if hit_cutoff and oldest_seen and oldest_seen <= cutoff:
            print(f"    reached cutoff {cutoff.date()} (oldest in batch: {oldest_seen.date()})")
            break
        if token is None:
            print("    no more pages from Play Store")
            break

    if rows:
        oldest = min(r["date"] for r in rows if r.get("date"))
        window_start = cutoff.strftime("%Y-%m-%d")
        if oldest > window_start:
            print(
                f"  WARNING: Play oldest review {oldest} is newer than window start {window_start}. "
                "High-volume apps may need multiple export runs or a paid export tool.",
                file=sys.stderr,
            )

    return rows


def filter_by_window(rows: list[dict], weeks: int) -> list[dict]:
    cutoff = (datetime.now() - timedelta(weeks=weeks)).strftime("%Y-%m-%d")
    return [r for r in rows if (r.get("date") or "") >= cutoff]


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["platform", "date", "rating", "title", "text", "version", "country", "source"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def date_range(rows: list[dict]) -> dict:
    dates = sorted(d for d in (r.get("date") or "" for r in rows) if d)
    return {"min": dates[0] if dates else None, "max": dates[-1] if dates else None}


def main() -> None:
    args = parse_args()
    if not 8 <= args.weeks <= 12:
        print("WARNING: --weeks outside 8-12; using anyway.", file=sys.stderr)

    export_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Product: {PRODUCT}")
    print(f"Output:  {RAW_DIR}")
    print(f"Window:  last {args.weeks} weeks")
    print()

    print("App Store (public RSS)...")
    ios_all = fetch_app_store_reviews()
    ios_rows = filter_by_window(ios_all, args.weeks)
    ios_path = RAW_DIR / f"appstore-reviews-{export_date}.csv"
    write_csv(ios_path, ios_rows)
    print(f"  -> {len(ios_rows)} in window ({len(ios_all)} fetched) -> {ios_path}")

    print("Google Play (public scraper)...")
    android_rows = fetch_play_store_reviews(weeks=args.weeks, max_batches=args.max_play_fetches)
    play_path = RAW_DIR / f"playstore-reviews-{export_date}.csv"
    write_csv(play_path, android_rows)
    print(f"  -> {len(android_rows)} in window -> {play_path}")

    summary = {
        "product": PRODUCT,
        "milestone": "MILESTONE 1 - ZOMATO",
        "export_date": export_date,
        "review_window_weeks": args.weeks,
        "window_start": (datetime.now() - timedelta(weeks=args.weeks)).strftime("%Y-%m-%d"),
        "play_country": PLAY_COUNTRY,
        "app_store_id": APP_STORE_ID,
        "play_package": PLAY_PACKAGE,
        "ios_count": len(ios_rows),
        "android_count": len(android_rows),
        "ios_date_range": date_range(ios_rows),
        "android_date_range": date_range(android_rows),
        "files": {
            "ios": ios_path.name,
            "android": play_path.name,
        },
        "sources": {
            "ios": f"https://itunes.apple.com/rss/customerreviews/id={APP_STORE_ID}/json",
            "android": f"https://play.google.com/store/apps/details?id={PLAY_PACKAGE}",
        },
    }
    summary_path = RAW_DIR / f"export-summary-{export_date}.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSummary -> {summary_path}")

    # Also write combined JSON to data/reviews/
    try:
        import subprocess

        script = Path(__file__).parent / "csv-to-reviews-json.py"
        subprocess.run([sys.executable, str(script)], check=True)
    except Exception as e:
        print(f"Note: could not build reviews.json ({e})", file=sys.stderr)

    print("Done.")


if __name__ == "__main__":
    main()
