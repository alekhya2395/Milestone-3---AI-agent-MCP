# Raw review exports

Place downloaded App Store and Play Store CSV files here.

## Download Groww reviews (8–12 weeks)

From project root:

```powershell
pip install -r requirements.txt
python phases/phase-02-review-ingestion/scripts/fetch-reviews.py
```

Default window is **10 weeks**. Use `--weeks 12` for a wider window:

```powershell
python phases/phase-02-review-ingestion/scripts/fetch-reviews.py --weeks 12
```

## Output files

| File | Description |
|------|-------------|
| `appstore-reviews-YYYY-MM-DD.csv` | iOS reviews in window |
| `playstore-reviews-YYYY-MM-DD.csv` | Android reviews in window |
| `export-summary-YYYY-MM-DD.json` | Counts and date ranges |

## Product (Milestone 1)

- **Groww** — App Store `1404871703`, Play Store `com.nextbillion.groww`

Configure via `.env`: `PRODUCT_NAME`, `APP_STORE_ID`, `PLAY_PACKAGE`.

Normalization uses the **latest** `export-summary-*.json` only (older Zomato exports are ignored).

Files are gitignored by default (size / PII). They remain on your machine under this folder.

**JSON (all reviews combined):** see [`../reviews/reviews.json`](../reviews/README.md)
