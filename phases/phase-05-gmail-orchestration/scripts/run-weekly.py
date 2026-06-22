#!/usr/bin/env python3
"""End-to-end weekly run: Phase 2 (skip fetch) → 3 → 4 → 5."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def run(label: str, cmd: list[str]) -> None:
    print(f"\n=== {label} ===\n>> {' '.join(cmd)}\n")
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        print(f"\nFAILED: {label}", file=sys.stderr)
        sys.exit(r.returncode)


def main() -> None:
    p = argparse.ArgumentParser(description="Weekly E2E orchestration")
    p.add_argument("--weeks", type=int, default=10)
    p.add_argument("--fetch", action="store_true", default=True, help="Download latest reviews (default)")
    p.add_argument("--no-fetch", action="store_true", help="Skip fetch; use existing raw CSVs")
    p.add_argument("--skip-gmail", action="store_true", help="Stop after Phase 4")
    args = p.parse_args()

    py = sys.executable
    phase2 = ROOT / "phases" / "phase-02-review-ingestion" / "scripts" / "run-phase2.py"
    phase3 = ROOT / "phases" / "phase-03-pulse-generation" / "scripts" / "run-phase3.py"
    phase4 = ROOT / "phases" / "phase-04-google-docs-mcp" / "scripts" / "run-phase4.py"
    phase5 = ROOT / "phases" / "phase-05-gmail-orchestration" / "scripts" / "run-phase5.py"

    if args.fetch and not args.no_fetch:
        fetch = ROOT / "phases" / "phase-02-review-ingestion" / "scripts" / "fetch-reviews.py"
        run("Fetch reviews", [py, str(fetch), "--weeks", str(args.weeks)])

    p2_cmd = [py, str(phase2), "--weeks", str(args.weeks)]
    if args.no_fetch:
        p2_cmd.append("--skip-fetch")
    run("Phase 2 — normalize", p2_cmd)
    run("Phase 3 — pulse", [py, str(phase3)])
    run("Phase 4 — Google Doc (Drive MCP)", [py, str(phase4)])

    if not args.skip_gmail:
        run("Phase 5 — Gmail draft", [py, str(phase5)])

    print("\nWeekly run complete.")


if __name__ == "__main__":
    main()
