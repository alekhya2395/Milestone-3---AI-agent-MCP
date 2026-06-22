#!/usr/bin/env python3
"""Phase 5 — create Gmail draft via Gmail MCP only."""

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
PHASE4_SCRIPTS = ROOT / "phases" / "phase-04-google-docs-mcp" / "scripts"
sys.path.insert(0, str(ROOT / "phases" / "shared"))
sys.path.insert(0, str(PHASE4_SCRIPTS))

from google_oauth import get_access_token  # noqa: E402
from product_config import PRODUCT_NAME  # noqa: E402
from workspace_mcp_client import WorkspaceMcpError, gmail_client  # noqa: E402

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
    return match.group(1) if match else datetime.now(timezone.utc).strftime("%Y-%m-%d")


def load_doc_url() -> str:
    publish_result = PROCESSED / "publish-result.json"
    if publish_result.is_file():
        data = json.loads(publish_result.read_text(encoding="utf-8"))
        url = data.get("doc_url", "").strip()
        if url:
            return url
    doc_id = os.getenv("GOOGLE_DOC_ID", "").strip()
    if doc_id:
        from doc_utils import parse_google_doc_id  # noqa: E402

        return f"https://docs.google.com/document/d/{parse_google_doc_id(doc_id)}/edit"
    return ""


def main() -> None:
    load_dotenv(ROOT / ".env")

    parser = argparse.ArgumentParser(description="Phase 5: Gmail draft via MCP")
    parser.add_argument("--pulse", type=Path, help="Pulse markdown (default: latest)")
    parser.add_argument("--to", help="Recipient email (default: GMAIL_DRAFT_TO from .env)")
    parser.add_argument("--no-doc-link", action="store_true", help="Omit Google Doc URL from body")
    parser.add_argument("--api-only", action="store_true", help="Use Gmail API (skip MCP)")
    args = parser.parse_args()

    recipient = (args.to or os.getenv("GMAIL_DRAFT_TO", "")).strip()
    if not recipient:
        print(
            "ERROR: Set GMAIL_DRAFT_TO in .env or pass --to user@example.com",
            file=sys.stderr,
        )
        sys.exit(1)

    pulse_path = args.pulse or find_latest_pulse()
    pulse_md = pulse_path.read_text(encoding="utf-8").strip()
    pulse_date = pulse_date_from_path(pulse_path)
    subject = f"Weekly Pulse — {PRODUCT_NAME} — {pulse_date}"

    body = pulse_md
    if not args.no_doc_link:
        doc_url = load_doc_url()
        if doc_url:
            body = f"{pulse_md}\n\n---\nGoogle Doc: {doc_url}\n"

    print("Phase 5 — Gmail draft")
    print(f"  To: {recipient}")
    print(f"  Subject: {subject}")

    draft_id = None
    draft = None
    via = ""

    if args.api_only:
        from api_publish import create_gmail_draft  # noqa: E402

        print("  Mode: Gmail API")
        draft = create_gmail_draft(recipient, subject, body)
        draft_id = draft.get("draft_id")
        via = "Gmail API (create_draft)"
    else:
        token = get_access_token()
        client = gmail_client(token)
        try:
            draft = client.call_tool(
                "create_draft",
                {"to": [recipient], "subject": subject, "body": body},
            )
            draft_id = draft.get("id") if isinstance(draft, dict) else None
            via = "google-gmail MCP (create_draft)"
        except WorkspaceMcpError as exc:
            print(f"MCP failed: {exc}")
            print("Using Gmail API fallback...")
            from api_publish import create_gmail_draft  # noqa: E402

            draft = create_gmail_draft(recipient, subject, body)
            draft_id = draft.get("draft_id")
            via = "Gmail API (create_draft fallback)"

    result = {
        "phase": 5,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "publish_via": via,
        "draft_id": draft_id,
        "to": recipient,
        "subject": subject,
        "pulse_file": str(pulse_path.relative_to(ROOT)),
        "draft": draft,
    }
    out = PROCESSED / "gmail-draft-result.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"\nDraft created (id={draft_id}). Check Gmail -> Drafts.")
    print(f"Wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
