#!/usr/bin/env python3
"""Inspect Cursor state.vscdb for MCP server entries."""
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("tables:", [r[0] for r in cur.fetchall()])

for table in ("ItemTable", "cursorDiskKV"):
    try:
        cur.execute(f"SELECT key, length(value) FROM {table}")
        rows = cur.fetchall()
        hits = [
            (k, n)
            for k, n in rows
            if k
            and (
                "mcp" in k.lower()
                or "alphavantage" in k.lower()
                or "google-drive" in k.lower()
                or "google-gmail" in k.lower()
            )
        ]
        print(f"\n{table} MCP-related keys ({len(hits)}):")
        for k, n in hits:
            print(f"  {k} ({n} bytes)")
    except Exception as e:
        print(f"{table}: {e}")

# Search values too
for table in ("ItemTable", "cursorDiskKV"):
    try:
        cur.execute(
            f"SELECT key FROM {table} WHERE value LIKE '%alphavantage%' OR value LIKE '%google-drive%' OR value LIKE '%google-gmail%' OR value LIKE '%mcpServers%'"
        )
        rows = cur.fetchall()
        print(f"\n{table} value matches ({len(rows)}):")
        for (k,) in rows[:40]:
            print(f"  {k}")
    except Exception as e:
        print(f"{table} value search: {e}")

conn.close()
