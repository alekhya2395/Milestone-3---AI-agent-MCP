#!/usr/bin/env python3
"""Sync OAuth vars from .env to Windows User environment (required for Cursor MCP).

Cursor ${env:VAR} in .cursor/mcp.json does NOT read project .env for remote MCP servers.
Run this script, then fully quit and reopen Cursor.

Usage:
  python phases/phase-01-mcp-setup/scripts/sync-mcp-env.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: pip install python-dotenv", file=sys.stderr)
    sys.exit(1)

VARS = (
    "GOOGLE_OAUTH_CLIENT_ID",
    "GOOGLE_OAUTH_CLIENT_SECRET",
    "GROQ_API_KEY",
)


def main() -> None:
    load_dotenv(ROOT / ".env")

    if sys.platform != "win32":
        print("This script targets Windows User env vars.")
        print("On macOS/Linux, export vars in your shell profile instead.")
        sys.exit(1)

    import winreg  # noqa: WPS433

    missing = []
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Environment",
        0,
        winreg.KEY_READ | winreg.KEY_SET_VALUE,
    ) as key:
        for name in VARS:
            value = os.getenv(name, "").strip()
            if not value:
                missing.append(name)
                continue
            winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
            os.environ[name] = value
            print(f"OK  {name} -> Windows User environment")

    if missing:
        print(f"\nFAIL: missing in .env: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)

    print("\nDone. Fully QUIT Cursor (File > Exit), then reopen.")
    print("Settings -> Tools & MCP -> Logout google-drive & google-gmail -> reconnect.")


if __name__ == "__main__":
    main()
