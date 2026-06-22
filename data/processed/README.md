# Processed data

Outputs from ingestion and pulse generation (Phases 2–3).

## Phase 2 (review ingestion)

| Artifact | Description |
|----------|-------------|
| `normalized-reviews.json` | All good reviews: English, >6 words, no emojis, PII-stripped |
| `reviews-for-llm.json` | **≤1,000** stratified subset for Phase 3 Groq |
| `normalization-summary.json` | Filter stats, date range, rating distribution, LLM corpus counts |
| `ingestion-summary.json` | Full Phase 2 report + Phase 3 handoff metadata |

Regenerate:

```powershell
python phases/phase-02-review-ingestion/scripts/run-phase2.py --skip-fetch --weeks 10
```

## Phase 3 (pulse generation — future)

| Artifact | Description |
|----------|-------------|
| `theme-summary.json` | Theme counts and rankings |
| `weekly-pulse-YYYY-MM-DD.md` | Approved pulse before Google publish |

Small test fixtures may live under `fixtures/` and can be committed.
