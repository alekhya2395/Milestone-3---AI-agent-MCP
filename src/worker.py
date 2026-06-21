#!/usr/bin/env python3
"""Cron worker — fetch and normalize reviews on a schedule."""

from __future__ import annotations

import argparse
import sys

from src.pipeline import run_fetch_reviews, run_normalize_reviews


def main() -> None:
    parser = argparse.ArgumentParser(description="Weekly review ingestion worker")
    parser.add_argument("--weeks", type=int, default=10, help="Review window in weeks")
    args = parser.parse_args()

    print(f"Fetching reviews ({args.weeks} weeks)...")
    print(run_fetch_reviews(args.weeks))

    print("Normalizing reviews...")
    print(run_normalize_reviews())

    print("Worker finished successfully.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Worker failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
