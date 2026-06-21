#!/usr/bin/env python3
"""Find any Cursor DB value containing alphavantage or the old API key."""
import sqlite3
from pathlib import Path

NEEDLES = ("YOUR_API_KEY", "alphavantage", "mcp.alphavantage.co")
DB_PATHS = [
    Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb",
    Path.home() / "AppData/Roaming/Cursor/User/workspaceStorage/2be959de5f50993e975cfdb5cfdfb508/state.vscdb",
]


def scan_db(path: Path) -> None:
    if not path.exists():
        return
    conn = sqlite3.connect(path)
    for table in ("ItemTable", "cursorDiskKV"):
        try:
            rows = conn.execute(f"SELECT key, value FROM {table}").fetchall()
        except sqlite3.Error:
            continue
        for key, val in rows:
            text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
            if any(n.lower() in key.lower() or n.lower() in text.lower() for n in NEEDLES):
                print(f"\n[{path.name}/{table}] {key[:120]}")
                idx = text.lower().find("alphavantage")
                if idx == -1:
                    idx = text.lower().find("48kxet")
                start = max(0, idx - 80)
                print(text[start : start + 400])
    conn.close()


for db in DB_PATHS:
    scan_db(db)

# Also scan all workspace DBs
ws = Path.home() / "AppData/Roaming/Cursor/User/workspaceStorage"
for folder in ws.iterdir():
    db = folder / "state.vscdb"
    if db.exists():
        scan_db(db)
