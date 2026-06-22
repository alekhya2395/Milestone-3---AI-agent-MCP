"""OAuth token for Google Workspace MCP (Drive + Gmail). No Docs/Drive REST SDK."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]

# Official Google Workspace MCP scopes (see Google Drive/Gmail MCP configure guides)
MCP_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]

OAUTH_PORTS = (8091, 8092, 8765, 8081, 8090)


def oauth_client_config() -> dict:
    load_dotenv(ROOT / ".env")
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
    if client_id and client_secret:
        return {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [f"http://localhost:{p}/" for p in OAUTH_PORTS],
            }
        }

    creds_file = ROOT / "credentials.json"
    if creds_file.is_file():
        return json.loads(creds_file.read_text(encoding="utf-8"))

    raise SystemExit(
        "ERROR: Set GOOGLE_OAUTH_CLIENT_ID/SECRET in .env or add credentials.json"
    )


def _run_local_oauth(flow) -> object:
    print("\n>>> Browser opening for Google sign-in...", flush=True)
    print(">>> Use the account connected to Drive MCP / Gmail MCP.\n", flush=True)
    last_err: OSError | None = None
    for port in OAUTH_PORTS:
        try:
            return flow.run_local_server(
                port=port,
                open_browser=True,
                prompt="consent",
                authorization_prompt_message="Sign in for Google Workspace MCP (Drive + Gmail).",
            )
        except OSError as exc:
            last_err = exc
            print(f"Port {port} busy, trying next...", flush=True)
    raise OSError(f"Could not bind OAuth port. Tried {OAUTH_PORTS}") from last_err


def get_access_token() -> str:
    """Return a valid OAuth access token for Workspace MCP calls."""
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    token_file = ROOT / "token.json"
    config = oauth_client_config()

    creds = None
    if token_file.is_file():
        creds = Credentials.from_authorized_user_file(str(token_file), MCP_SCOPES)
        missing = [s for s in MCP_SCOPES if s not in (creds.scopes or [])]
        if missing:
            print(f"Token missing scopes {missing}; re-authenticating...", flush=True)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif "installed" in config:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(ROOT / "credentials.json"), MCP_SCOPES
            )
            creds = _run_local_oauth(flow)
        else:
            web = config.get("web", config)
            installed_config = {
                "installed": {
                    "client_id": web["client_id"],
                    "client_secret": web["client_secret"],
                    "auth_uri": web.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
                    "token_uri": web.get("token_uri", "https://oauth2.googleapis.com/token"),
                    "redirect_uris": [f"http://localhost:{p}/" for p in OAUTH_PORTS],
                }
            }
            flow = InstalledAppFlow.from_client_config(installed_config, MCP_SCOPES)
            creds = _run_local_oauth(flow)
        token_file.write_text(creds.to_json(), encoding="utf-8")
        print(f"Saved token -> {token_file.name}", flush=True)

    if not creds.token:
        raise SystemExit("ERROR: OAuth token missing after sign-in.")
    return creds.token
