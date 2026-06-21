# Phase 4 Evaluation — Google Docs via Drive MCP

**Phase:** [Implementation Plan — Phase 4](../implementationplan.md#phase-4--google-docs-via-drive-mcp)

---

## Objectives Under Test

- Weekly pulse published to Google Docs using **Drive MCP tools only**
- Doc title and content match local pulse artifact
- No direct Google Drive/Docs API usage in codebase

---

## Test Cases

| ID | Test | Steps | Expected result |
|----|------|-------|-----------------|
| T4.1 | MCP-only creation | Agent calls Drive MCP `create_file` (or equivalent) | Google Doc created; no REST/SDK calls in `src/` |
| T4.2 | Title convention | Inspect Doc title in Drive | Matches pattern e.g. `[Product] Weekly Pulse — YYYY-MM-DD` |
| T4.3 | Content parity | Compare Doc body to local `weekly-pulse-*.md` | Same themes, quotes, and actions (minor formatting diff OK) |
| T4.4 | Read-back verify | Call `read_file_content` or `get_file_metadata` via MCP | Confirms file ID and readable content |
| T4.5 | Auth failure handling | Simulate expired token (if safe) | Agent or runbook documents re-auth steps; no silent failure |
| T4.6 | Duplicate run | Create pulse Doc twice same day | Behavior documented (new file vs update); no unintended overwrite unless chosen |
| T4.7 | Code audit | `grep` repo for `googleapis`, Drive SDK, Docs API | No matches in application code (MCP config excluded) |
| T4.8 | Formatting | Open Doc in Google Docs UI | Headings/lists readable; not a single unbroken paragraph |

---

## Manual Verification Checklist

- [ ] Doc URL opens in browser for reviewer
- [ ] Doc owned by correct Google account
- [ ] Sharing settings appropriate (private or team — document in `decision.md`)
- [ ] MCP tool call sequence documented in runbook

---

## Exit Criteria

1. At least **one** Google Doc created exclusively via Drive MCP.
2. Content parity with Phase 3 artifact confirmed.
3. Code audit (T4.7) passes.
4. Doc title convention and duplicate policy recorded in `decision.md` (resolves OQ-003 if applicable).
5. Phase 4 checklist **100% passed**.

---

## Evidence to Capture

- Doc link (share internally only; do not commit if policy forbids)
- MCP tool invocation log or transcript (redacted)
- Screenshot of Doc in Google Docs UI

---

## Sign-off

| Role | Name | Date | Pass / Fail |
|------|------|------|-------------|
| Implementer | | | |
| Reviewer | | | |
