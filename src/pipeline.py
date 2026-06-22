"""Pipeline helpers — wrap Phase 2/3 scripts for MCP tools and cron worker."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.config import (
    BUILD_BUNDLE_SCRIPT,
    FETCH_SCRIPT,
    GENERATE_PULSE_SCRIPT,
    NORMALIZE_SCRIPT,
    PROCESSED_DIR,
    REVIEWS_DIR,
    ROOT,
    RUN_PHASE3_SCRIPT,
    RUN_PHASE4_SCRIPT,
    RUN_PHASE5_SCRIPT,
)


def _ensure_data_dirs() -> None:
    for path in (ROOT / "data" / "raw", PROCESSED_DIR, REVIEWS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def _run_script(script: Path, *args: str) -> str:
    _ensure_data_dirs()
    env = None
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    output = (result.stdout or "").strip()
    errors = (result.stderr or "").strip()
    combined = "\n".join(x for x in (output, errors) if x)
    if result.returncode != 0:
        raise RuntimeError(combined or f"{script.name} failed")
    return output or f"{script.name} completed successfully."


def run_fetch_reviews(weeks: int = 10) -> str:
    return _run_script(FETCH_SCRIPT, "--weeks", str(weeks))


def run_normalize_reviews(weeks: int = 10) -> str:
    return _run_script(NORMALIZE_SCRIPT, "--weeks", str(weeks))


def run_build_llm_bundle() -> str:
    return _run_script(BUILD_BUNDLE_SCRIPT)


def run_generate_pulse(pulse_date: str | None = None) -> str:
    args: list[str] = []
    if pulse_date:
        args.extend(["--date", pulse_date])
    return _run_script(GENERATE_PULSE_SCRIPT, *args)


def run_phase3(pulse_date: str | None = None) -> str:
    args: list[str] = []
    if pulse_date:
        args.extend(["--date", pulse_date])
    return _run_script(RUN_PHASE3_SCRIPT, *args)


def get_review_stats() -> str:
    reviews_file = REVIEWS_DIR / "reviews.json"
    summary_file = PROCESSED_DIR / "normalization-summary.json"
    llm_file = PROCESSED_DIR / "reviews-for-llm.json"

    if not reviews_file.is_file():
        return json.dumps(
            {"error": "reviews.json not found — run fetch_reviews then normalize_reviews first."}
        )

    data = json.loads(reviews_file.read_text(encoding="utf-8"))
    reviews = data.get("reviews", [])
    stats: dict = {
        "review_count": len(reviews),
        "source_file": str(reviews_file.relative_to(ROOT)),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    if summary_file.is_file():
        stats["normalization"] = json.loads(summary_file.read_text(encoding="utf-8"))
    if llm_file.is_file():
        llm = json.loads(llm_file.read_text(encoding="utf-8"))
        stats["llm_corpus_count"] = llm.get("total_count", len(llm.get("reviews", [])))
    return json.dumps(stats, indent=2)


def get_theme_summary() -> str:
    path = PROCESSED_DIR / "theme-summary.json"
    if not path.is_file():
        return json.dumps(
            {"error": "theme-summary.json not found — run generate_pulse or run_phase3 first."}
        )
    return path.read_text(encoding="utf-8")


def get_llm_bundle() -> str:
    path = PROCESSED_DIR / "llm-input-bundle.json"
    if not path.is_file():
        return json.dumps(
            {"error": "llm-input-bundle.json not found — run build_llm_bundle first."}
        )
    return path.read_text(encoding="utf-8")


def get_latest_pulse() -> str:
    pulses = sorted(PROCESSED_DIR.glob("weekly-pulse-*.md"), reverse=True)
    if not pulses:
        return "No weekly pulse artifact found in data/processed/. Run generate_pulse first."
    latest = pulses[0]
    header = f"<!-- {latest.name} -->\n"
    return header + latest.read_text(encoding="utf-8")


def _write_scheduler_log(record: dict) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    (PROCESSED_DIR / "scheduler-last-run.json").write_text(
        json.dumps(record, indent=2), encoding="utf-8"
    )


def run_weekly_job(
    weeks: int = 10,
    *,
    fetch: bool = True,
    pulse: bool = True,
    publish: bool = False,
    api_only: bool = True,
    skip_gmail: bool = False,
) -> str:
    """Scheduled weekly job: refresh reviews, generate pulse, optionally publish."""
    started = datetime.now(timezone.utc)
    steps: dict[str, str] = {}
    error: str | None = None

    try:
        if fetch:
            steps["fetch"] = run_fetch_reviews(weeks)
            steps["normalize"] = run_normalize_reviews(weeks)
        if pulse:
            steps["phase3"] = run_phase3()
        if publish:
            p4_args = ["--api-only"] if api_only else []
            steps["phase4"] = _run_script(RUN_PHASE4_SCRIPT, *p4_args)
            if not skip_gmail:
                p5_args = ["--api-only"] if api_only else []
                steps["phase5"] = _run_script(RUN_PHASE5_SCRIPT, *p5_args)
        status = "success"
    except Exception as exc:
        status = "failed"
        error = str(exc)

    finished = datetime.now(timezone.utc)
    pulses = sorted(PROCESSED_DIR.glob("weekly-pulse-*.md"), reverse=True)
    record = {
        "status": status,
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "weeks": weeks,
        "fetch": fetch,
        "pulse": pulse,
        "publish": publish,
        "api_only": api_only,
        "latest_pulse": pulses[0].name if pulses else None,
        "steps": {k: v[:500] for k, v in steps.items()},
        "error": error,
    }
    _write_scheduler_log(record)

    if error:
        raise RuntimeError(error)

    lines = [
        f"Weekly job {status} ({finished.isoformat()})",
        f"Latest pulse: {record['latest_pulse'] or 'none'}",
    ]
    for name, summary in steps.items():
        first_line = summary.splitlines()[0] if summary else "ok"
        lines.append(f"  {name}: {first_line[:120]}")
    lines.append(f"Log: data/processed/scheduler-last-run.json")
    return "\n".join(lines)
