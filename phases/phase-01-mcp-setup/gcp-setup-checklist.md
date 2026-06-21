# GCP Setup Checklist — Phase 1

Complete before connecting MCP servers in Cursor.  
Reference: [Google Workspace MCP configuration](https://developers.google.com/workspace/guides/configure-mcp-servers)

---

## 1. Google Cloud project

- [ ] Create or select a GCP project
- [ ] Note project ID → set `GOOGLE_CLOUD_PROJECT_ID` in `.env` (optional, for your records)

---

## 2. Enable Workspace APIs

Enable in [Google Cloud Console → APIs & Services](https://console.cloud.google.com/apis/library) or run:

```powershell
.\phases\phase-01-mcp-setup\scripts\enable-gcp-apis.ps1 -ProjectId YOUR_PROJECT_ID
```

| API | Service name |
|-----|----------------|
| Gmail API | `gmail.googleapis.com` |
| Google Drive API | `drive.googleapis.com` |

- [ ] Gmail API enabled
- [ ] Google Drive API enabled

---

## 3. Enable MCP services

| MCP API | Service name |
|---------|----------------|
| Gmail MCP API | `gmailmcp.googleapis.com` |
| Google Drive MCP API | `drivemcp.googleapis.com` |

- [ ] Gmail MCP API enabled
- [ ] Drive MCP API enabled

---

## 4. OAuth consent screen

Google Auth Platform → **Branding** / **Audience** / **Data Access**

- [ ] App name set (e.g. `Workspace MCP — Weekly Pulse`)
- [ ] User support email configured
- [ ] Test users added (if app is **External** and in testing)

### Scopes (Data Access → Add scopes)

**Gmail**

- `https://www.googleapis.com/auth/gmail.readonly`
- `https://www.googleapis.com/auth/gmail.compose`

**Google Drive**

- `https://www.googleapis.com/auth/drive.readonly`
- `https://www.googleapis.com/auth/drive.file`

- [ ] All scopes added and saved

---

## 5. OAuth client (Web application)

Google Auth Platform → **Clients** → **Create client** → **Web application**

| Field | Value |
|-------|--------|
| Name | `Cursor MCP — Weekly Pulse` |
| Authorized redirect URI | `cursor://anysphere.cursor-mcp/oauth/callback` |

> Cursor uses this fixed redirect for all MCP OAuth. [Cursor MCP docs](https://cursor.com/docs/mcp#static-redirect-url)

- [ ] OAuth client created
- [ ] Client ID copied → `GOOGLE_OAUTH_CLIENT_ID` in `.env`
- [ ] Client secret copied → `GOOGLE_OAUTH_CLIENT_SECRET` in `.env`
- [ ] Redirect URI registered

---

## 6. Workspace admin (if Gmail returns 403)

For Google Workspace accounts, a super admin may need to **trust** the OAuth app for restricted Gmail/Drive scopes.

- [ ] No 403 on Gmail MCP smoke test, **or**
- [ ] Admin trust steps documented in [docs/decision.md](../../docs/decision.md)

---

## 7. Local environment

- [ ] Copy `.env.example` → `.env` (never commit `.env`)
- [ ] Restart Cursor after setting environment variables
- [ ] Confirm `.cursor/mcp.json` present in project root

---

## Sign-off

| Step | Done | Date |
|------|------|------|
| APIs enabled | | |
| OAuth configured | | |
| `.env` populated | | |
