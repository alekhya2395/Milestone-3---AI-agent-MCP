#!/usr/bin/env python3
"""DEPRECATED — use run-phase4.py (Drive MCP only).

This script uses the Google Docs REST API directly, which violates Phase 4 eval
(T4.7 MCP-only audit). Kept as a manual fallback only.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from doc_utils import parse_google_doc_id  # noqa: E402
from google_auth import get_credentials  # noqa: E402


def find_latest_pulse() -> Path:
    processed = ROOT / "data" / "processed"
    pulses = sorted(processed.glob("weekly-pulse-*.md"), reverse=True)
    if not pulses:
        print("ERROR: No weekly-pulse-*.md — run Phase 3 first.", file=sys.stderr)
        sys.exit(1)
    return pulses[0]


def replace_doc_content(doc_id: str, text: str) -> None:
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build("docs", "v1", credentials=creds, cache_discovery=False)

    doc = service.documents().get(documentId=doc_id).execute()
    body = doc.get("body", {}).get("content", [])
    end_index = body[-1].get("endIndex", 1) - 1 if body else 1

    requests = []
    if end_index > 1:
        requests.append(
            {"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end_index}}}
        )
    requests.append({"insertText": {"location": {"index": 1}, "text": text}})

    service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()


def verify_doc(doc_id: str, expected_snippet: str) -> str:
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build("docs", "v1", credentials=creds, cache_discovery=False)
    doc = service.documents().get(documentId=doc_id).execute()
    title = doc.get("title", "")
    text = ""
    for el in doc.get("body", {}).get("content", []):
        para = el.get("paragraph")
        if not para:
            continue
        for elem in para.get("elements", []):
            text += elem.get("textRun", {}).get("content", "")
    ok = expected_snippet[:40] in text
    return f"title={title!r} chars={len(text)} verified={ok}"


def main() -> None:
    load_dotenv(ROOT / ".env")

    parser = argparse.ArgumentParser(description="Publish pulse to Google Doc")
    parser.add_argument("--doc-id", help="Google Doc ID (default: GOOGLE_DOC_ID from .env)")
    parser.add_argument("--pulse", type=Path, help="Pulse markdown file (default: latest)")
    args = parser.parse_args()

    raw_doc = args.doc_id or os.getenv("GOOGLE_DOC_ID", "").strip()
    if not raw_doc:
        print("ERROR: Set GOOGLE_DOC_ID in .env or pass --doc-id", file=sys.stderr)
        sys.exit(1)

    doc_id = parse_google_doc_id(raw_doc)
    pulse_path = args.pulse or find_latest_pulse()
    pulse_text = pulse_path.read_text(encoding="utf-8").strip() + "\n"

    print(f"Publishing {pulse_path.name} -> Doc {doc_id}...")
    replace_doc_content(doc_id, pulse_text)

    snippet = pulse_text.splitlines()[0] if pulse_text else ""
    check = verify_doc(doc_id, snippet)
    print(f"Verify: {check}")

    result = {
        "published_at": datetime.now(timezone.utc).isoformat(),
        "doc_id": doc_id,
        "doc_url": f"https://docs.google.com/document/d/{doc_id}/edit",
        "pulse_file": str(pulse_path.relative_to(ROOT)),
        "verification": check,
    }
    out = ROOT / "data" / "processed" / "publish-result.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"\nDone. Open: {result['doc_url']}")


if __name__ == "__main__":
    main()
