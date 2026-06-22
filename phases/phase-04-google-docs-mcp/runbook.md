# Phase 4 Runbook — Google Docs via Drive MCP

Per [implementation plan](../../docs/implementationplan.md#phase-4--google-docs-via-drive-mcp): publish using **Drive MCP only** — no Docs/Drive REST SDK in the main path.

**MCP endpoints (Phase 1):**

| Server | URL |
|--------|-----|
| weekly-pulse (Railway) | https://milestone-3-ai-agent-mcp-production.up.railway.app/mcp |
| google-drive | https://drivemcp.googleapis.com/mcp/v1 |
| google-gmail | https://gmailmcp.googleapis.com/mcp/v1 |

Configure in `.cursor/mcp.json` (already set for Drive + Gmail).

---

## Prerequisites

1. Phase 3 complete — `data/processed/weekly-pulse-*.md`
2. `.env` — `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`
3. Optional: `GOOGLE_DRIVE_FOLDER_ID` (where new Docs are created)
4. Cursor **Settings → Tools & MCP** → `google-drive` connected (green)

---

## Automated publish (recommended)

```powershell
# From project root
python phases/phase-04-google-docs-mcp/scripts/prepare-publish.py
python phases/phase-04-google-docs-mcp/scripts/run-phase4.py
```

**First run:** browser opens for Google OAuth. Token saved to `token.json` (gitignored).

**What it does:**

1. Calls Drive MCP `create_file` — title `{Product} Weekly Pulse — YYYY-MM-DD` (DEC-008)
2. Calls `read_file_content` — verifies parity with local pulse
3. Writes `data/processed/publish-result.json` with Doc URL

---

## Verify existing Doc (optional)

If `GOOGLE_DOC_ID` is set:

```powershell
python phases/phase-04-google-docs-mcp/scripts/run-phase4.py --verify-only
```

---

## Phase 3 + 4 in one command

```powershell
python phases/phase-03-pulse-generation/scripts/run-phase3.py --publish-doc
```

---

## Cursor chat (manual MCP)

```
Using google-drive MCP only:
1. Read data/processed/weekly-pulse-2026-06-21.md
2. create_file with title "Groww Weekly Pulse — 2026-06-21", textContent = full markdown, contentMimeType text/plain
3. read_file_content on the new file id to verify
4. Report Doc URL
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| MCP Unauthorized | Connect `google-drive` in Cursor MCP settings; re-run OAuth (delete `token.json` if scopes changed) |
| Empty Doc body | Ensure `textContent` + `contentMimeType: text/plain` |
| Wrong account | Sign in with the Google account that owns Drive |
| Legacy Docs API script | `publish-pulse-to-doc.py` is deprecated — use `run-phase4.py` |

---

## Handoff to Phase 5

After Phase 4, run Phase 5 to create a Gmail draft with the Doc link:

```powershell
python phases/phase-05-gmail-orchestration/scripts/run-phase5.py
```

Set `GMAIL_DRAFT_TO=your@email.com` in `.env` first.
