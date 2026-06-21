# Processed data

Outputs from ingestion and pulse generation (Phases 2–3).

| Artifact | Phase | Description |
|----------|-------|-------------|
| `normalized-reviews.json` | 2 | English, >6 words, no emojis, PII-stripped |
| `normalization-summary.json` | 2 | Filter stats (dropped counts) |
| `theme-summary.json` | 3 | Theme counts and rankings |
| `weekly-pulse-YYYY-MM-DD.md` | 3 | Approved pulse before Google publish |

Small test fixtures may live under `fixtures/` and can be committed.
