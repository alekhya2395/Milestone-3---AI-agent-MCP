# Evaluation — Milestone 3 (Master)

Master evaluation index for the **Weekly Review Pulse AI Agent with MCP**. Use this file to track overall milestone readiness; use **phase eval files** for detailed tests and exit criteria before advancing each phase.

---

## How Evaluation Works

1. **Phase gate** — Complete the phase’s `eval.md` checklist and exit criteria before starting the next phase.
2. **Milestone gate** — When all five phases pass, complete the **Milestone Acceptance** section below.

| Phase | Name | Detailed eval |
|-------|------|----------------|
| 1 | MCP & project foundation | [phases/phase-01-mcp-setup/eval.md](./phases/phase-01-mcp-setup/eval.md) |
| 2 | Review ingestion & normalization | [phases/phase-02-review-ingestion/eval.md](./phases/phase-02-review-ingestion/eval.md) |
| 3 | Theme analysis & pulse generation | [phases/phase-03-pulse-generation/eval.md](./phases/phase-03-pulse-generation/eval.md) |
| 4 | Google Docs via Drive MCP | [phases/phase-04-google-docs-mcp/eval.md](./phases/phase-04-google-docs-mcp/eval.md) |
| 5 | Gmail draft & E2E orchestration | [phases/phase-05-gmail-orchestration/eval.md](./phases/phase-05-gmail-orchestration/eval.md) |

---

## Phase Gate Status

Update as you complete each phase.

| Phase | Eval file | Status | Date passed | Notes |
|-------|-----------|--------|-------------|-------|
| 1 | [phase-01-mcp-setup/eval.md](./phases/phase-01-mcp-setup/eval.md) | 🟡 In progress | | Repo + MCP config scaffolded; OAuth smoke tests pending |
| 2 | [phase-02-review-ingestion/eval.md](./phases/phase-02-review-ingestion/eval.md) | ⬜ Not started | | |
| 3 | [phase-03-pulse-generation/eval.md](./phases/phase-03-pulse-generation/eval.md) | ⬜ Not started | | |
| 4 | [phase-04-google-docs-mcp/eval.md](./phases/phase-04-google-docs-mcp/eval.md) | ⬜ Not started | | |
| 5 | [phase-05-gmail-orchestration/eval.md](./phases/phase-05-gmail-orchestration/eval.md) | ⬜ Not started | | |

**Status legend:** ⬜ Not started · 🟡 In progress · ✅ Passed · ❌ Failed (blocked)

---

## Milestone Acceptance Criteria

Derived from [problemstatement.md](./problemstatement.md). All must pass for milestone completion.

| ID | Criterion | Verified in phase | Pass |
|----|-----------|-------------------|------|
| M1 | Reviews from **8–12 weeks** imported and themed correctly | Phase 2, 3, 5 | ⬜ |
| M2 | Weekly pulse: **top 3 themes**, **3 quotes**, **3 action ideas** | Phase 3, 5 | ⬜ |
| M3 | Pulse is **≤250 words** and scannable | Phase 3, 5 | ⬜ |
| M4 | **Google Doc** created via **Drive MCP** only | Phase 4, 5 | ⬜ |
| M5 | **Gmail draft** created via **Gmail MCP** only (self/alias) | Phase 5 | ⬜ |
| M6 | **No PII** in Doc, email, or artifacts | Phase 2, 3, 5 | ⬜ |
| M7 | **No direct Google API** usage in agent code | Phase 1, 4, 5 | ⬜ |
| M8 | **Public exports only** — no login scraping | Phase 2 | ⬜ |
| M9 | **≤5 themes** when clustering; top 3 in final note | Phase 3 | ⬜ |
| M10 | Full **E2E run** documented (ingest → pulse → Doc → draft) | Phase 5 | ⬜ |

---

## Milestone Test Summary

High-level tests that span multiple phases. Details live in phase `eval.md` files.

| ID | Test | Phases | Expected result |
|----|------|--------|-----------------|
| E2E-1 | Happy path | 1–5 | One agent run produces pulse, Google Doc, and Gmail draft |
| E2E-2 | MCP auth | 1, 4, 5 | Drive + Gmail MCP authenticate without 403 (or documented admin fix) |
| E2E-3 | Content traceability | 3, 4, 5 | Doc and email body match approved local pulse artifact |
| E2E-4 | PII audit | 2, 3, 5 | Automated or manual scan finds zero PII in deliverables |
| E2E-5 | Code audit | 4, 5 | No `googleapis` / Gmail / Drive SDK in `src/` |
| E2E-6 | Operator runbook | 5 | New operator can run weekly job using docs only |
| E2E-7 | Constraint compliance | 2, 3 | Public data only; theme and word limits enforced |

---

## Pre-Submission Checklist

Before marking the milestone complete:

- [ ] All five phase eval files signed off (implementer + reviewer)
- [ ] All milestone acceptance criteria (M1–M10) checked
- [ ] `decision.md` updated (product name, review window, Gmail recipient, Doc policy)
- [ ] Evidence captured: pulse artifact, Doc link, draft screenshot (internal only)
- [ ] No secrets in repository
- [ ] Runbook or execution notes available for weekly repeat

---

## Evidence Register

| Artifact | Location / link | Date | Owner |
|----------|-----------------|------|-------|
| Processed reviews | `data/processed/` | | |
| Weekly pulse (markdown) | `data/processed/weekly-pulse-*.md` | | |
| Google Doc | (internal link) | | |
| Gmail draft | (screenshot or draft ID) | | |
| E2E run log | | | |

---

## Milestone Sign-off

| Role | Name | Date | Pass / Fail |
|------|------|------|-------------|
| Implementer | | | |
| Reviewer | | | |

**Milestone complete when:** All phase gates ✅ and all M1–M10 criteria ✅.

---

## Related Documents

- [Problem Statement](./problemstatement.md)
- [Architecture](./architecture.md)
- [Implementation Plan](./implementationplan.md)
- [Decisions Log](./decision.md)
