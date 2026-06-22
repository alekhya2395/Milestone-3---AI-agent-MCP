#!/usr/bin/env python3
"""Validate Phase 3 artifacts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pulse_lib import pulse_word_count  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
PROCESSED = ROOT / "data" / "processed"

PII_RE = [
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    re.compile(r"\b\+?\d{10,}\b"),
]


def main() -> None:
    errors: list[str] = []

    bundle = PROCESSED / "llm-input-bundle.json"
    theme = PROCESSED / "theme-summary.json"
    pulses = sorted(PROCESSED.glob("weekly-pulse-*.md"))

    if not bundle.exists():
        errors.append("missing llm-input-bundle.json")
    if not theme.exists():
        errors.append("missing theme-summary.json")
    if not pulses:
        errors.append("missing weekly-pulse-*.md")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)

    bundle_data = json.loads(bundle.read_text(encoding="utf-8"))
    theme_data = json.loads(theme.read_text(encoding="utf-8"))
    pulse_path = pulses[-1]
    pulse_md = pulse_path.read_text(encoding="utf-8")

    if bundle_data.get("groq_sample_size", 0) > 120:
        errors.append("groq sample exceeds 120")
    if len(theme_data.get("top_3_themes", [])) != 3:
        errors.append("top_3_themes must have 3 entries")

    words = pulse_word_count(pulse_md)
    if words > 250:
        errors.append(f"pulse word count {words} > 250")

    for section in ("## At a glance", "## Top themes", "## What users are saying", "## Recommended actions"):
        if section not in pulse_md:
            errors.append(f"missing section: {section}")

    for p in PII_RE:
        if p.search(pulse_md):
            errors.append("possible PII in pulse")

    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    print(f"OK: {bundle.name} (sample {bundle_data.get('groq_sample_size')})")
    print(f"OK: {theme.name} (top: {[t['theme'] for t in theme_data['top_3_themes']]})")
    print(f"OK: {pulse_path.name} ({words} words)")
    print("\nPhase 3 validation passed.")


if __name__ == "__main__":
    main()
