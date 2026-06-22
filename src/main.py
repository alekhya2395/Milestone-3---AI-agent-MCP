"""Weekly Pulse MCP server — Streamable HTTP for Railway + Cursor."""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.pipeline import (
    get_latest_pulse,
    get_llm_bundle,
    get_review_stats,
    get_theme_summary,
    run_build_llm_bundle,
    run_fetch_reviews,
    run_generate_pulse,
    run_normalize_reviews,
    run_phase3,
    run_weekly_job as execute_weekly_job,
)

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))
RAILWAY_URL = os.getenv(
    "RAILWAY_PUBLIC_DOMAIN",
    "milestone-3-ai-agent-mcp-production.up.railway.app",
)

mcp = FastMCP(
    "weekly-pulse",
    host=HOST,
    port=PORT,
    stateless_http=True,
)


@mcp.custom_route("/", methods=["GET"])
async def root(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "service": "weekly-pulse-mcp",
            "status": "running",
            "endpoints": {
                "health": "/health",
                "mcp": "/mcp",
            },
            "tools": [
                "fetch_reviews",
                "normalize_reviews",
                "review_stats",
                "build_llm_bundle",
                "generate_pulse",
                "run_phase3",
                "run_weekly_job",
                "scheduler_status",
                "theme_summary",
                "llm_bundle",
                "latest_pulse",
            ],
        }
    )


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "weekly-pulse-mcp"})


@mcp.tool()
def fetch_reviews(weeks: int = 10) -> str:
    """Download public App Store and Play Store reviews into data/raw/."""
    return run_fetch_reviews(weeks)


@mcp.tool()
def normalize_reviews(weeks: int = 10) -> str:
    """Normalize, filter, de-PII reviews; build reviews-for-llm.json (Phase 2)."""
    return run_normalize_reviews(weeks)


@mcp.tool()
def review_stats() -> str:
    """Return JSON summary of normalized review counts and LLM corpus size."""
    return get_review_stats()


@mcp.tool()
def build_llm_bundle() -> str:
    """Build llm-input-bundle.json — stats on 1,000 reviews + ~120 Groq sample (Phase 3 step 1)."""
    return run_build_llm_bundle()


@mcp.tool()
def generate_pulse(pulse_date: str = "") -> str:
    """Generate theme-summary.json and weekly-pulse markdown via 2 Groq calls (Phase 3).

    Requires GROQ_API_KEY in environment. Optional pulse_date as YYYY-MM-DD.
    Returns path summary and latest pulse content.
    """
    date_arg = pulse_date.strip() or None
    output = run_generate_pulse(date_arg)
    pulse = get_latest_pulse()
    return f"{output}\n\n---\n\n{pulse}"


@mcp.tool()
def run_phase3_pipeline(pulse_date: str = "") -> str:
    """Full Phase 3: build_llm_bundle -> generate_pulse -> validate."""
    date_arg = pulse_date.strip() or None
    output = run_phase3(date_arg)
    pulse = get_latest_pulse()
    return f"{output}\n\n---\n\n{pulse}"


@mcp.tool()
def run_weekly_job(
    weeks: int = 10,
    fetch: bool = True,
    pulse: bool = True,
    publish: bool = False,
) -> str:
    """Scheduled weekly job: refresh Groww reviews, generate pulse, optional publish.

    Default (Railway cron): fetch + normalize + Phase 3 pulse.
    Set publish=true only when Google credentials are configured on the host.
    """
    return execute_weekly_job(
        weeks,
        fetch=fetch,
        pulse=pulse,
        publish=publish,
        api_only=True,
    )


@mcp.tool()
def scheduler_status() -> str:
    """Return the last scheduler run log (scheduler-last-run.json)."""
    from pathlib import Path

    from src.config import PROCESSED_DIR

    path = PROCESSED_DIR / "scheduler-last-run.json"
    if not path.is_file():
        return '{"status":"never_run","hint":"Call run_weekly_job or run python -m src.worker"}'
    return path.read_text(encoding="utf-8")


@mcp.tool()
def theme_summary() -> str:
    """Return theme-summary.json — ranked themes, stats, quote candidates."""
    return get_theme_summary()


@mcp.tool()
def llm_bundle() -> str:
    """Return llm-input-bundle.json — corpus stats and Groq sample."""
    return get_llm_bundle()


@mcp.tool()
def latest_pulse() -> str:
    """Return the most recent weekly-pulse-YYYY-MM-DD.md content."""
    return get_latest_pulse()


def main() -> None:
    print(f"Starting weekly-pulse MCP on {HOST}:{PORT}", flush=True)
    print(f"Public URL hint: https://{RAILWAY_URL}/mcp", flush=True)
    print("Routes: GET / GET /health POST /mcp", flush=True)
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
