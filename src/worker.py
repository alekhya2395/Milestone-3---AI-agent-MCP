#!/usr/bin/env python3
"""Cron worker — scheduled weekly review refresh + pulse (+ optional publish)."""

from __future__ import annotations

import argparse
import sys

from src.config import REVIEW_WEEKS
from src.pipeline import run_weekly_job


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Weekly scheduler: fetch reviews, normalize, pulse, optional publish"
    )
    parser.add_argument(
        "--weeks",
        type=int,
        default=REVIEW_WEEKS,
        help=f"Review window in weeks (default {REVIEW_WEEKS} or REVIEW_WEEKS env)",
    )
    parser.add_argument("--skip-fetch", action="store_true", help="Skip store review download")
    parser.add_argument("--skip-pulse", action="store_true", help="Skip Phase 3 pulse")
    parser.add_argument(
        "--pulse-only",
        action="store_true",
        help="Skip fetch/normalize; run Phase 3 only",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Also publish to Google Doc + Gmail draft after pulse",
    )
    parser.add_argument(
        "--skip-gmail",
        action="store_true",
        help="With --publish, skip Gmail draft",
    )
    parser.add_argument(
        "--no-api-only",
        action="store_true",
        help="Try Drive/Gmail MCP for publish instead of API fallback",
    )
    args = parser.parse_args()

    do_fetch = not args.skip_fetch and not args.pulse_only
    do_pulse = not args.skip_pulse

    print(
        f"Scheduler: weeks={args.weeks} fetch={do_fetch} pulse={do_pulse} "
        f"publish={args.publish}",
        flush=True,
    )
    result = run_weekly_job(
        args.weeks,
        fetch=do_fetch,
        pulse=do_pulse,
        publish=args.publish,
        api_only=not args.no_api_only,
        skip_gmail=args.skip_gmail,
    )
    print(result, flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Worker failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
