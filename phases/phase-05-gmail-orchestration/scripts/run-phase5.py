#!/usr/bin/env python3
"""Run Phase 5: Gmail draft via MCP."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent


def main() -> None:
    cmd = [sys.executable, str(SCRIPTS / "create-gmail-draft.py"), *sys.argv[1:]]
    print(f">> {' '.join(cmd)}\n")
    sys.exit(subprocess.call(cmd))


if __name__ == "__main__":
    main()
