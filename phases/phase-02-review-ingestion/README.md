# Phase 2 — Review Ingestion & Normalization

**Status:** Implemented  
**Eval:** [docs/phases/phase-02-review-ingestion/eval.md](../../docs/phases/phase-02-review-ingestion/eval.md)  
**Plan:** [Implementation Plan — Phase 2](../../docs/implementationplan.md#phase-2--review-ingestion--normalization)

## Objective

Import public App Store and Play Store exports into a unified, PII-stripped dataset for the configured 8–12 week window. Build a **≤1,000** review Groq-ready corpus for Phase 3 (no LLM calls in Phase 2).

## Quick start (full pipeline)

```powershell
pip install -r requirements.txt
python phases/phase-02-review-ingestion/scripts/run-phase2.py --weeks 10
```

Use `--skip-fetch` if CSVs already exist in `data/raw/`. Use `--skip-validate` to skip T2.x checks.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/run-phase2.py` | Orchestrator: fetch → normalize → validate |
| `scripts/fetch-reviews.py` | Download 8–12 weeks of public reviews |
| `scripts/normalize-reviews.py` | Filter, PII strip, build LLM corpus |
| `scripts/validate-phase2.py` | Artifact and schema checks (T2.x) |
| `scripts/review_lib.py` | Shared normalization + corpus selection |
| `scripts/csv-to-reviews-json.py` | Legacy merge helper (prefer normalize) |

## Data flow

```
data/raw/*.csv
    → normalize-reviews.py
        → data/reviews/reviews-raw.json      (full unfiltered archive)
        → data/reviews/reviews.json          (good reviews, main file)
        → data/processed/normalized-reviews.json
        → data/processed/reviews-for-llm.json  (≤1,000 for Phase 3)
        → data/processed/normalization-summary.json
        → data/processed/ingestion-summary.json
```

## Normalization rules (DEC-016)

- English only (`langdetect`)
- More than 6 words (title + text)
- Emojis stripped
- PII redacted (email, phone, @handles)

## LLM corpus selection (§5.1)

From normalized reviews, select **≤1,000** into `reviews-for-llm.json`:

- Recent first (within window)
- ~50% low ratings (1–2★)
- Prefer longer review text

Phase 3 uses this file for local stats + a ~120-review Groq sample (2 API calls).

## Fixtures

`fixtures/sample-reviews.csv` — small CSV for manual eval / smoke tests.

## Prerequisites

- Milestone 1 product exports in `data/raw/` (or run `fetch-reviews.py`)
- `pip install langdetect` (in `requirements.txt`)

## Previous / next

- **Previous:** [Phase 1](../phase-01-mcp-setup/README.md)
- **Next:** [Phase 3](../phase-03-pulse-generation/README.md)
