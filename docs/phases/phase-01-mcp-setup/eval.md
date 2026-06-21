# Phase 1 Evaluation — MCP & Project Foundation

**Phase:** [Implementation Plan — Phase 1](../../implementationplan.md#phase-1--mcp--project-foundation)  
**Work folder:** [phases/phase-01-mcp-setup](../../../phases/phase-01-mcp-setup/)

---

## Objectives Under Test

- Google Cloud project has Drive MCP and Gmail MCP enabled
- OAuth 2.0 configured for MCP client
- MCP client discovers and can invoke tools on both servers
- Repo structure and secrets hygiene in place

---

## Test Cases

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| T1.1 | GCP APIs enabled | In Cloud Console, verify Drive MCP, Gmail MCP, and underlying Drive + Gmail APIs are enabled | All services show **Enabled** |
| T1.2 | OAuth client configured | Confirm OAuth client ID, redirect URIs, and consent screen | Client usable by MCP client without config errors |
| T1.3 | Drive MCP connection | In MCP client, connect to `https://drivemcp.googleapis.com/mcp/v1` | Connection succeeds after OAuth |
| T1.4 | Gmail MCP connection | Connect to `https://gmailmcp.googleapis.com/mcp/v1` | Connection succeeds after OAuth |
| T1.5 | Tool discovery — Drive | Run `tools/list` or equivalent via client | Tools include `create_file`, `read_file_content` (or documented equivalents) |
| T1.6 | Tool discovery — Gmail | Run `tools/list` for Gmail MCP | Tools include `create_draft` (or documented equivalent) |
| T1.7 | Drive smoke test | Call a read-only Drive tool (e.g. `list_recent_files` or `search_files`) | Returns data without 403/401 |
| T1.8 | Gmail smoke test | Call a read-only Gmail tool (e.g. `list_drafts` or `list_labels`) | Returns data without 403/401 |
| T1.9 | Secrets hygiene | Inspect repo for committed credentials | No `.env`, tokens, or client secrets in git; `.env.example` present |
| T1.10 | Repo layout | Check folders exist per architecture doc | `docs/`, planned `data/`, `prompts/` or documented equivalent |

---

## Manual Verification Checklist

- [ ] Completed OAuth flow end-to-end in MCP client
- [ ] Screenshot or log of successful `tools/list` for Drive MCP
- [ ] Screenshot or log of successful `tools/list` for Gmail MCP
- [x] Documented MCP server config location in [runbook](../../../phases/phase-01-mcp-setup/runbook.md) and [README](../../../README.md)
- [ ] Recorded any Workspace admin steps required (if 403 encountered) in `decision.md`

---

## Exit Criteria

All of the following must be true before starting **Phase 2**:

1. **Both** Google Workspace MCP servers authenticate successfully from the MCP client.
2. Drive and Gmail tool lists are documented (names + brief purpose).
3. At least one **read-only** tool call succeeds on each server.
4. No secrets committed to the repository.
5. Phase 1 checklist above is **100% passed** or failures have documented workarounds with target fix date.

---

## Evidence to Capture

- MCP config snippet (redacted)
- Tool list export or notes
- Date of successful smoke tests

---

## Sign-off

| Role | Name | Date | Pass / Fail |
|------|------|------|-------------|
| Implementer | | | |
| Reviewer | | | |
