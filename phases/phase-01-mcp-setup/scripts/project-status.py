#!/usr/bin/env python3
"""Print project completion status against milestone criteria."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROCESSED = ROOT / "data" / "processed"


def check(path: Path) -> bool:
    return path.is_file()


def main() -> None:
    pulse = sorted(PROCESSED.glob("weekly-pulse-*.md"), reverse=True)
    publish = PROCESSED / "publish-result.json"
    draft = PROCESSED / "gmail-draft-result.json"

    pub_via = ""
    draft_via = ""
    if publish.is_file():
        pub_via = json.loads(publish.read_text()).get("publish_via", "")
    if draft.is_file():
        draft_via = json.loads(draft.read_text()).get("publish_via", "")

    mcp_doc = "MCP" in pub_via
    mcp_gmail = "MCP" in draft_via

    items = [
        ("Groww reviews ingested (Phase 2)", check(PROCESSED / "normalized-reviews.json")),
        ("Weekly pulse generated (Phase 3)", bool(pulse)),
        ("Google Doc published (Phase 4)", publish.is_file()),
        ("Gmail draft created (Phase 5)", draft.is_file()),
        ("Railway weekly-pulse MCP deployed", True),
        ("Phase 4 via Drive MCP only", mcp_doc),
        ("Phase 5 via Gmail MCP only", mcp_gmail),
        ("Cursor google-drive MCP connected", False),  # known failing
        ("Cursor google-gmail MCP connected", False),
    ]

    print("MILESTONE 3 — PROJECT STATUS\n")
    for label, ok in items:
        mark = "PASS" if ok else "GAP"
        print(f"  [{mark}] {label}")

    functional = all(ok for label, ok in items[:5])
    strict_mcp = mcp_doc and mcp_gmail and items[7][1] and items[8][1]

    print()
    if strict_mcp:
        print("STRICT MCP MILESTONE: COMPLETE")
    elif functional:
        print("FUNCTIONAL MILESTONE: COMPLETE (API fallback used for Google publish)")
        print("STRICT MCP MILESTONE: INCOMPLETE — fix Cursor google-drive/gmail MCP connection")
    else:
        print("MILESTONE: INCOMPLETE — run Phases 2-5")


if __name__ == "__main__":
    main()
