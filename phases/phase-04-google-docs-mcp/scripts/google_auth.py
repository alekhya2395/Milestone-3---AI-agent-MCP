"""OAuth helpers for Phase 4 Google Docs publish."""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]

SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive",
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
    from google_auth_oauthlib.flow import InstalledAppFlow

    print("\n>>> Browser opening for Google sign-in...", flush=True)
    print(">>> Use the account that OWNS the Google Doc.", flush=True)
    print(">>> If blocked, add http://localhost:8091/ to GCP OAuth redirect URIs.\n", flush=True)
    last_err: OSError | None = None
    for port in OAUTH_PORTS:
        try:
            return flow.run_local_server(
                port=port,
                open_browser=True,
                prompt="consent",
                authorization_prompt_message="Sign in to publish the weekly pulse to Google Docs.",
            )
        except OSError as exc:
            last_err = exc
            print(f"Port {port} busy, trying next...", flush=True)
    raise OSError(f"Could not bind OAuth port. Tried {OAUTH_PORTS}") from last_err


def get_credentials():
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    token_file = ROOT / "token.json"
    config = oauth_client_config()

    creds = None
    if token_file.is_file():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        missing = [s for s in SCOPES if s not in (creds.scopes or [])]
        if missing:
            print(f"Token missing scopes {missing}; re-authenticating...", flush=True)
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif "installed" in config:
            creds_file = ROOT / "credentials.json"
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
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
            flow = InstalledAppFlow.from_client_config(installed_config, SCOPES)
            creds = _run_local_oauth(flow)
        token_file.write_text(creds.to_json(), encoding="utf-8")
        print(f"Saved token -> {token_file.name}", flush=True)

    return creds
