# Milestone 3 — AI Agent with MCP

Weekly **review pulse** agent: ingest App Store / Play Store exports → synthesize themes and actions → publish to **Google Docs** and **Gmail draft** via **Google Workspace MCP** (no direct Google APIs).

**Repository:** [github.com/alekhya2395/Milestone-3---AI-agent-MCP](https://github.com/alekhya2395/Milestone-3---AI-agent-MCP)

## Settings

Local setup from scratch (Windows / PowerShell):

```powershell
# 1. Clone
git clone https://github.com/alekhya2395/Milestone-3---AI-agent-MCP.git
cd Milestone-3---AI-agent-MCP

# 2. Virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment variables
copy .env.example .env
# Edit .env with your keys (Google OAuth, Alpha Vantage, etc.)

# 5. MCP setup (Cursor)
# Follow: phases/phase-01-mcp-setup/gcp-setup-checklist.md
# Then:  phases/phase-01-mcp-setup/runbook.md

# 6. Phase 2 — review ingestion
python phases/phase-02-review-ingestion/scripts/run-phase2.py --skip-fetch --weeks 10

# 7. Phase 3 — themes + weekly pulse (needs GROQ_API_KEY)
python phases/phase-03-pulse-generation/scripts/run-phase3.py
```

Step 5 details:

- [GCP setup checklist](phases/phase-01-mcp-setup/gcp-setup-checklist.md) — Google Cloud project, OAuth, APIs
- [MCP runbook](phases/phase-01-mcp-setup/runbook.md) — connect MCP servers in **Settings → Tools & MCP**
- [Railway MCP deployment](docs/deployment-railway.md) — custom `weekly-pulse` server

After step 7:

| Path | Content |
|------|---------|
| `data/processed/theme-summary.json` | Theme rankings |
| `data/processed/weekly-pulse-YYYY-MM-DD.md` | **Weekly pulse (main output)** |
| `data/processed/llm-input-bundle.json` | Groq input bundle |

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/problemstatement.md](docs/problemstatement.md) | Goals and constraints |
| [docs/architecture.md](docs/architecture.md) | System design |
| [docs/implementationplan.md](docs/implementationplan.md) | Phase-wise plan |
| [docs/eval.md](docs/eval.md) | Milestone evaluation tracker |
| [docs/decision.md](docs/decision.md) | Architecture decisions |
| [docs/deployment-railway.md](docs/deployment-railway.md) | Railway MCP server deploy |

## Project layout

```
├── .cursor/mcp.json          # weekly-pulse + Google MCP
├── src/                      # Railway MCP server (Phase 2–3 tools)
├── data/processed/           # theme-summary.json, weekly-pulse-*.md
├── phases/                   # Phase scripts
└── prompts/                  # Groq prompts (Phase 3)
```

## Current status: Phases 1–5 complete (functional)

**Product:** Groww | **Latest pulse:** `data/processed/weekly-pulse-2026-06-22.md`

| Deliverable | Link / location |
|-------------|-----------------|
| Google Doc | https://docs.google.com/document/d/1AwEeMAJA5KRT-y8cfcI2ndnw6JQXSyPItYFkUsRLyz4/edit |
| Gmail draft | Gmail → Drafts → `alekhya2395@gmail.com` |
| Railway MCP | https://milestone-3-ai-agent-mcp-production.up.railway.app/mcp |

### MCP setup (if Tools & MCP shows Error)

```powershell
# Quit Cursor first (File > Exit), then:
.\phases\phase-01-mcp-setup\scripts\reset-all-mcp.ps1
```

Then reopen Cursor and connect `google-drive` + `google-gmail`.

### Weekly run (manual or scheduled)

```powershell
# Full refresh + pulse + publish (local scheduler / manual)
python -m src.worker --weeks 10 --publish

# Or step-by-step
python phases/phase-05-gmail-orchestration/scripts/run-weekly.py --fetch
```

**Windows auto-schedule:** `.\phases\phase-05-gmail-orchestration\scripts\install-weekly-scheduler.ps1`

**Railway auto-schedule:** add a second service with `deploy/railway.cron.toml` (Mondays 06:00 UTC).

---

## Phase 1 — MCP & foundation (optional parallel)

1. Complete [GCP setup checklist](phases/phase-01-mcp-setup/gcp-setup-checklist.md)
2. Set env vars from [.env.example](.env.example)
3. Restart Cursor → **Settings → Tools & MCP** → Connect `google-drive` and `google-gmail`
4. Run smoke tests per [runbook](phases/phase-01-mcp-setup/runbook.md)
5. Sign off [Phase 1 eval](docs/phases/phase-01-mcp-setup/eval.md)

## MCP servers

| Server | URL | Purpose |
|--------|-----|---------|
| `weekly-pulse` | `https://milestone-3-ai-agent-mcp-production.up.railway.app/mcp` | Review ingestion + pulse (this repo) |
| `google-drive` | `https://drivemcp.googleapis.com/mcp/v1` | Google Docs (Phase 4) |
| `google-gmail` | `https://gmailmcp.googleapis.com/mcp/v1` | Gmail drafts (Phase 5) |

Configured in `.cursor/mcp.json`. Secrets via `.env`: `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`, `GROQ_API_KEY`.

## References

- [Configure Google Workspace MCP servers](https://developers.google.com/workspace/guides/configure-mcp-servers)
- [Cursor MCP docs](https://cursor.com/docs/mcp)
