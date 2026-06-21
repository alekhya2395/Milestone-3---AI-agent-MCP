# Phase 3 — Theme Analysis & Pulse Generation

**Status:** Not started  
**Eval:** [docs/phases/phase-03-pulse-generation/eval.md](../../docs/phases/phase-03-pulse-generation/eval.md)  
**Plan:** [Implementation Plan — Phase 3](../../docs/implementationplan.md#phase-3--theme-analysis--pulse-generation)

## Objective

Generate the weekly pulse (top 3 themes, 3 quotes, 3 actions, ≤250 words) as a **local markdown artifact** for operator approval before Google publish.

## Folders & artifacts

| Path | Purpose |
|------|---------|
| `../../data/processed/weekly-pulse-*.md` | Approved pulse |
| `../../data/processed/theme-summary.json` | Theme rankings |
| `../../prompts/` | Agent prompts for theming and pulse |
| `samples/` | Example pulses for eval rubric |

## Planned deliverables

- Theme vocabulary and clustering output
- Approved `weekly-pulse-YYYY-MM-DD.md`
- Phase 3 eval signed off

## Prerequisites

- Phase 2 complete: `normalized-reviews.json`

## Previous / next

- **Previous:** [Phase 2](../phase-02-review-ingestion/README.md)
- **Next:** [Phase 4](../phase-04-google-docs-mcp/README.md)
