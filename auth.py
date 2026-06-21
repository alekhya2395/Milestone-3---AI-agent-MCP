"""Google OAuth helpers — load credentials.json and obtain user tokens."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

ROOT = Path(__file__).resolve().parent
CREDENTIALS_FILE = ROOT / "credentials.json"
TOKEN_FILE = ROOT / "token.json"
ENV_FILE = ROOT / ".env"

DEFAULT_LOGIN_EMAIL = "dhulipudialekhya@gmail.com"
OAUTH_PORTS = (8080, 8081, 8090, 8765)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


def load_env_value(key: str, default: str = "") -> str:
    if os.environ.get(key):
        return os.environ[key]
    if ENV_FILE.is_file():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith(f"{key}="):
                return line.split("=", 1)[1].strip()
    return default


def validate_credentials_file() -> list[str]:
    problems: list[str] = []

    if not CREDENTIALS_FILE.is_file():
        problems.append(f"Missing {CREDENTIALS_FILE.name} in project root.")
        return problems

    try:
        data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        problems.append(f"{CREDENTIALS_FILE.name} is not valid JSON.")
        return problems

    if "installed" not in data and "web" not in data:
        problems.append(
            f"{CREDENTIALS_FILE.name} must be a Desktop ('installed') or Web ('web') OAuth client."
        )
        return problems

    block = data.get("installed") or data.get("web", {})
    if not block.get("client_id") or not block.get("client_secret"):
        problems.append(f"{CREDENTIALS_FILE.name} is missing client_id or client_secret.")

    if "installed" not in data:
        problems.append(
            "For auth.py use a Desktop OAuth client JSON (contains 'installed' key). "
            "Download: GCP -> Clients -> Desktop app -> Download JSON."
        )

    return problems


def load_saved_credentials(scopes: list[str] | None = None) -> Credentials | None:
    scopes = scopes or SCOPES
    if not TOKEN_FILE.is_file():
        return None
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), scopes)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    if creds.valid:
        return creds
    return None


def run_oauth_flow(login_hint: str) -> Credentials:
    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)

    print(f"Opening browser - sign in with: {login_hint}", flush=True)
    print("IMPORTANT: Keep this terminal open until you see 'Authenticated successfully'.", flush=True)
    print("Do NOT reuse an old localhost link from a previous attempt.\n", flush=True)

    last_error: OSError | None = None
    for port in OAUTH_PORTS:
        try:
            return flow.run_local_server(
                port=port,
                open_browser=True,
                prompt="consent",
                access_type="offline",
                login_hint=login_hint,
                authorization_prompt_message=(
                    f"Waiting for Google sign-in on http://localhost:{port}/ ...\n"
                    f"Use account: {login_hint}\n"
                    "Keep the terminal open until auth completes.\n"
                ),
                success_message=(
                    "Authentication complete. You can close this browser tab."
                ),
            )
        except OSError as exc:
            last_error = exc
            print(f"Port {port} unavailable, trying next...", flush=True)

    raise OSError(
        f"Could not start local OAuth server on ports {OAUTH_PORTS}."
    ) from last_error


def get_credentials(
    scopes: list[str] | None = None,
    *,
    force_refresh: bool = False,
    login_hint: str | None = None,
) -> Credentials:
    problems = validate_credentials_file()
    if problems:
        raise SystemExit("\n".join(f"Setup error: {p}" for p in problems))

    scopes = scopes or SCOPES
    login_hint = login_hint or load_env_value("GOOGLE_OAUTH_EMAIL", DEFAULT_LOGIN_EMAIL)

    if not force_refresh:
        creds = load_saved_credentials(scopes)
        if creds:
            return creds

    creds = run_oauth_flow(login_hint)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def print_gcp_fix_instructions() -> None:
    email = load_env_value("GOOGLE_OAUTH_EMAIL", DEFAULT_LOGIN_EMAIL)
    project = load_env_value("GOOGLE_CLOUD_PROJECT_ID", "silver-treat-499611-r3")
    print(
        f"\nIf Google shows 'Access blocked' or Error 403:\n"
        f"  1. Open: https://console.cloud.google.com/auth/audience?project={project}\n"
        f"  2. Under Test users -> Add users -> {email}\n"
        f"  3. Save, then run: python auth.py --force\n"
        f"\nIf localhost refused to connect:\n"
        f"  - That link is expired. Run: python auth.py --force\n"
        f"  - Use the NEW link printed in the terminal (not an old browser tab).\n"
    )


def main() -> None:
    force = "--force" in sys.argv
    problems = validate_credentials_file()
    if problems:
        for p in problems:
            print(f"ERROR: {p}")
        print_gcp_fix_instructions()
        raise SystemExit(1)

    if not force:
        existing = load_saved_credentials()
        if existing:
            print("Already authenticated - token.json is valid.", flush=True)
            print(f"Token file: {TOKEN_FILE.relative_to(ROOT)}", flush=True)
            if existing.expiry:
                print(f"Token expires: {existing.expiry.isoformat()}", flush=True)
            print("To sign in again, run: python auth.py --force", flush=True)
            return

    try:
        creds = get_credentials(force_refresh=True)
    except Exception as exc:
        print(f"\nAuthentication failed: {exc}")
        print_gcp_fix_instructions()
        raise SystemExit(1) from exc

    print("Authenticated successfully.", flush=True)
    print(f"Token saved to {TOKEN_FILE.relative_to(ROOT)}", flush=True)
    if creds.expiry:
        print(f"Token expires: {creds.expiry.isoformat()}", flush=True)


if __name__ == "__main__":
    main()
