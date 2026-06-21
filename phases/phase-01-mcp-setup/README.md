# Phase 1 — MCP & Project Foundation

**Status:** In progress  
**Eval:** [docs/phases/phase-01-mcp-setup/eval.md](../../docs/phases/phase-01-mcp-setup/eval.md)  
**Plan:** [Implementation Plan — Phase 1](../../docs/implementationplan.md#phase-1--mcp--project-foundation)

## Objective

Prove Google **Drive MCP** and **Gmail MCP** connectivity from Cursor before building review analysis or publish workflows.

## Contents

| File / folder | Purpose |
|---------------|---------|
| [gcp-setup-checklist.md](./gcp-setup-checklist.md) | Google Cloud + OAuth setup steps |
| [runbook.md](./runbook.md) | Cursor MCP connect + smoke tests |
| [tool-inventory.md](./tool-inventory.md) | Drive/Gmail MCP tools (verify via `tools/list`) |
| [scripts/enable-gcp-apis.ps1](./scripts/enable-gcp-apis.ps1) | Enable required APIs (Windows) |
| `evidence/` | Screenshots/logs for eval (gitignored) |

## Exit criteria (summary)

- [ ] GCP APIs and MCP services enabled
- [ ] OAuth client with Cursor redirect URI
- [ ] `google-drive` and `google-gmail` connected in Cursor
- [ ] Read-only smoke test on each server
- [ ] Tool inventory confirmed
- [ ] Phase 1 eval signed off

## Next phase

[Phase 2 — Review ingestion](../phase-02-review-ingestion/README.md) (can start data prep in parallel once repo is ready).
