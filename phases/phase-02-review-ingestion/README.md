# Phase 2 — Review Ingestion & Normalization

**Status:** Not started (blocked on Phase 1 eval optional; data work can begin after repo ready)  
**Eval:** [docs/phases/phase-02-review-ingestion/eval.md](../../docs/phases/phase-02-review-ingestion/eval.md)  
**Plan:** [Implementation Plan — Phase 2](../../docs/implementationplan.md#phase-2--review-ingestion--normalization)

## Objective

Import public App Store and Play Store exports into a unified, PII-stripped dataset for the configured 8–12 week window.

## Folders & artifacts

| Path | Purpose |
|------|---------|
| `../../data/raw/` | Downloaded CSV exports (**start here**) |
| `scripts/fetch-reviews.py` | Download 8–12 weeks of public reviews |
| `fixtures/` | Small sample files for eval tests |
| `notes/` | Export URLs, column mapping notes |

### Download reviews

```powershell
pip install -r requirements.txt
python phases/phase-02-review-ingestion/scripts/fetch-reviews.py --weeks 10
```

Files appear in **`data/raw/`** (gitignored but on disk).

### Normalize (English, >6 words, no emojis)

```powershell
python phases/phase-02-review-ingestion/scripts/normalize-reviews.py
```

Output: **`data/processed/normalized-reviews.json`**

## Planned deliverables

- Normalized review dataset
- PII sanitization verified
- Ingestion summary (counts, date range)
- Phase 2 eval signed off

## Prerequisites

- Milestone 1 product exports downloaded to `data/raw/`
- Export provenance recorded in [docs/decision.md](../../docs/decision.md)

## Previous / next

- **Previous:** [Phase 1](../phase-01-mcp-setup/README.md)
- **Next:** [Phase 3](../phase-03-pulse-generation/README.md)
