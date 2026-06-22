# Phase 5 — Gmail Draft & End-to-End Orchestration

**Status:** Implemented  
**Eval:** [docs/phases/phase-05-gmail-orchestration/eval.md](../../docs/phases/phase-05-gmail-orchestration/eval.md)  
**Plan:** [Implementation Plan — Phase 5](../../docs/implementationplan.md#phase-5--gmail-draft--end-to-end-orchestration)

## Objective

Create a **Gmail draft** via Gmail MCP and run the full weekly workflow end-to-end.

## Scripts

| Path | Purpose |
|------|---------|
| `scripts/create-gmail-draft.py` | Gmail MCP `create_draft` |
| `scripts/run-phase5.py` | Phase 5 entry point |
| `scripts/run-weekly.py` | E2E: Phase 2 → 3 → 4 → 5 |
| `scripts/install-weekly-scheduler.ps1` | Windows Task Scheduler (weekly auto-run) |
| `runbook.md` | Weekly procedure |

## Configuration

Set in `.env`:

```
GMAIL_DRAFT_TO=you@example.com
```

## Quick start

```powershell
python phases/phase-04-google-docs-mcp/scripts/run-phase4.py
python phases/phase-05-gmail-orchestration/scripts/run-phase5.py
```

## Prerequisites

- Phases 3 and 4 complete
- `google-gmail` MCP connected in Cursor
- `GMAIL_DRAFT_TO` in `.env`

## Previous

- **Previous:** [Phase 4](../phase-04-google-docs-mcp/README.md)
