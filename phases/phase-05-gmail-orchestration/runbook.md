# Phase 5 Runbook — Gmail Draft & E2E

Per [implementation plan](../../docs/implementationplan.md#phase-5--gmail-draft--end-to-end-orchestration).

---

## Prerequisites

1. Phases 3 and 4 complete
2. `.env` — `GMAIL_DRAFT_TO=you@example.com` (plain email, no display name)
3. Cursor **Settings → Tools & MCP** → `google-gmail` connected

---

## Create Gmail draft

```powershell
python phases/phase-05-gmail-orchestration/scripts/create-gmail-draft.py
```

Or:

```powershell
python phases/phase-05-gmail-orchestration/scripts/run-phase5.py
```

**Output:** draft in Gmail → Drafts folder; `data/processed/gmail-draft-result.json`

**Subject:** `Weekly Pulse — Groww — YYYY-MM-DD`  
**Body:** full pulse markdown + Google Doc link (from Phase 4 `publish-result.json`)

Operator sends manually from Gmail UI (DEC-009).

---

## Full weekly run (E2E)

```powershell
# Recommended — single command with fresh reviews + publish
python -m src.worker --weeks 10 --publish

# Or phased scripts
python phases/phase-05-gmail-orchestration/scripts/run-weekly.py
```

## Automated scheduler

**Windows (every Monday 9 AM):**

```powershell
.\phases\phase-05-gmail-orchestration\scripts\install-weekly-scheduler.ps1
```

**Railway (Mondays 06:00 UTC):** add a second service with config `deploy/railway.cron.toml`.

**MCP:** call `run_weekly_job` on the `weekly-pulse` server; check `scheduler_status` for last run.

Log file: `data/processed/scheduler-last-run.json`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| GMAIL_DRAFT_TO missing | Add to `.env` |
| MCP Unauthorized | Connect `google-gmail` in Cursor; re-run OAuth |
| Wrong recipient | Check `.env`; verify draft in Gmail UI before send |

---

## MCP servers

| Server | URL |
|--------|-----|
| weekly-pulse | https://milestone-3-ai-agent-mcp-production.up.railway.app/mcp |
| google-gmail | https://gmailmcp.googleapis.com/mcp/v1 |
