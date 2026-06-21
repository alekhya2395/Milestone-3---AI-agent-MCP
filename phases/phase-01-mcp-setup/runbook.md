# Phase 1 Runbook — Cursor MCP Connect & Smoke Tests

## Prerequisites

- [gcp-setup-checklist.md](./gcp-setup-checklist.md) complete
- `.env` with `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET`
- Cursor restarted after env vars are set

---

## MCP configuration

| Item | Location |
|------|----------|
| Project MCP config | `.cursor/mcp.json` |
| Server: Drive | `google-drive` → `https://drivemcp.googleapis.com/mcp/v1` |
| Server: Gmail | `google-gmail` → `https://gmailmcp.googleapis.com/mcp/v1` |
| Global MCP (optional) | `%USERPROFILE%\.cursor\mcp.json` on Windows |

This project uses **project-scoped** config so the team can share server URLs without secrets.

---

## Step 1 — Verify config loads

1. Open **Cursor Settings** → **Tools & MCP** (or Features → Model Context Protocol).
2. Confirm servers appear: `google-drive`, `google-gmail`.
3. If missing: check `.cursor/mcp.json` syntax and restart Cursor.
4. If env errors: ensure `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` are set (system env or shell that launches Cursor).

**Debug:** Output panel → **MCP Logs** (`Ctrl+Shift+U`).

---

## Step 2 — Authenticate (OAuth)

For each server (`google-drive`, `google-gmail`):

1. Click **Connect** (or **Authenticate**).
2. Complete Google sign-in in the browser.
3. Grant requested scopes.
4. Confirm server shows as connected / authenticated in Tools & MCP.

- [ ] `google-drive` authenticated
- [ ] `google-gmail` authenticated

---

## Step 3 — Tool discovery (`tools/list`)

In Cursor chat (Agent mode), ask:

> List all available tools from the `google-drive` and `google-gmail` MCP servers.

Record results in [tool-inventory.md](./tool-inventory.md). Mark **Verified** when they match expectations.

**Expected Drive tools (minimum for later phases):**

- `create_file`
- `read_file_content`
- `search_files` or `list_recent_files`

**Expected Gmail tools (minimum):**

- `create_draft`
- `list_drafts` or `list_labels`

---

## Step 4 — Read-only smoke tests

Run in Cursor chat with MCP tools enabled.

### Drive (T1.7)

> Using google-drive MCP, list my recent files (or search for any file). Show a brief summary.

**Pass:** Response without 401/403; file metadata returned.

### Gmail (T1.8)

> Using google-gmail MCP, list my Gmail labels (or list drafts). Show a brief summary.

**Pass:** Response without 401/403; labels or drafts returned.

| Test | Date | Pass / Fail | Notes |
|------|------|-------------|-------|
| Drive smoke | | | |
| Gmail smoke | | | |

---

## Step 5 — Capture evidence

Save to `phases/phase-01-mcp-setup/evidence/` (gitignored):

- Redacted screenshot of Tools & MCP showing both servers connected
- Tool list summary (paste into `tool-inventory.md`)
- Smoke test date

---

## Troubleshooting

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| 403 Gmail/Drive | Workspace admin trust | See GCP checklist §6; log in `decision.md` |
| Connect button missing | Invalid `mcp.json` | Validate JSON; restart Cursor |
| Env not picked up | Cursor started before `.env` | Set system user env vars; restart Cursor |
| Tool not found | API not enabled | Re-run `enable-gcp-apis.ps1` |
| OAuth redirect error | Wrong redirect URI | Must be `cursor://anysphere.cursor-mcp/oauth/callback` |

---

## Phase 1 complete when

All items in [eval.md](../../docs/phases/phase-01-mcp-setup/eval.md) pass → proceed to [Phase 2](../phase-02-review-ingestion/README.md).
