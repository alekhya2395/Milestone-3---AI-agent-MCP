#!/usr/bin/env python3
"""Run Phase 3: build bundle -> Groq pulse -> validate."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def run(cmd: list[str]) -> None:
    print(f"\n>> {' '.join(cmd)}\n")
    r = subprocess.run(cmd, cwd=SCRIPTS)
    if r.returncode != 0:
        sys.exit(r.returncode)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", help="Pulse date YYYY-MM-DD")
    p.add_argument("--skip-validate", action="store_true")
    p.add_argument(
        "--publish-doc",
        action="store_true",
        help="After Phase 3, publish pulse via Drive MCP (Phase 4)",
    )
    args = p.parse_args()

    py = sys.executable
    run([py, str(SCRIPTS / "build-llm-bundle.py")])

    gen = [py, str(SCRIPTS / "generate-pulse.py")]
    if args.date:
        gen.extend(["--date", args.date])
    run(gen)

    if not args.skip_validate:
        run([py, str(SCRIPTS / "validate-phase3.py")])

    if args.publish_doc:
        publish = (
            SCRIPTS.parents[1]
            / "phase-04-google-docs-mcp"
            / "scripts"
            / "run-phase4.py"
        )
        print("\nPublishing pulse via Drive MCP (Phase 4)...")
        run([py, str(publish)])

    print("\nPhase 3 complete.")


if __name__ == "__main__":
    main()
