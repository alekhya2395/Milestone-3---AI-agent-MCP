#!/usr/bin/env python3
"""Validate Phase 4 artifacts (local checks; MCP calls require run-phase4.py)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROCESSED = ROOT / "data" / "processed"


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    pulses = sorted(PROCESSED.glob("weekly-pulse-*.md"), reverse=True)
    if not pulses:
        fail("No weekly-pulse-*.md")

    manifest = PROCESSED / "publish-manifest.json"
    if manifest.is_file():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("publish_via") != "google-drive MCP only":
            fail("publish-manifest.json publish_via is not MCP-only")
        print(f"OK: manifest title={data.get('doc_title')}")
    else:
        print("WARN: publish-manifest.json missing — run prepare-publish.py")

    result = PROCESSED / "publish-result.json"
    if result.is_file():
        data = json.loads(result.read_text(encoding="utf-8"))
        via = data.get("publish_via", "")
        if "MCP" not in via:
            print(f"WARN: publish-result.json is from legacy publish ({via!r}) — re-run run-phase4.py")
        elif not data.get("doc_url"):
            fail("publish-result.json missing doc_url")
        else:
            v = data.get("verification", {})
            if not v.get("verified"):
                fail("publish-result verification failed")
            print(f"OK: published {data.get('doc_url')}")
    else:
        print("WARN: publish-result.json missing — run run-phase4.py")

    # Audit: main path must not import googleapiclient
    deprecated = ROOT / "phases" / "phase-04-google-docs-mcp" / "scripts" / "publish-pulse-to-doc.py"
    if deprecated.is_file():
        text = deprecated.read_text(encoding="utf-8")
        if "DEPRECATED" not in text[:500]:
            fail("publish-pulse-to-doc.py should be marked DEPRECATED")

    print(f"OK: latest pulse {pulses[0].name}")
    print("\nPhase 4 validation passed (local).")


if __name__ == "__main__":
    main()
