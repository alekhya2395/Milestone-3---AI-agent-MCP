#!/usr/bin/env python3
"""Generate theme summary and weekly pulse via 2 Groq calls (Phase 3)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from pulse_lib import (
    GROQ_MODEL,
    THEME_VOCABULARY,
    corpus_stats,
    pick_quotes,
    pulse_word_count,
    rank_themes,
    select_groq_sample,
    truncate_text,
    utc_now_iso,
)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "phases" / "shared"))
from product_config import PRODUCT_NAME, pulse_title  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
LLM_CORPUS = PROCESSED / "reviews-for-llm.json"
BUNDLE_PATH = PROCESSED / "llm-input-bundle.json"
USAGE_LOG = PROCESSED / "groq-usage-log.json"


def load_env() -> str:
    load_dotenv(ROOT / ".env")
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        print("ERROR: Set GROQ_API_KEY in .env or environment", file=sys.stderr)
        sys.exit(1)
    return key


def load_prompt(name: str, fallback: str) -> str:
    path = ROOT / "prompts" / name
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return fallback


def groq_call(client: Groq, messages: list[dict], json_mode: bool = False) -> tuple[str, dict]:
    kwargs: dict = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.2,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    usage = {
        "prompt_tokens": resp.usage.prompt_tokens if resp.usage else 0,
        "completion_tokens": resp.usage.completion_tokens if resp.usage else 0,
        "total_tokens": resp.usage.total_tokens if resp.usage else 0,
    }
    return resp.choices[0].message.content or "", usage


def call1_theme_tag(client: Groq, groq_sample: list[dict]) -> tuple[list[dict], dict]:
    themes_list = "\n".join(f"- {t}" for t in THEME_VOCABULARY)
    user_payload = json.dumps({"reviews": groq_sample}, ensure_ascii=False)
    system = load_prompt(
        "theming.md",
        (
            "You assign each app review to exactly ONE theme from the fixed vocabulary. "
            "Return JSON only: {\"assignments\": [{\"id\": 0, \"theme\": \"...\"}, ...]}. "
            f"Use only these themes:\n{themes_list}"
        ),
    )

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_payload},
    ]

    raw, usage = groq_call(client, messages, json_mode=True)
    try:
        parsed = json.loads(raw)
        assignments = parsed.get("assignments", [])
    except json.JSONDecodeError:
        print("ERROR: Groq call 1 returned invalid JSON", file=sys.stderr)
        print(raw[:500], file=sys.stderr)
        sys.exit(1)

    return assignments, usage


def call2_pulse_write(
    client: Groq,
    top_themes: list[dict],
    stats: dict,
    quote_candidates: list[dict],
) -> tuple[str, dict]:
    themes_block = "\n".join(
        f"{t['rank']}. {t['theme']} (score {t['score']}, {t['review_count']} reviews)"
        for t in top_themes[:3]
    )
    quotes_block = "\n".join(
        f"- [{q['theme']}] ({q['rating']}★) \"{q['text'][:200]}\""
        for q in quote_candidates[:9]
    )

    system = load_prompt(
        "pulse-format.md",
        (
            f"Write a weekly review pulse for {PRODUCT_NAME} product leadership. "
            f"Use EXACTLY this markdown structure:\n\n"
            f"# {PRODUCT_NAME} — Weekly Review Pulse (DATE)\n\n"
            "## At a glance\n"
            "- [1-2 sentences]\n\n"
            "## Top themes\n"
            "1. [Theme] — [why it matters]\n"
            "2. ...\n"
            "3. ...\n\n"
            "## What users are saying\n"
            "- \"[quote 1]\"\n"
            "- \"[quote 2]\"\n"
            "- \"[quote 3]\"\n\n"
            "## Recommended actions\n"
            "1. [action for theme 1]\n"
            "2. [action for theme 2]\n"
            "3. [action for theme 3]\n\n"
            "Rules: ≤250 words total (all sections after title), no PII, "
            "exactly 3 themes/quotes/actions, quotes must come from candidates, "
            "actions grounded in themes. Replace DATE with the pulse date provided."
        ),
    )

    messages = [
        {"role": "system", "content": system},
        {
            "role": "user",
            "content": (
                f"Pulse date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}\n\n"
                f"Stats: {json.dumps(stats, ensure_ascii=False)}\n\n"
                f"Top themes:\n{themes_block}\n\n"
                f"Quote candidates (pick 3, lightly edit for clarity, keep anonymous):\n{quotes_block}"
            ),
        },
    ]

    return groq_call(client, messages, json_mode=False)


def append_usage_log(calls: list[dict]) -> None:
    log = {"runs": []}
    if USAGE_LOG.exists():
        log = json.loads(USAGE_LOG.read_text(encoding="utf-8"))
    log["runs"].append(
        {
            "generated_at": utc_now_iso(),
            "model": GROQ_MODEL,
            "calls": calls,
            "total_tokens": sum(c.get("usage", {}).get("total_tokens", 0) for c in calls),
        }
    )
    USAGE_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--date", help="Pulse date YYYY-MM-DD (default: today UTC)")
    p.add_argument("--delay", type=float, default=2.0, help="Seconds between Groq calls")
    args = p.parse_args()

    pulse_date = args.date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not LLM_CORPUS.exists():
        print("ERROR: Run Phase 2 first.", file=sys.stderr)
        sys.exit(1)

    corpus_data = json.loads(LLM_CORPUS.read_text(encoding="utf-8"))
    reviews = corpus_data.get("reviews", [])

    if BUNDLE_PATH.exists():
        bundle = json.loads(BUNDLE_PATH.read_text(encoding="utf-8"))
        groq_sample = bundle.get("groq_sample", [])
        stats = bundle.get("corpus_stats", corpus_stats(reviews))
    else:
        sample_rows = select_groq_sample(reviews)
        groq_sample = [
            {
                "id": i,
                "platform": r.get("platform"),
                "date": r.get("date"),
                "rating": r.get("rating"),
                "text": truncate_text(r.get("title", ""), r.get("text", "")),
            }
            for i, r in enumerate(sample_rows)
        ]
        stats = corpus_stats(reviews)

    sample_rows = select_groq_sample(reviews)
    client = Groq(api_key=load_env())
    usage_calls: list[dict] = []

    print(f"Groq call 1: theme tagging ({len(groq_sample)} reviews)...")
    assignments, u1 = call1_theme_tag(client, groq_sample)
    usage_calls.append({"step": "theme_tag", "usage": u1})
    print(f"  tokens: {u1['total_tokens']}")

    groq_themes: dict[int, str] = {}
    for item in assignments:
        idx = item.get("id")
        theme = item.get("theme", "")
        if theme not in THEME_VOCABULARY:
            continue
        if isinstance(idx, int) and 0 <= idx < len(sample_rows):
            groq_themes[id(sample_rows[idx])] = theme
    all_ranked = rank_themes(reviews, groq_themes=groq_themes)
    top3 = all_ranked[:3]

    quote_candidates = []
    for t in top3:
        for r in pick_quotes(reviews, t["theme"], n=3):
            quote_candidates.append(
                {
                    "theme": t["theme"],
                    "rating": r.get("rating"),
                    "text": (r.get("text") or r.get("title", ""))[:300],
                    "date": r.get("date"),
                }
            )

    time.sleep(args.delay)

    print("Groq call 2: pulse writing...")
    pulse_md, u2 = call2_pulse_write(client, top3, stats, quote_candidates)
    usage_calls.append({"step": "pulse_write", "usage": u2})
    print(f"  tokens: {u2['total_tokens']}")

    if f"({pulse_date})" not in pulse_md and pulse_date not in pulse_md:
        pulse_md = pulse_md.replace(
            "Weekly Review Pulse",
            f"Weekly Review Pulse ({pulse_date})",
            1,
        )

    theme_path = PROCESSED / "theme-summary.json"
    pulse_path = PROCESSED / f"weekly-pulse-{pulse_date}.md"
    pulse_path.write_text(pulse_md.strip() + "\n", encoding="utf-8")

    subprocess.run([sys.executable, str(Path(__file__).parent / "fix-pulse.py")], check=True)
    pulse_md = pulse_path.read_text(encoding="utf-8")
    words = pulse_word_count(pulse_md)

    theme_summary = {
        "product": PRODUCT_NAME,
        "generated_at": utc_now_iso(),
        "pulse_date": pulse_date,
        "corpus_stats": stats,
        "theme_vocabulary": THEME_VOCABULARY,
        "groq_sample_assignments": assignments,
        "ranked_themes": all_ranked,
        "top_3_themes": top3,
        "quote_candidates": quote_candidates,
        "pulse_word_count": words,
    }

    theme_path.write_text(json.dumps(theme_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    append_usage_log(usage_calls)

    print(f"\nWrote {theme_path}")
    print(f"Wrote {pulse_path} ({words} words)")
    print(f"Top themes: {', '.join(t['theme'] for t in top3)}")
    print(f"Groq usage log -> {USAGE_LOG}")


if __name__ == "__main__":
    main()
