"""HTTP JSON-RPC client for Google Workspace MCP servers (Drive, Gmail)."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

DRIVE_MCP_URL = "https://drivemcp.googleapis.com/mcp/v1"
GMAIL_MCP_URL = "https://gmailmcp.googleapis.com/mcp/v1"


class WorkspaceMcpError(RuntimeError):
    pass


def _parse_sse_payload(raw: str) -> dict[str, Any]:
    """Extract JSON from SSE or plain JSON response bodies."""
    raw = raw.strip()
    if not raw:
        raise WorkspaceMcpError("Empty MCP response")

    if raw.startswith("{"):
        return json.loads(raw)

    for line in raw.splitlines():
        if line.startswith("data:"):
            data = line[5:].strip()
            if data and data != "[DONE]":
                return json.loads(data)
    raise WorkspaceMcpError(f"Could not parse MCP response: {raw[:300]}")


class WorkspaceMcpClient:
    def __init__(self, base_url: str, access_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.access_token = access_token
        self._req_id = 0

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.base_url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "Authorization": f"Bearer {self.access_token}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise WorkspaceMcpError(
                f"MCP HTTP {exc.code}: {detail[:500] or exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise WorkspaceMcpError(f"MCP request failed: {exc.reason}") from exc

        data = _parse_sse_payload(raw)
        if "error" in data:
            err = data["error"]
            msg = err.get("message", err) if isinstance(err, dict) else err
            raise WorkspaceMcpError(f"MCP error: {msg}")
        return data

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        self._req_id += 1
        data = self._post(
            {
                "jsonrpc": "2.0",
                "id": self._req_id,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )
        result = data.get("result")
        if isinstance(result, dict) and result.get("isError"):
            blocks = result.get("content") or []
            msg = blocks[0].get("text", "Unknown MCP tool error") if blocks else "MCP tool error"
            raise WorkspaceMcpError(msg)
        if isinstance(result, dict) and "content" in result:
            blocks = result["content"]
            if blocks and isinstance(blocks[0], dict) and "text" in blocks[0]:
                text = blocks[0]["text"]
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict) and parsed.get("error"):
                        raise WorkspaceMcpError(str(parsed["error"]))
                    return parsed
                except json.JSONDecodeError:
                    if "permission" in text.lower() or "error" in text.lower():
                        raise WorkspaceMcpError(text)
                    return text
        return result

    def list_tools(self) -> list[dict[str, Any]]:
        self._req_id += 1
        data = self._post(
            {"jsonrpc": "2.0", "id": self._req_id, "method": "tools/list", "params": {}}
        )
        tools = data.get("result", {}).get("tools", [])
        return tools if isinstance(tools, list) else []


def drive_client(access_token: str) -> WorkspaceMcpClient:
    return WorkspaceMcpClient(DRIVE_MCP_URL, access_token)


def gmail_client(access_token: str) -> WorkspaceMcpClient:
    return WorkspaceMcpClient(GMAIL_MCP_URL, access_token)


def normalize_doc_text(text: str) -> str:
    """Collapse whitespace for content parity checks."""
    text = re.sub(r"\r\n?", "\n", text)
    return re.sub(r"[ \t]+", " ", text).strip()
