#!/usr/bin/env python3
"""Validate Google OAuth / MCP auth setup before running auth.py."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CREDENTIALS = ROOT / "credentials.json"
ENV_FILE = ROOT / ".env"
MCP_FILE = ROOT / ".cursor" / "mcp.json"
TOKEN_FILE = ROOT / "token.json"

EXPECTED_EMAIL = "dhulipudialekhya@gmail.com"
EXPECTED_PROJECT = "silver-treat-499611-r3"


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_FILE.is_file():
        return values
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            values[key] = val
    return values


def main() -> None:
    ok = True
    env = load_env()

    print("=== Auth setup check ===\n")

    # credentials.json
    if not CREDENTIALS.is_file():
        print("FAIL  credentials.json missing")
        ok = False
    else:
        data = json.loads(CREDENTIALS.read_text(encoding="utf-8"))
        if "installed" in data:
            print("OK    credentials.json (Desktop client - for auth.py)")
            pid = data["installed"].get("project_id", "")
            if pid != EXPECTED_PROJECT:
                print(f"WARN  project_id is '{pid}' (expected {EXPECTED_PROJECT})")
        elif "web" in data:
            print("WARN  credentials.json is Web client — auth.py needs Desktop client JSON")
            ok = False
        else:
            print("FAIL  credentials.json has no 'installed' or 'web' block")
            ok = False

    # .env
    for key in ("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET", "GOOGLE_CLOUD_PROJECT_ID"):
        if env.get(key):
            print(f"OK    .env has {key}")
        else:
            print(f"FAIL  .env missing {key}")
            ok = False

    # MCP config
    if MCP_FILE.is_file():
        mcp = json.loads(MCP_FILE.read_text(encoding="utf-8"))
        servers = mcp.get("mcpServers", {})
        for name in ("google-gmail", "google-drive"):
            if name in servers:
                print(f"OK    .cursor/mcp.json has {name}")
            else:
                print(f"FAIL  .cursor/mcp.json missing {name}")
                ok = False
    else:
        print("FAIL  .cursor/mcp.json missing")
        ok = False

    # Windows env (Cursor MCP)
    for key in ("GOOGLE_OAUTH_CLIENT_ID", "GOOGLE_OAUTH_CLIENT_SECRET"):
        if os.environ.get(key):
            print(f"OK    Windows env has {key} (Cursor can read it)")
        else:
            print(f"WARN  Windows env missing {key} - run set-google-oauth-env.ps1, restart Cursor")

    # token
    if TOKEN_FILE.is_file():
        print("OK    token.json exists")
    else:
        print("INFO  token.json not yet created - run: python auth.py")

    print("\n=== GCP action required (cannot fix from code) ===")
    print(f"Add test user in Google Cloud Console:")
    print(f"  https://console.cloud.google.com/auth/audience?project={EXPECTED_PROJECT}")
    print(f"  Test users -> Add: {EXPECTED_EMAIL}")
    print("\nFor Cursor MCP also create a Web OAuth client with redirect URI:")
    print("  cursor://anysphere.cursor-mcp/oauth/callback")
    print("  Put Web client ID/secret in .env (Desktop client is only for auth.py)")

    if not ok:
        raise SystemExit("\nFix the FAIL items above, then run: python auth.py")
    print("\nLocal setup looks good. Run: python auth.py")


if __name__ == "__main__":
    main()
