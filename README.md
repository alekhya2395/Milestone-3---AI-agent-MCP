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

# 6. Download reviews (Phase 2)
python phases/phase-02-review-ingestion/scripts/fetch-reviews.py --weeks 10
python phases/phase-02-review-ingestion/scripts/normalize-reviews.py
```

Step 5 details:

- [GCP setup checklist](phases/phase-01-mcp-setup/gcp-setup-checklist.md) — Google Cloud project, OAuth, APIs
- [MCP runbook](phases/phase-01-mcp-setup/runbook.md) — connect `google-drive` and `google-gmail` in **Settings → Tools & MCP**

After step 6, review outputs are in `data/raw/` (CSV) and `data/reviews/reviews.json` (filtered JSON).

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
