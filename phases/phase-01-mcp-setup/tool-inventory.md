# MCP Tool Inventory — Phase 1

Document tools discovered via `tools/list` after OAuth.  
Source reference: [Google Workspace MCP supported products](https://developers.google.com/workspace/guides/configure-mcp-servers#supported-products)

**Verification date:** _fill after smoke tests_  
**Verified by:** _

---

## Google Drive MCP (`google-drive`)

Endpoint: `https://drivemcp.googleapis.com/mcp/v1`

| Tool | Purpose | Needed this milestone | Verified |
|------|---------|----------------------|----------|
| `copy_file` | Duplicate a file | No | ⬜ |
| `create_file` | Create Doc/file with content | **Yes — Phase 4** | ⬜ |
| `download_file_content` | Download file bytes | No | ⬜ |
| `get_file_metadata` | File name, id, mime | **Yes — Phase 4** | ⬜ |
| `get_file_permissions` | Sharing info | No | ⬜ |
| `list_recent_files` | Recent files listing | **Yes — Phase 1 smoke** | ⬜ |
| `read_file_content` | Read Doc/file text | **Yes — Phase 4** | ⬜ |
| `search_files` | Find by query | **Yes — Phase 1 smoke** | ⬜ |

### Phase 1 smoke tool used

- Tool name: _______________
- Result: Pass / Fail
- Notes:

---

## Gmail MCP (`google-gmail`)

Endpoint: `https://gmailmcp.googleapis.com/mcp/v1`

| Tool | Purpose | Needed this milestone | Verified |
|------|---------|----------------------|----------|
| `create_draft` | Create email draft | **Yes — Phase 5** | ⬜ |
| `create_label` | New label | No | ⬜ |
| `get_thread` | Read thread | No | ⬜ |
| `label_message` | Label a message | No | ⬜ |
| `label_thread` | Label thread | No | ⬜ |
| `list_drafts` | List drafts | **Yes — Phase 1 smoke** | ⬜ |
| `list_labels` | List labels | **Yes — Phase 1 smoke** | ⬜ |
| `search_threads` | Search mail | No | ⬜ |
| `unlabel_message` | Remove label | No | ⬜ |
| `unlabel_thread` | Remove thread label | No | ⬜ |

### Phase 1 smoke tool used

- Tool name: _______________
- Result: Pass / Fail
- Notes:

---

## Discrepancies

If Cursor `tools/list` differs from this table, record here and update Phases 4–5 runbooks.

| Server | Documented tool | Actual tool name | Resolution |
|--------|-----------------|------------------|------------|
| | | | |
