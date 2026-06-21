"""Shared paths and environment configuration."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT / "data")))

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REVIEWS_DIR = DATA_DIR / "reviews"

FETCH_SCRIPT = ROOT / "phases" / "phase-02-review-ingestion" / "scripts" / "fetch-reviews.py"
NORMALIZE_SCRIPT = ROOT / "phases" / "phase-02-review-ingestion" / "scripts" / "normalize-reviews.py"

MCP_SERVER_API_KEY = os.getenv("MCP_SERVER_API_KEY", "")
