#!/usr/bin/env python3
"""Verify .cursor/mcp.json and that OAuth env vars resolve."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

MCP_PATH = ROOT / ".cursor" / "mcp.json"

REQUIRED_AUTH_SCOPES = {
    "google-drive": [
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.file",
    ],
    "google-gmail": [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
    ],
}


def resolve_env(value: str) -> str:
    if not isinstance(value, str):
        return value
    if value.startswith("${env:") and value.endswith("}"):
        name = value[6:-1]
        return os.getenv(name, "")
    return value


def main() -> None:
    if not MCP_PATH.is_file():
        print(f"FAIL: missing {MCP_PATH}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(MCP_PATH.read_text(encoding="utf-8"))
    servers = data.get("mcpServers", {})
    ok = True

    for name in ("google-drive", "google-gmail"):
        if name not in servers:
            print(f"FAIL: {name} not in mcp.json", file=sys.stderr)
            ok = False
            continue

        auth = servers[name].get("auth", {})
        cid = resolve_env(auth.get("CLIENT_ID", ""))
        secret = resolve_env(auth.get("CLIENT_SECRET", ""))

        win_cid = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
        dot_cid = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")

        if not cid:
            print(f"FAIL: {name} CLIENT_ID empty (Cursor cannot read .env for remote MCP)")
            print(f"      .env has value: {bool(dot_cid)}")
            print(f"      Windows User env: {bool(win_cid)}")
            print("      Run: python phases/phase-01-mcp-setup/scripts/sync-mcp-env.py")
            ok = False
        else:
            print(f"OK  {name} CLIENT_ID resolves ({cid[:20]}...)")

        if not secret:
            print(f"FAIL: {name} CLIENT_SECRET empty")
            ok = False
        else:
            print(f"OK  {name} CLIENT_SECRET resolves")

        scopes = auth.get("scopes", [])
        expected = REQUIRED_AUTH_SCOPES[name]
        if scopes != expected:
            print(f"WARN {name} scopes should be: {expected}")

    if "weekly-pulse" in servers:
        print("OK  weekly-pulse configured")
    else:
        print("WARN weekly-pulse missing from mcp.json")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
