#!/usr/bin/env python3
"""Phase 4 — publish weekly pulse to Google Doc via Drive MCP only."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "phases" / "shared"))
sys.path.insert(0, str(SCRIPTS))

from doc_utils import parse_google_doc_id  # noqa: E402
from google_oauth import get_access_token  # noqa: E402
from product_config import PRODUCT_NAME  # noqa: E402
from workspace_mcp_client import (  # noqa: E402
    WorkspaceMcpError,
    drive_client,
    normalize_doc_text,
)

PROCESSED = ROOT / "data" / "processed"
PULSE_DATE_RE = re.compile(r"weekly-pulse-(\d{4}-\d{2}-\d{2})\.md$")


def find_latest_pulse() -> Path:
    pulses = sorted(PROCESSED.glob("weekly-pulse-*.md"), reverse=True)
    if not pulses:
        print("ERROR: No weekly-pulse-*.md — run Phase 3 first.", file=sys.stderr)
        sys.exit(1)
    return pulses[0]


def pulse_date_from_path(path: Path) -> str:
    match = PULSE_DATE_RE.search(path.name)
    if match:
        return match.group(1)
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def doc_title(pulse_date: str) -> str:
    return f"{PRODUCT_NAME} Weekly Pulse — {pulse_date}"


def verify_content(local_md: str, remote_text: str) -> dict:
    local_norm = normalize_doc_text(local_md)
    remote_norm = normalize_doc_text(remote_text)
    snippet = local_norm.splitlines()[0][:60] if local_norm else ""
    themes_ok = all(
        theme in remote_norm
        for theme in ("Top themes", "What users are saying", "Recommended actions")
        if theme in local_norm
    )
    snippet_ok = bool(snippet and snippet in remote_norm)
    return {
        "verified": snippet_ok and themes_ok,
        "snippet_ok": snippet_ok,
        "sections_ok": themes_ok,
        "local_chars": len(local_norm),
        "remote_chars": len(remote_norm),
    }


def publish_via_api(
    pulse_md: str,
    pulse_path: Path,
    title: str,
    pulse_date: str,
) -> dict:
    """Fallback: Docs/Drive API when MCP is unavailable."""
    from api_publish import create_new_google_doc, publish_pulse_to_doc  # noqa: E402

    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    existing = os.getenv("GOOGLE_DOC_ID", "").strip()

    print("\nDrive MCP unavailable — using Google Docs API fallback...")
    if existing:
        doc_id = parse_google_doc_id(existing)
        check = publish_pulse_to_doc(doc_id, pulse_md)
        doc_id_out = doc_id
        doc_url = check["doc_url"]
        via = "Google Docs API (update existing doc)"
    else:
        check = create_new_google_doc(title, pulse_md, folder_id)
        doc_id_out = check["doc_id"]
        doc_url = check["doc_url"]
        via = "Google Docs API (create new doc)"

    verification = {
        "verified": check.get("verified", False),
        "remote_chars": check.get("chars", 0),
        "title": check.get("title", title),
    }
    print(f"  Doc: {doc_url}")
    print(f"  Verify: title={verification['title']!r} verified={verification['verified']}")

    result = {
        "phase": 4,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "publish_via": via,
        "doc_id": doc_id_out,
        "doc_url": doc_url,
        "doc_title": title,
        "pulse_file": str(pulse_path.relative_to(ROOT)),
        "verification": verification,
    }
    out = PROCESSED / "publish-result.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote {out.relative_to(ROOT)}")
    print(f"Done. Open: {doc_url}")
    return result


def main() -> None:
    load_dotenv(ROOT / ".env")

    parser = argparse.ArgumentParser(description="Phase 4: publish pulse via Drive MCP")
    parser.add_argument("--pulse", type=Path, help="Pulse markdown (default: latest)")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Read GOOGLE_DOC_ID via MCP and verify against local pulse (no create)",
    )
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Skip MCP; publish via Google Docs API (fallback)",
    )
    args = parser.parse_args()

    pulse_path = args.pulse or find_latest_pulse()
    pulse_md = pulse_path.read_text(encoding="utf-8").strip() + "\n"
    pulse_date = pulse_date_from_path(pulse_path)
    title = doc_title(pulse_date)

    if args.api_only:
        publish_via_api(pulse_md, pulse_path, title, pulse_date)
        return

    print("Phase 4 — Drive MCP publish")
    print(f"  Pulse: {pulse_path.name} ({len(pulse_md.split())} words)")
    print(f"  Title: {title}")

    token = get_access_token()
    client = drive_client(token)

    folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
    existing_doc = os.getenv("GOOGLE_DOC_ID", "").strip()

    if args.verify_only:
        if not existing_doc:
            print("ERROR: Set GOOGLE_DOC_ID for --verify-only", file=sys.stderr)
            sys.exit(1)
        doc_id = parse_google_doc_id(existing_doc)
        print(f"  Verify existing Doc: {doc_id}")
        meta = client.call_tool("get_file_metadata", {"fileId": doc_id})
        content = client.call_tool("read_file_content", {"fileId": doc_id})
        remote = content.get("fileContent", "") if isinstance(content, dict) else str(content)
        check = verify_content(pulse_md, remote)
        print(f"  Metadata title: {meta.get('title') if isinstance(meta, dict) else meta}")
        print(f"  Parity: {check}")
        sys.exit(0 if check["verified"] else 1)

    create_args: dict = {
        "title": title,
        "textContent": pulse_md,
        "contentMimeType": "text/plain",
    }
    if folder_id:
        create_args["parentId"] = folder_id

    print("\nCalling Drive MCP create_file...")
    try:
        created = client.call_tool("create_file", create_args)
    except WorkspaceMcpError as exc:
        print(f"MCP failed: {exc}", file=sys.stderr)
        publish_via_api(pulse_md, pulse_path, title, pulse_date)
        return

    doc_id = created.get("id") if isinstance(created, dict) else None
    doc_url = created.get("viewUrl") if isinstance(created, dict) else None
    if not doc_id:
        raise WorkspaceMcpError(
            f"Unexpected create_file response: {created!r}\n"
            "Try: delete token.json and re-run (browser OAuth with Drive + Gmail scopes)."
        )
    if not doc_url:
        doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"

    print(f"  Created Doc id={doc_id}")
    print("Calling Drive MCP read_file_content (verify)...")
    content = client.call_tool("read_file_content", {"fileId": doc_id})
    remote = content.get("fileContent", "") if isinstance(content, dict) else str(content)
    check = verify_content(pulse_md, remote)
    print(f"  Parity: verified={check['verified']} remote_chars={check['remote_chars']}")

    result = {
        "phase": 4,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "publish_via": "google-drive MCP (create_file + read_file_content)",
        "mcp_endpoint": "https://drivemcp.googleapis.com/mcp/v1",
        "doc_id": doc_id,
        "doc_url": doc_url,
        "doc_title": title,
        "pulse_file": str(pulse_path.relative_to(ROOT)),
        "verification": check,
    }
    out = PROCESSED / "publish-result.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nWrote {out.relative_to(ROOT)}")
    print(f"Done. Open: {doc_url}")

    if not check["verified"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
