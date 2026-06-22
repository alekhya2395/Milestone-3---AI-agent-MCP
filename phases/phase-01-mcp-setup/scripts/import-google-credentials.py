#!/usr/bin/env python3
"""Import Google OAuth credentials.json into this project.

Copies the file to project root (gitignored) and writes
GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET into .env.

Usage:
  python phases/phase-01-mcp-setup/scripts/import-google-credentials.py path/to/credentials.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = ROOT / ".env"
CREDENTIALS_DEST = ROOT / "credentials.json"


def parse_credentials(path: Path) -> tuple[str, str, str | None]:
    data = json.loads(path.read_text(encoding="utf-8"))
    block = data.get("web") or data.get("installed")
    if not block:
        raise ValueError(
            "Unrecognized JSON format. Expected top-level 'web' or 'installed' key."
        )
    client_id = block.get("client_id", "").strip()
    client_secret = block.get("client_secret", "").strip()
    if not client_id or not client_secret:
        raise ValueError("Missing client_id or client_secret in credentials file.")
    project_id = data.get("project_id") or block.get("project_id")
    return client_id, client_secret, project_id


def update_env(client_id: str, client_secret: str, project_id: str | None) -> None:
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()
    else:
        example = ROOT / ".env.example"
        lines = example.read_text(encoding="utf-8").splitlines() if example.exists() else []

    def set_var(name: str, value: str) -> None:
        nonlocal lines
        prefix = f"{name}="
        for i, line in enumerate(lines):
            if line.startswith(prefix):
                lines[i] = f"{prefix}{value}"
                return
        lines.append(f"{prefix}{value}")

    set_var("GOOGLE_OAUTH_CLIENT_ID", client_id)
    set_var("GOOGLE_OAUTH_CLIENT_SECRET", client_secret)
    if project_id:
        set_var("GOOGLE_CLOUD_PROJECT_ID", project_id)

    ENV_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description="Import Google credentials.json")
    p.add_argument("source", type=Path, help="Path to downloaded credentials JSON")
    args = p.parse_args()

    src = args.source.expanduser().resolve()
    if not src.exists():
        print(f"ERROR: File not found: {src}", file=sys.stderr)
        sys.exit(1)

    client_id, client_secret, project_id = parse_credentials(src)
    shutil.copy2(src, CREDENTIALS_DEST)
    update_env(client_id, client_secret, project_id)

    print(f"Copied -> {CREDENTIALS_DEST}")
    print(f"Updated -> {ENV_PATH}")
    print("Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET")
    if project_id:
        print(f"Set GOOGLE_CLOUD_PROJECT_ID={project_id}")
    print("\nRestart Cursor so MCP picks up the new env vars.")


if __name__ == "__main__":
    main()
