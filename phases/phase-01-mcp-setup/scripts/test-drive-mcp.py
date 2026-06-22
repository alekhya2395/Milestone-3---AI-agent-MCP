#!/usr/bin/env python3
"""Test Drive MCP list_recent_files via OAuth token."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "phases" / "phase-04-google-docs-mcp" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from google_oauth import get_access_token  # noqa: E402
from workspace_mcp_client import WorkspaceMcpError, drive_client  # noqa: E402


def main() -> None:
    try:
        token = get_access_token()
        client = drive_client(token)
        result = client.call_tool("list_recent_files", {"pageSize": 5})
        files = result.get("files", []) if isinstance(result, dict) else []
        print("Drive MCP test: SUCCESS")
        print(f"Recent files: {len(files)}")
        for f in files:
            print(f"  - {f.get('title', '?')} | {f.get('mimeType', '?')}")
    except WorkspaceMcpError as exc:
        print(f"Drive MCP test: FAILED - {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
