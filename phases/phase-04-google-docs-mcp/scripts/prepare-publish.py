#!/usr/bin/env python3
"""Prepare Phase 4 publish manifest (local pulse + MCP tool sequence)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "phases" / "shared"))
from product_config import PRODUCT_NAME  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
OUT = PROCESSED / "publish-manifest.json"


def main() -> None:
    load_dotenv(ROOT / ".env")

    pulses = sorted(PROCESSED.glob("weekly-pulse-*.md"), reverse=True)
    if not pulses:
        print("ERROR: No weekly-pulse-*.md — run Phase 3 first.", file=sys.stderr)
        sys.exit(1)

    pulse_path = pulses[0]
    pulse_md = pulse_path.read_text(encoding="utf-8")
    pulse_date = pulse_path.stem.replace("weekly-pulse-", "")

    manifest = {
        "phase": 4,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "product": PRODUCT_NAME,
        "doc_title": f"{PRODUCT_NAME} Weekly Pulse — {pulse_date}",
        "pulse_file": str(pulse_path.relative_to(ROOT)),
        "pulse_title_line": pulse_md.splitlines()[0] if pulse_md else "",
        "pulse_word_count": len(pulse_md.split()),
        "publish_via": "google-drive MCP only",
        "mcp_endpoint": "https://drivemcp.googleapis.com/mcp/v1",
        "mcp_tools": ["create_file", "read_file_content", "get_file_metadata"],
        "drive_folder_id": os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip() or None,
        "run_command": "python phases/phase-04-google-docs-mcp/scripts/run-phase4.py",
        "note": "Creates a new Google Doc each run (DEC-008). No direct Docs/Drive REST API.",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Product: {PRODUCT_NAME}")
    print(f"Title:   {manifest['doc_title']}")
    print(f"Pulse:   {pulse_path.name} ({manifest['pulse_word_count']} words)")
    print(f"Wrote:   {OUT.relative_to(ROOT)}")
    print("\nNext: python phases/phase-04-google-docs-mcp/scripts/run-phase4.py")


if __name__ == "__main__":
    main()
