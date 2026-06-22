"""Google Doc ID helpers for Phase 4."""

from __future__ import annotations

import re

DOC_ID_RE = re.compile(r"/document/d/([a-zA-Z0-9_-]+)")
RAW_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{20,}$")


def parse_google_doc_id(value: str) -> str:
    """Accept raw Doc ID or full Google Docs URL; return ID only."""
    value = (value or "").strip()
    if not value:
        return ""
    match = DOC_ID_RE.search(value)
    if match:
        return match.group(1)
    if RAW_ID_RE.match(value):
        return value
    raise ValueError(
        "GOOGLE_DOC_ID must be the Doc ID or a docs.google.com URL, "
        "e.g. 1AwEeMAJA5KRT-y8cfcI2ndnw6JQXSyPItYFkUsRLyz4"
    )
