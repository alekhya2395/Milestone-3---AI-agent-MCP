# Railway Deployment — Weekly Pulse MCP

Deploy the **custom MCP server** to [Railway](https://railway.app). Google Gmail/Drive MCP stay on Google's servers.

**Live server:** [https://milestone-3-ai-agent-mcp-production.up.railway.app/](https://milestone-3-ai-agent-mcp-production.up.railway.app/)

**Repository:** [github.com/alekhya2395/Milestone-3---AI-agent-MCP](https://github.com/alekhya2395/Milestone-3---AI-agent-MCP)

---

## MCP tools

### Phase 2 — Review ingestion

| Tool | Description |
|------|-------------|
| `fetch_reviews` | Download App Store + Play Store reviews |
| `normalize_reviews` | Clean, filter, de-PII; build `reviews-for-llm.json` |
| `review_stats` | JSON summary of normalized reviews |

### Phase 3 — Pulse generation (Groq)

| Tool | Description |
|------|-------------|
| `build_llm_bundle` | Stats on 1,000 + ~120 Groq sample |
| `generate_pulse` | 2 Groq calls → `theme-summary.json` + `weekly-pulse-*.md` |
| `run_phase3_pipeline` | Full Phase 3 with validation |
| `theme_summary` | Return theme rankings JSON |
| `llm_bundle` | Return LLM input bundle JSON |
| `latest_pulse` | Return latest weekly pulse markdown |

### Scheduler (Phase 5)

| Tool | Description |
|------|-------------|
| `run_weekly_job` | Fetch → normalize → pulse (+ optional publish) |
| `scheduler_status` | Last cron/MCP run from `scheduler-last-run.json` |

---

## Railway environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `REVIEW_WEEKS` | Optional | Review window for cron (default `10`) |
| `GROQ_API_KEY` | **Yes for Phase 3** | Groq API for theme + pulse |
| `DATA_DIR` | Yes | `/app/data` (use Volume) |
| `GOOGLE_OAUTH_CLIENT_ID` | Cursor only | Google MCP in IDE |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Cursor only | Google MCP in IDE |
| `MCP_SERVER_API_KEY` | Optional | Protect MCP endpoint |

---

## Cursor MCP config

`.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "weekly-pulse": {
      "url": "https://milestone-3-ai-agent-mcp-production.up.railway.app/mcp"
    }
  }
}
```

Restart Cursor after updating.

---

## Deploy updates

```bash
git push origin main
# Railway auto-deploys from GitHub
```

Or: `railway up`

**Important:** After pushing Phase 3 code, redeploy Railway so `generate_pulse` tools are available.

---

## Weekly workflow

### Automated scheduler (keeps reviews up to date)

| Platform | Config | Schedule | Command |
|----------|--------|----------|---------|
| **Local Windows** | `install-weekly-scheduler.ps1` | Every Monday 09:00 | `python -m src.worker --publish` |
| **Railway cron** | `deploy/railway.cron.toml` | Mondays 06:00 UTC | `python -m src.worker` |
| **MCP (Cursor)** | `run_weekly_job` tool | On demand | fetch + pulse via Railway MCP |

Worker logs last run to `data/processed/scheduler-last-run.json`.

### Railway cron service setup

1. In your Railway project, **New Service** → same GitHub repo.
2. **Settings → Deploy → Config file path:** `deploy/railway.cron.toml`
3. Attach a **Volume** mounted at `/app/data` (same as main MCP service).
4. Set `GROQ_API_KEY` on the cron service.
5. Cron runs `python -m src.worker` (fetch + pulse only; publish stays local or via MCP with `publish=true`).

### Manual weekly run

| Step | Where | Action |
|------|-------|--------|
| 1 | Worker / MCP | `python -m src.worker` or `run_weekly_job` |
| 2 | Operator | Approve `data/processed/weekly-pulse-*.md` |
| 3 | Worker `--publish` or Phase 4/5 | Google Doc + Gmail draft |

---

## Related

- [Phase 3 README](../phases/phase-03-pulse-generation/README.md)
- [Architecture](./architecture.md)
- [Implementation plan](./implementationplan.md)
