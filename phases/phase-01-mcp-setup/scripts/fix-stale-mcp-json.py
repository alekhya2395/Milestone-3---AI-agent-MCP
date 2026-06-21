#!/usr/bin/env python3
"""Overwrite stale mcp.json overlay cache (root cause of old API key in Settings UI)."""
import json
import re
import shutil
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
GLOBAL_MCP = Path.home() / ".cursor" / "mcp.json"
CLEAN = '{\n  "mcpServers": {}\n}\n'
NEEDLE = "YOUR_API_KEY"
MCP_MARKERS = ("/.cursor/mcp.json", "%2F.cursor%2Fmcp.json", "mcp.json")


def is_mcp_json_key(key: str) -> bool:
    return any(m in key for m in MCP_MARKERS)


def main() -> None:
    GLOBAL_MCP.parent.mkdir(parents=True, exist_ok=True)
    GLOBAL_MCP.write_text(CLEAN, encoding="utf-8")
    print(f"wrote disk: {GLOBAL_MCP}")

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Overwrite (not delete) editor overlay — deleting lets Cursor restore from memory
    ofs_updated = 0
    for (key,) in cur.execute("SELECT key FROM cursorDiskKV WHERE key LIKE 'ofsContent:%'"):
        if is_mcp_json_key(key):
            cur.execute(
                "UPDATE cursorDiskKV SET value = ? WHERE key = ?",
                (CLEAN.encode("utf-8"), key),
            )
            ofs_updated += 1
            print(f"overwrote ofsContent: {key}")

    # Remove composer snapshots containing old mcp.json
    composer_removed = 0
    for (key,) in cur.execute("SELECT key FROM cursorDiskKV WHERE key LIKE 'composer.content.%'"):
        val = cur.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (key,)).fetchone()[0]
        text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
        if NEEDLE in text and "mcpServers" in text:
            cur.execute("DELETE FROM cursorDiskKV WHERE key = ?", (key,))
            composer_removed += 1
            print(f"deleted composer snapshot: {key}")

    cur.execute(
        "UPDATE ItemTable SET value = ? WHERE key = 'mcpService.knownServerIds'",
        (json.dumps([]),),
    )

    conn.commit()
    conn.close()

    # Remove alphavantage MCP cache
    cache_removed = 0
    projects_root = Path.home() / ".cursor" / "projects"
    for mcps_dir in projects_root.glob("*/mcps"):
        for child in list(mcps_dir.iterdir()):
            if "alphavantage" in child.name.lower():
                shutil.rmtree(child, ignore_errors=True)
                cache_removed += 1

    # Remove Cursor local history for mcp.json if present
    history_root = Path.home() / "AppData/Roaming/Cursor/User/History"
    for entries in history_root.glob("*/entries.json"):
        try:
            data = json.loads(entries.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if "mcp.json" in data.get("resource", "") and ".cursor" in data.get("resource", ""):
            shutil.rmtree(entries.parent, ignore_errors=True)
            print(f"removed history: {entries.parent}")

    print(
        f"\nDone. ofs_updated={ofs_updated}, composer_removed={composer_removed}, "
        f"cache_removed={cache_removed}"
    )


if __name__ == "__main__":
    main()
