# Phase 2 Evaluation — Review Ingestion & Normalization

**Phase:** [Implementation Plan — Phase 2](../implementationplan.md#phase-2--review-ingestion--normalization)

---

## Objectives Under Test

- Public App Store and Play Store exports load correctly
- Reviews normalized to a unified schema
- Date filter restricts to 8–12 week window
- PII removed from processed dataset

---

## Test Cases

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| T2.1 | App Store parse | Load App Store export file | All rows map to `rating`, `title`, `text`, `date`, `source`, `platform` |
| T2.2 | Play Store parse | Load Play Store export file | Same unified schema as T2.1 |
| T2.3 | Schema validation | Inspect sample of 20 normalized rows | No null `date` or `text` on included rows; `platform` ∈ {ios, android} |
| T2.4 | Date window — lower bound | Set window to 8 weeks; run filter | No review older than 8 weeks in output |
| T2.5 | Date window — upper bound | Set window to 12 weeks; run filter | Reviews within 12 weeks included |
| T2.6 | Malformed rows | Include row with missing text in fixture | Row skipped or flagged; pipeline does not crash |
| T2.7 | PII — email | Input review containing `user@example.com` | Email redacted or row excluded from processed output |
| T2.8 | PII — handle | Input with `@username` or display name pattern | Identifier redacted in processed text |
| T2.9 | Volume report | Run ingestion on full exports | Log or report: count per platform, date range, total kept |
| T2.10 | Reproducibility | Re-run ingestion twice on same raw files | Identical processed output (deterministic) |
| T2.11 | Word count | Inspect dropped vs kept | Only reviews with **>6 words** (7+) in title+text kept |
| T2.12 | English only | Sample non-English raw reviews | Excluded from `normalized-reviews.json` |
| T2.13 | Emojis | Sample emoji-heavy reviews | Emojis stripped; empty/short results dropped |

---

## Sample Data Requirements

- Minimum **50 reviews** per platform in test fixture (or full export if smaller)
- At least **3 reviews** with intentional PII patterns for stripper tests
- Date spread covering **>12 weeks** raw data to validate filtering

---

## Manual Verification Checklist

- [ ] Export source URLs documented (public only)
- [ ] Chosen review window (8–12 weeks) recorded in `decision.md`
- [ ] `data/processed/` output inspected manually for 10 random rows
- [ ] No raw PII visible in processed files
- [ ] Milestone 1 product name matches export metadata

---

## Exit Criteria

1. Both store formats ingest without manual per-row fixes.
2. Processed dataset contains only reviews within configured window.
3. PII stripper passes T2.7 and T2.8 on fixture data.
4. Row counts and date range documented.
5. Phase 2 checklist **100% passed**.

---

## Evidence to Capture

- Row count summary (iOS / Android / total)
- Min and max review dates in processed set
- Sample of 3 normalized rows (redacted if needed)

---

## Sign-off

| Role | Name | Date | Pass / Fail |
|------|------|------|-------------|
| Implementer | | | |
| Reviewer | | | |
