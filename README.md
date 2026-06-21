# Milestone 3 — AI Agent with MCP

Weekly **review pulse** agent: ingest App Store / Play Store exports → synthesize themes and actions → publish to **Google Docs** and **Gmail draft** via **Google Workspace MCP** (no direct Google APIs).

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/problemstatement.md](docs/problemstatement.md) | Goals and constraints |
| [docs/architecture.md](docs/architecture.md) | System design |
| [docs/implementationplan.md](docs/implementationplan.md) | Phase-wise plan |
| [docs/eval.md](docs/eval.md) | Milestone evaluation tracker |
| [docs/decision.md](docs/decision.md) | Architecture decisions |

## Project layout

```
├── .cursor/mcp.json          # Drive + Gmail MCP (secrets via env vars)
├── data/raw/                 # Store review exports
├── data/processed/           # Normalized reviews & pulse artifacts
├── docs/                     # Specs and per-phase eval.md
├── phases/                   # Phase work folders (runbooks, artifacts)
└── prompts/                  # Agent prompts (Phase 3+)
```

## Current phase: 1 — MCP & foundation

1. Complete [GCP setup checklist](phases/phase-01-mcp-setup/gcp-setup-checklist.md)
2. Set env vars from [.env.example](.env.example)
3. Restart Cursor → **Settings → Tools & MCP** → Connect `google-drive` and `google-gmail`
4. Run smoke tests per [runbook](phases/phase-01-mcp-setup/runbook.md)
5. Sign off [Phase 1 eval](docs/phases/phase-01-mcp-setup/eval.md)

## MCP config location

- **Project:** `.cursor/mcp.json` (committed, no secrets)
- **Credentials:** `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in `.env` or system environment

## References

- [Configure Google Workspace MCP servers](https://developers.google.com/workspace/guides/configure-mcp-servers)
- [Cursor MCP docs](https://cursor.com/docs/mcp)
