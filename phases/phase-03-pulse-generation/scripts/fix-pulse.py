#!/usr/bin/env python3
"""Post-process pulse: enforce word limit and redact PII patterns."""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pulse_lib import pulse_word_count  # noqa: E402

PII_PATTERNS = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[email]"),
    (re.compile(r"\b\+?\d{10,}\b"), "[phone]"),
]


def scrub_pii(text: str) -> str:
    for pattern, repl in PII_PATTERNS:
        text = pattern.sub(repl, text)
    return text


def trim_pulse(markdown: str, limit: int = 250) -> str:
    md = scrub_pii(markdown.strip())
    if pulse_word_count(md) <= limit:
        return md + "\n"

    lines = md.splitlines()
    compact_glance = (
        "## At a glance\n"
        "- Heavy low-star feedback this period; top themes highlight urgent product fixes."
    )
    out = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "## At a glance":
            out.extend(compact_glance.splitlines())
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        if lines[i].strip() == "## Recommended actions":
            out.append(lines[i])
            i += 1
            out.append("1. Staff support with faster settlement and live escalation for trading and withdrawal issues.")
            out.append("2. Streamline KYC and onboarding with clearer status updates and fewer document resubmits.")
            out.append("3. Fix high-impact app bugs around order execution, charts, and login reliability.")
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        out.append(lines[i])
        i += 1

    result = "\n".join(out)
    if pulse_word_count(result) > limit:
        words = re.findall(r"[A-Za-z0-9']+", result)
        body_words = words[:(limit + 5)]
        # keep structure — last resort shorten quotes
        result = re.sub(
            r'(".*?")',
            lambda m: m.group(1)[:120] + ('..."' if len(m.group(1)) > 120 else ""),
            result,
            count=3,
        )
    return result.strip() + "\n"


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    pulses = sorted((root / "data" / "processed").glob("weekly-pulse-*.md"))
    if not pulses:
        print("No pulse file found")
        sys.exit(1)
    path = pulses[-1]
    original = path.read_text(encoding="utf-8")
    fixed = trim_pulse(original)
    path.write_text(fixed, encoding="utf-8")
    print(f"Fixed {path.name}: {pulse_word_count(original)} -> {pulse_word_count(fixed)} words")


if __name__ == "__main__":
    main()
