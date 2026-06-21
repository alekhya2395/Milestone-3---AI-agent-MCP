#!/usr/bin/env python3
"""Phase 1 — probe Google Workspace MCP endpoints (no OAuth required for reachability)."""

import json
import urllib.error
import urllib.request

ENDPOINTS = {
    "drive": "https://drivemcp.googleapis.com/mcp/v1",
    "gmail": "https://gmailmcp.googleapis.com/mcp/v1",
}


def probe(name: str, url: str) -> dict:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"name": name, "url": url, "status": resp.status, "reachable": True}
    except urllib.error.HTTPError as e:
        # 401/403/404 often expected without auth — still proves endpoint exists
        return {
            "name": name,
            "url": url,
            "status": e.code,
            "reachable": True,
            "note": "HTTP error without OAuth is expected",
        }
    except Exception as e:
        return {"name": name, "url": url, "reachable": False, "error": str(e)}


def main() -> None:
    results = [probe(n, u) for n, u in ENDPOINTS.items()]
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
