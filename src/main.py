"""Weekly Pulse MCP server — Streamable HTTP for Railway + Cursor."""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.pipeline import get_latest_pulse, get_review_stats, run_fetch_reviews, run_normalize_reviews

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8080"))

mcp = FastMCP(
    "weekly-pulse",
    host=HOST,
    port=PORT,
    stateless_http=True,
)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "healthy", "service": "weekly-pulse-mcp"})


@mcp.tool()
def fetch_reviews(weeks: int = 10) -> str:
    """Download public App Store and Play Store reviews into data/raw/."""
    return run_fetch_reviews(weeks)


@mcp.tool()
def normalize_reviews() -> str:
    """Normalize, filter, and de-PII reviews into data/reviews/reviews.json."""
    return run_normalize_reviews()


@mcp.tool()
def review_stats() -> str:
    """Return JSON summary of normalized review counts."""
    return get_review_stats()


@mcp.tool()
def latest_pulse() -> str:
    """Return the most recent weekly-pulse-YYYY-MM-DD.md content."""
    return get_latest_pulse()


def main() -> None:
    print(f"Starting weekly-pulse MCP on {HOST}:{PORT}", flush=True)
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
