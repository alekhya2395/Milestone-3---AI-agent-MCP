"""Google Docs + Gmail publish via API (fallback when Workspace MCP unavailable)."""

from __future__ import annotations

import base64
from email.mime.text import MIMEText

from google_auth import get_credentials


def publish_pulse_to_doc(doc_id: str, text: str) -> dict:
    """Replace content of an existing Google Doc."""
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build("docs", "v1", credentials=creds, cache_discovery=False)

    doc = service.documents().get(documentId=doc_id).execute()
    body = doc.get("body", {}).get("content", [])
    end_index = body[-1].get("endIndex", 1) - 1 if body else 1

    requests = []
    if end_index > 1:
        requests.append(
            {"deleteContentRange": {"range": {"startIndex": 1, "endIndex": end_index}}}
        )
    requests.append({"insertText": {"location": {"index": 1}, "text": text}})

    service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

    doc = service.documents().get(documentId=doc_id).execute()
    title = doc.get("title", "")
    content = ""
    for el in doc.get("body", {}).get("content", []):
        para = el.get("paragraph")
        if not para:
            continue
        for elem in para.get("elements", []):
            content += elem.get("textRun", {}).get("content", "")

    snippet = text.splitlines()[0][:40] if text else ""
    verified = snippet in content
    return {
        "verified": verified,
        "title": title,
        "chars": len(content),
        "doc_url": f"https://docs.google.com/document/d/{doc_id}/edit",
    }


def create_new_google_doc(title: str, text: str, folder_id: str = "") -> dict:
    """Create a new Google Doc via Drive + Docs API."""
    from googleapiclient.discovery import build

    creds = get_credentials()
    drive = build("drive", "v3", credentials=creds, cache_discovery=False)

    metadata: dict = {"name": title, "mimeType": "application/vnd.google-apps.document"}
    if folder_id:
        metadata["parents"] = [folder_id]

    created = drive.files().create(body=metadata, fields="id").execute()
    doc_id = created["id"]
    check = publish_pulse_to_doc(doc_id, text)
    check["doc_id"] = doc_id
    return check


def create_gmail_draft(to: str, subject: str, body: str) -> dict:
    """Create a Gmail draft via Gmail API."""
    from googleapiclient.discovery import build

    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}
    ).execute()

    return {"draft_id": draft.get("id"), "message_id": draft.get("message", {}).get("id")}
