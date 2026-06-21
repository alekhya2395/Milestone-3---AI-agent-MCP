# Phase 3 Evaluation — Theme Analysis & Pulse Generation

**Phase:** [Implementation Plan — Phase 3](../implementationplan.md#phase-3--theme-analysis--pulse-generation)

---

## Objectives Under Test

- Reviews clustered into ≤5 themes
- Weekly pulse contains top 3 themes, 3 quotes, 3 action ideas
- Pulse is ≤250 words, scannable, and PII-free
- Output saved as local artifact before MCP publish

---

## Test Cases

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| T3.1 | Theme count | Run theming on full processed dataset | ≤5 distinct themes assigned |
| T3.2 | Top 3 themes | Inspect pulse output | Exactly 3 themes highlighted with clear labels |
| T3.3 | User quotes | Count quotes in pulse | Exactly 3 quotes, each tied to a theme |
| T3.4 | Action ideas | Count actions in pulse | Exactly 3 actionable recommendations |
| T3.5 | Word limit | Run word count on pulse body | ≤250 words |
| T3.6 | Scannable format | Visual review of markdown | Headings + bullets; readable in <2 minutes |
| T3.7 | PII scan | Search pulse for email, @handle, user ID patterns | Zero matches |
| T3.8 | Quote anonymization | Compare selected quotes to raw reviews | No usernames or identifiable strings |
| T3.9 | Theme relevance | Manual review by reviewer | Themes match product domain (e.g. KYC, payments) |
| T3.10 | Action quality | Manual review | Each action is specific, feasible, tied to a theme |
| T3.11 | Artifact saved | Check `data/processed/weekly-pulse-*.md` | File exists with correct date stamp |
| T3.12 | Empty / sparse data | Run with <10 reviews fixture | Graceful message or degraded pulse; no crash |

---

## Content Rubric (Manual)

| Criterion | 1 — Fail | 2 — Pass | 3 — Exceeds |
|-----------|----------|----------|-------------|
| Theme clarity | Vague or duplicate themes | 3 distinct, labeled themes | Themes ranked with severity/volume hint |
| Quote representativeness | Off-topic or duplicate | One strong quote per top theme | Quotes illustrate pain and sentiment |
| Action usefulness | Generic (“improve UX”) | Specific next steps per theme | Prioritized with owner hint (e.g. Product, Eng) |

**Pass threshold:** All criteria ≥2.

---

## Manual Verification Checklist

- [ ] Pulse reviewed against processed review sample for factual grounding
- [ ] Word count verified (tool or manual)
- [ ] Theme vocabulary documented in prompts or `decision.md`
- [ ] Second person on team can understand pulse without extra context

---

## Exit Criteria

1. Pulse artifact meets **all** structural requirements (3+3+3, ≤250 words).
2. PII scan clean on final artifact.
3. Content rubric ≥2 on all criteria.
4. Local markdown file saved and versioned (or gitignored with sample committed).
5. Phase 3 checklist **100% passed**.

---

## Evidence to Capture

- Final `weekly-pulse-YYYY-MM-DD.md`
- Word count output
- Theme distribution summary (count per theme)

---

## Sign-off

| Role | Name | Date | Pass / Fail |
|------|------|------|-------------|
| Implementer | | | |
| Reviewer | | | |
