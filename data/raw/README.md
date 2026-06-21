# Raw review exports

Place downloaded App Store and Play Store CSV files here.

## Download Zomato reviews (8–12 weeks)

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

- **Zomato** — App Store `434613896`, Play Store `com.application.zomato`

Files are gitignored by default (size / PII). They remain on your machine under this folder.

**JSON (all reviews combined):** see [`../reviews/reviews.json`](../reviews/README.md)
