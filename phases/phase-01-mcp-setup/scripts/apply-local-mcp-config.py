#!/usr/bin/env python3
"""Write .cursor/mcp.json with literal credentials from .env (fixes Cursor MCP errors on Windows).

Merges ALL MCP servers into one project config and clears conflicting global ~/.cursor/mcp.json.

Usage (Cursor must be fully quit first):
  python phases/phase-01-mcp-setup/scripts/apply-local-mcp-config.py
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MCP_PATH = ROOT / ".cursor" / "mcp.json"
BACKUP = ROOT / ".cursor" / "mcp.json.env-interpolation.bak"
GLOBAL_MCP = Path.home() / ".cursor" / "mcp.json"
GLOBAL_BACKUP = Path.home() / ".cursor" / "mcp.json.bak"

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()
CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
ALPHA_KEY = os.getenv("ALPHAVANTAGE_API_KEY", "").strip()

if not CLIENT_ID or not CLIENT_SECRET:
    print("ERROR: Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET in .env", file=sys.stderr)
    sys.exit(1)

servers: dict = {
    "weekly-pulse": {
        "url": "https://milestone-3-ai-agent-mcp-production.up.railway.app/mcp",
    },
    "google-drive": {
        "url": "https://drivemcp.googleapis.com/mcp/v1",
        "auth": {
            "CLIENT_ID": CLIENT_ID,
            "CLIENT_SECRET": CLIENT_SECRET,
            "scopes": [
                "https://www.googleapis.com/auth/drive.readonly",
                "https://www.googleapis.com/auth/drive.file",
            ],
        },
    },
    "google-gmail": {
        "url": "https://gmailmcp.googleapis.com/mcp/v1",
        "auth": {
            "CLIENT_ID": CLIENT_ID,
            "CLIENT_SECRET": CLIENT_SECRET,
            "scopes": [
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.compose",
            ],
        },
    },
}

if ALPHA_KEY:
    servers["alphavantage"] = {
        "url": f"https://mcp.alphavantage.co/mcp?apikey={ALPHA_KEY}",
    }

CONFIG = {"mcpServers": servers}


def main() -> None:
    MCP_PATH.parent.mkdir(parents=True, exist_ok=True)
    if MCP_PATH.is_file() and not BACKUP.is_file():
        shutil.copy2(MCP_PATH, BACKUP)
        print(f"Backup -> {BACKUP.relative_to(ROOT)}")

    MCP_PATH.write_text(json.dumps(CONFIG, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {MCP_PATH.relative_to(ROOT)} ({len(servers)} servers)")

    GLOBAL_MCP.parent.mkdir(parents=True, exist_ok=True)
    if GLOBAL_MCP.is_file() and not GLOBAL_BACKUP.is_file():
        shutil.copy2(GLOBAL_MCP, GLOBAL_BACKUP)
        print(f"Backup global -> {GLOBAL_BACKUP}")
    GLOBAL_MCP.write_text('{\n  "mcpServers": {}\n}\n', encoding="utf-8")
    print("Cleared global ~/.cursor/mcp.json (avoids duplicate alphavantage/google servers)")

    print("\nNext:")
    print("  1. Fully quit Cursor (File > Exit)")
    print("  2. Run: .\\phases\\phase-01-mcp-setup\\scripts\\reset-all-mcp.ps1")
    print("  3. Reopen Cursor -> Tools & MCP -> Connect google-drive & google-gmail")


if __name__ == "__main__":
    main()
