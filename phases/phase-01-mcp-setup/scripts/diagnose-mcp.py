#!/usr/bin/env python3
"""Diagnose MCP setup issues — run from project root."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

RAILWAY = "https://milestone-3-ai-agent-mcp-production.up.railway.app"
DRIVE_MCP = "https://drivemcp.googleapis.com/mcp/v1"
GMAIL_MCP = "https://gmailmcp.googleapis.com/mcp/v1"
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID", "YOUR_PROJECT_ID").strip()


def ok(msg: str) -> None:
    print(f"  OK  {msg}")


def warn(msg: str) -> None:
    print(f"  WARN  {msg}")


def fail(msg: str) -> None:
    print(f"  FAIL  {msg}")


def check_env() -> list[str]:
    issues: list[str] = []
    print("\n=== .env variables ===")
    required = {
        "GOOGLE_OAUTH_CLIENT_ID": "OAuth client ID (Cursor MCP)",
        "GOOGLE_OAUTH_CLIENT_SECRET": "OAuth client secret (Cursor MCP)",
        "GROQ_API_KEY": "Groq LLM (Phase 3)",
        "GMAIL_DRAFT_TO": "Gmail draft recipient (Phase 5)",
    }
    for key, desc in required.items():
        val = os.getenv(key, "").strip()
        if not val:
            fail(f"{key} missing — {desc}")
            issues.append(key)
        elif key == "GMAIL_DRAFT_TO" and "@" not in val:
            fail(f"{key} invalid (needs @) — got {val!r}")
            issues.append(key)
        else:
            ok(f"{key} set")
    return issues


def check_mcp_json() -> list[str]:
    issues: list[str] = []
    print("\n=== .cursor/mcp.json ===")
    path = ROOT / ".cursor" / "mcp.json"
    if not path.is_file():
        fail("Missing .cursor/mcp.json")
        return ["mcp.json"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        servers = data.get("mcpServers", {})
        for name in ("weekly-pulse", "google-drive", "google-gmail"):
            if name in servers:
                ok(f"{name} configured")
            else:
                fail(f"{name} missing from mcpServers")
                issues.append(name)
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {exc}")
        issues.append("mcp.json")
    return issues


def probe_url(label: str, url: str) -> None:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            ok(f"{label} reachable (HTTP {resp.status})")
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403, 404, 405):
            ok(f"{label} reachable (HTTP {exc.code} — expected without OAuth)")
        else:
            warn(f"{label} HTTP {exc.code}")
    except Exception as exc:
        fail(f"{label} unreachable: {exc}")


def check_endpoints() -> None:
    print("\n=== Endpoint reachability ===")
    probe_url("Railway weekly-pulse", f"{RAILWAY}/health")
    probe_url("Google Drive MCP", DRIVE_MCP)
    probe_url("Google Gmail MCP", GMAIL_MCP)


def check_token() -> None:
    print("\n=== Local OAuth token (Phase 4/5 scripts) ===")
    token_path = ROOT / "token.json"
    if not token_path.is_file():
        warn("token.json missing — run run-phase4.py after fixing Drive MCP (browser sign-in)")
        return
    data = json.loads(token_path.read_text(encoding="utf-8"))
    scopes = data.get("scopes") or data.get("scope", "").split()
    expected = {
        "https://www.googleapis.com/auth/drive.readonly",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.compose",
    }
    missing = expected - set(scopes)
    if missing:
        warn(f"token.json missing MCP scopes: {sorted(missing)}")
        warn("Delete token.json and re-run run-phase4.py")
    else:
        ok("token.json has Drive + Gmail MCP scopes")


def print_fix_steps(issues: list[str]) -> None:
    print("\n" + "=" * 60)
    print("FIX STEPS (do in order)")
    print("=" * 60)

    print("""
1. GCP — Enable APIs (Console, project: %s)
   https://console.cloud.google.com/apis/library/drive.googleapis.com?project=%s
   https://console.cloud.google.com/apis/library/drivemcp.googleapis.com?project=%s
   https://console.cloud.google.com/apis/library/gmailmcp.googleapis.com?project=%s

2. GCP — OAuth consent screen -> Data Access -> Add scopes:
   Drive:  drive.readonly, drive.file
   Gmail:  gmail.readonly, gmail.compose
   https://console.cloud.google.com/auth/scopes?project=%s

3. GCP — OAuth client redirect URI (must be exact):
   cursor://anysphere.cursor-mcp/oauth/callback
   https://console.cloud.google.com/auth/clients?project=%s

4. GCP — Add your Gmail as Test user (if app is External):
   https://console.cloud.google.com/auth/audience?project=%s

5. Cursor — Settings -> Tools & MCP:
   - Run sync-mcp-env.py first if google-drive AND google-gmail both show Error
   - google-drive: click Logout -> toggle off -> on -> Connect (complete sign-in)
   - google-gmail: same reconnect steps
   - weekly-pulse: toggle ON (Railway server for Phase 2/3)

6. Restart Cursor completely (quit and reopen) so .env is loaded.

7. Smoke test in chat:
   "Using google-drive MCP, list_recent_files"
   "Using google-gmail MCP, list_labels"

8. Run publish pipeline:
   python phases/phase-04-google-docs-mcp/scripts/run-phase4.py
   python phases/phase-05-gmail-orchestration/scripts/run-phase5.py
""" % (PROJECT_ID, PROJECT_ID, PROJECT_ID, PROJECT_ID, PROJECT_ID, PROJECT_ID, PROJECT_ID))

    if issues:
        print("Issues detected:", ", ".join(issues))


def main() -> None:
    print("MCP setup diagnostic")
    print(f"Project root: {ROOT}")
    issues: list[str] = []
    issues.extend(check_env())
    issues.extend(check_mcp_json())
    check_endpoints()
    check_token()
    print_fix_steps(issues)
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
