#!/usr/bin/env python3
"""Run Phase 2 end-to-end: fetch -> normalize -> validate."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print(f"\n>> {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=SCRIPTS)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main() -> None:
    p = argparse.ArgumentParser(description="Phase 2 review ingestion pipeline")
    p.add_argument("--weeks", type=int, default=10, help="Review window (8-12 weeks)")
    p.add_argument("--llm-cap", type=int, default=1000, help="LLM corpus cap")
    p.add_argument("--skip-fetch", action="store_true", help="Skip fetch-reviews.py")
    p.add_argument("--skip-validate", action="store_true", help="Skip validate-phase2.py")
    args = p.parse_args()

    py = sys.executable

    if not args.skip_fetch:
        run([py, str(SCRIPTS / "fetch-reviews.py"), "--weeks", str(args.weeks)])

    run(
        [
            py,
            str(SCRIPTS / "normalize-reviews.py"),
            "--weeks",
            str(args.weeks),
            "--llm-cap",
            str(args.llm_cap),
        ]
    )

    if not args.skip_validate:
        run([py, str(SCRIPTS / "validate-phase2.py")])

    print("\nPhase 2 complete.")


if __name__ == "__main__":
    main()
