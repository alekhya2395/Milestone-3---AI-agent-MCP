#!/usr/bin/env python3
"""Load Google OAuth client_id/secret from credentials.json into .env."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CREDENTIALS = ROOT / "credentials.json"
ENV_FILE = ROOT / ".env"
ENV_EXAMPLE = ROOT / ".env.example"


def load_oauth_fields(credentials_path: Path) -> tuple[str, str, str | None]:
    data = json.loads(credentials_path.read_text(encoding="utf-8"))
    block = data.get("web") or data.get("installed")
    if not block:
        raise SystemExit(
            f"{credentials_path} must contain a 'web' or 'installed' OAuth client block."
        )

    client_id = block.get("client_id", "").strip()
    client_secret = block.get("client_secret", "").strip()
    project_id = block.get("project_id") or data.get("project_id")

    if not client_id or not client_secret:
        raise SystemExit(f"{credentials_path} is missing client_id or client_secret.")

    return client_id, client_secret, project_id


def upsert_env(lines: list[str], key: str, value: str) -> list[str]:
    prefix = f"{key}="
    updated = False
    result: list[str] = []

    for line in lines:
        if line.startswith(prefix):
            result.append(f"{prefix}{value}")
            updated = True
        else:
            result.append(line)

    if not updated:
        if result and result[-1].strip():
            result.append("")
        result.append(f"{prefix}{value}")

    return result


def main() -> None:
    credentials_path = Path(sys.argv[1]) if len(sys.argv) > 1 else CREDENTIALS
    if not credentials_path.is_file():
        raise SystemExit(
            f"Missing credentials file: {credentials_path}\n"
            "Place credentials.json in the project root, then rerun this script."
        )

    client_id, client_secret, project_id = load_oauth_fields(credentials_path)

    if ENV_FILE.is_file():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    elif ENV_EXAMPLE.is_file():
        lines = ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    lines = upsert_env(lines, "GOOGLE_OAUTH_CLIENT_ID", client_id)
    lines = upsert_env(lines, "GOOGLE_OAUTH_CLIENT_SECRET", client_secret)
    if project_id:
        lines = upsert_env(lines, "GOOGLE_CLOUD_PROJECT_ID", project_id)

    ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Updated {ENV_FILE.relative_to(ROOT)} from {credentials_path.name}")


if __name__ == "__main__":
    main()
