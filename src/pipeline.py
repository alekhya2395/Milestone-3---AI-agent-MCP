"""Pipeline helpers — wrap Phase 2 scripts for MCP tools and cron worker."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone

from src.config import FETCH_SCRIPT, NORMALIZE_SCRIPT, PROCESSED_DIR, REVIEWS_DIR, ROOT


def _ensure_data_dirs() -> None:
    for path in (ROOT / "data" / "raw", ROOT / "data" / "processed", ROOT / "data" / "reviews"):
        path.mkdir(parents=True, exist_ok=True)


def _run_script(script: Path, *args: str) -> str:
    _ensure_data_dirs()
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "").strip()
    errors = (result.stderr or "").strip()
    if result.returncode != 0:
        raise RuntimeError(errors or output or f"{script.name} failed")
    return output or f"{script.name} completed successfully."


def run_fetch_reviews(weeks: int = 10) -> str:
    return _run_script(FETCH_SCRIPT, "--weeks", str(weeks))


def run_normalize_reviews() -> str:
    return _run_script(NORMALIZE_SCRIPT)


def get_review_stats() -> str:
    reviews_file = REVIEWS_DIR / "reviews.json"
    summary_file = PROCESSED_DIR / "normalization-summary.json"

    if not reviews_file.is_file():
        return json.dumps({"error": "reviews.json not found — run fetch_reviews then normalize_reviews first."})

    data = json.loads(reviews_file.read_text(encoding="utf-8"))
    reviews = data.get("reviews", [])
    stats: dict = {
        "review_count": len(reviews),
        "source_file": str(reviews_file.relative_to(ROOT)),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    if summary_file.is_file():
        stats["normalization"] = json.loads(summary_file.read_text(encoding="utf-8"))
    return json.dumps(stats, indent=2)


def get_latest_pulse() -> str:
    pulses = sorted(PROCESSED_DIR.glob("weekly-pulse-*.md"), reverse=True)
    if not pulses:
        return "No weekly pulse artifact found in data/processed/. Run Phase 3 pulse generation first."
    latest = pulses[0]
    return latest.read_text(encoding="utf-8")
