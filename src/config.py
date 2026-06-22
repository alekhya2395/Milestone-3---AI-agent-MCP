"""Shared paths and environment configuration."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT / "data")))

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REVIEWS_DIR = DATA_DIR / "reviews"

PHASE2_SCRIPTS = ROOT / "phases" / "phase-02-review-ingestion" / "scripts"
PHASE3_SCRIPTS = ROOT / "phases" / "phase-03-pulse-generation" / "scripts"
PHASE4_SCRIPTS = ROOT / "phases" / "phase-04-google-docs-mcp" / "scripts"
PHASE5_SCRIPTS = ROOT / "phases" / "phase-05-gmail-orchestration" / "scripts"

FETCH_SCRIPT = PHASE2_SCRIPTS / "fetch-reviews.py"
NORMALIZE_SCRIPT = PHASE2_SCRIPTS / "normalize-reviews.py"
BUILD_BUNDLE_SCRIPT = PHASE3_SCRIPTS / "build-llm-bundle.py"
GENERATE_PULSE_SCRIPT = PHASE3_SCRIPTS / "generate-pulse.py"
RUN_PHASE3_SCRIPT = PHASE3_SCRIPTS / "run-phase3.py"
RUN_PHASE4_SCRIPT = PHASE4_SCRIPTS / "run-phase4.py"
RUN_PHASE5_SCRIPT = PHASE5_SCRIPTS / "create-gmail-draft.py"

REVIEW_WEEKS = int(os.getenv("REVIEW_WEEKS", "10"))

MCP_SERVER_API_KEY = os.getenv("MCP_SERVER_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
