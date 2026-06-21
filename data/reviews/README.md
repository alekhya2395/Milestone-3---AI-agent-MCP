# Combined review exports (JSON)

## Main file (good reviews only)

| File | Description |
|------|-------------|
| **`reviews.json`** | **Good reviews** — English, >6 words, no emojis, PII stripped |
| `appstore-reviews.json` | Good iOS reviews only |
| `playstore-reviews.json` | Good Android reviews only |
| `reviews-raw.json` | Full unfiltered archive (from CSV) |

## Regenerate

```powershell
python phases/phase-02-review-ingestion/scripts/normalize-reviews.py
```

Reads from `data/raw/*.csv`, writes filtered output here and to `data/processed/normalized-reviews.json`.

See `data/processed/normalization-summary.json` for drop counts.
