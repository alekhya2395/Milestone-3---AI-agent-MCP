# Phase 4 — Google Docs via Drive MCP

**Status:** Implemented (Drive MCP + Gmail MCP scripts)  
**Eval:** [docs/phases/phase-04-google-docs-mcp/eval.md](../../docs/phases/phase-04-google-docs-mcp/eval.md)  
**Plan:** [Implementation Plan — Phase 4](../../docs/implementationplan.md#phase-4--google-docs-via-drive-mcp)

## Objective

Publish the approved weekly pulse to a **new Google Doc** using **Drive MCP tools only**.

## Folders & artifacts

| Path | Purpose |
|------|---------|
| `scripts/run-phase4.py` | Publish pulse via Drive MCP (`create_file` + verify) |
| `scripts/prepare-publish.py` | Build `publish-manifest.json` |
| `scripts/validate-phase4.py` | Local Phase 4 checks |
| `runbook.md` | MCP tool sequence and troubleshooting |

## Planned deliverables

- Google Doc: `[Product] Weekly Pulse — YYYY-MM-DD`
- MCP-only publish runbook
- Content parity with local pulse verified
- Phase 4 eval signed off

## Prerequisites

- Phase 1: Drive MCP authenticated
- Phase 3: Approved `weekly-pulse-*.md`

## Previous / next

- **Previous:** [Phase 3](../phase-03-pulse-generation/README.md)
- **Next:** [Phase 5](../phase-05-gmail-orchestration/README.md)
