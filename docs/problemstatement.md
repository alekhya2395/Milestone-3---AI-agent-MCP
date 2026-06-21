# Problem Statement — Milestone 3: AI Agent with MCP

## Context

This milestone builds on the **same product you selected in Milestone 1**. You will create an **AI agent** that turns recent App Store and Play Store reviews into a scannable weekly pulse, stores the note in **Google Docs**, and drafts a **Gmail** message to yourself — all by calling **MCP (Model Context Protocol) servers**, not by integrating Google APIs directly in application code.

The agent should reason over review data, synthesize themes and actions, then use MCP tools to create the document and email draft. Authentication, transport, and Google-side operations are handled through the configured MCP servers and your MCP client (e.g. Cursor).

---

## Goal

Turn reviews from the last **8–12 weeks** into a **one-page weekly pulse** containing:

- **Top themes** (max 5)
- **Real user quotes** (anonymized)
- **Three action ideas**

Then:

1. **Save** the weekly note as a Google Doc (via MCP)
2. **Draft** an email containing the note and send it to yourself or an alias (via MCP)

---

## Who This Helps

| Audience | Benefit |
|----------|---------|
| **Product / Growth Teams** | Understand what to fix next |
| **Support Teams** | Know what users are saying and acknowledge recurring issues |
| **Leadership** | Quick weekly health pulse without reading hundreds of reviews |

---

## What You Must Build

### 1. Review ingestion & analysis

- Import reviews from the last **8–12 weeks** (rating, title, text, date)
- Use **public review exports only** — no scraping behind logins
- Group reviews into **5 themes max** (e.g. onboarding, KYC, payments, statements, withdrawals)
- Generate a weekly one-page note with:
  - Top **3 themes**
  - **3 user quotes**
  - **3 action ideas**
- Keep the note scannable, **≤ 250 words**
- **Do not include PII** (no usernames, emails, or IDs in any artifact)

### 2. Google Docs integration (via MCP — not direct API)

Use the **Google Workspace MCP server for Google Drive** to create and manage the weekly note as a Google Doc. The agent must invoke MCP tools (e.g. create file, read/write content) exposed by the server — **do not** call the Google Drive or Docs REST APIs from your own code.

- **MCP server:** Google Drive MCP (`https://drivemcp.googleapis.com/mcp/v1`)
- **Typical tools:** `create_file`, `read_file_content`, `search_files`, etc.
- **Output:** A Google Doc containing the formatted weekly pulse

### 3. Gmail integration (via MCP — not direct API)

Use the **Google Workspace MCP server for Gmail** to create a draft email with the weekly note. The agent must use MCP tools (e.g. `create_draft`, `search_threads`) — **do not** call the Gmail REST API from your own code.

- **MCP server:** Gmail MCP (`https://gmailmcp.googleapis.com/mcp/v1`)
- **Typical tools:** `create_draft`, `list_drafts`, `search_threads`, etc.
- **Output:** A draft email to yourself (or alias) with the weekly pulse in the body

### 4. AI agent orchestration

- Configure your MCP client with the required Google Workspace MCP servers and OAuth 2.0
- The agent should: analyze reviews → generate the pulse → call Drive MCP to save the Doc → call Gmail MCP to create the draft
- Tool discovery and invocation follow the MCP spec (`tools/list`, tool calls with structured arguments)

---

## MCP Setup (Reference)

Enable the relevant services in your Google Cloud project and connect them in your MCP client. See [Configure the Google Workspace MCP servers](https://developers.google.com/workspace/guides/configure-mcp-servers).

| Integration | MCP endpoint | Underlying capability |
|-------------|--------------|------------------------|
| Google Docs (via Drive) | `https://drivemcp.googleapis.com/mcp/v1` | Create/update document content |
| Gmail | `https://gmailmcp.googleapis.com/mcp/v1` | Create draft emails |

Both servers use **OAuth 2.0**; credentials and scopes are configured at the MCP client level, not hard-coded in the agent’s business logic.

---

## Key Constraints

- **MCP only for Google:** Use Google Workspace MCP servers for Docs and Gmail — no direct Google API SDKs or REST calls in your agent code
- **Public data only:** Public review exports — no scraping behind logins
- **Max 5 themes** when clustering; surface **top 3** in the final note
- **≤ 250 words** for the weekly note
- **No PII** in the Doc, email, or any intermediate output
- **Scannable format:** bullets, short sections, clear headings

---

## Success Criteria

- [ ] Reviews from 8–12 weeks are imported and themed correctly
- [ ] Weekly pulse includes top 3 themes, 3 quotes, and 3 action ideas
- [ ] Google Doc is created/updated via **Drive MCP** tools
- [ ] Gmail draft is created via **Gmail MCP** tools (to self or alias)
- [ ] No PII appears in any deliverable
- [ ] Agent uses MCP tool calls end-to-end for Google integrations (no parallel API integration path)
