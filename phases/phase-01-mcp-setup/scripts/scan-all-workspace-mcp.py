#!/usr/bin/env python3
"""Scan all Cursor workspace DBs for MCP server references."""
import json
import sqlite3
from pathlib import Path

WS = Path.home() / "AppData/Roaming/Cursor/User/workspaceStorage"
NEEDLES = ("alphavantage", "google-drive", "google-gmail", "mcpServers", "knownServerIds")


def scan_db(db_path: Path) -> None:
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.Error as e:
        print(f"  skip {db_path.name}: {e}")
        return
    cur = conn.cursor()
    hits = []
    for table in ("ItemTable", "cursorDiskKV"):
        try:
            rows = cur.execute(f"SELECT key, value FROM {table}").fetchall()
        except sqlite3.Error:
            continue
        for key, val in rows:
            text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
            if any(n.lower() in key.lower() or n.lower() in text.lower() for n in NEEDLES):
                if any(n in text for n in ("alphavantage", "google-drive", "google-gmail")):
                    hits.append((table, key, text[:400]))
    conn.close()
    if hits:
        ws_json = db_path.parent / "workspace.json"
        label = ws_json.read_text(encoding="utf-8")[:120] if ws_json.exists() else db_path.parent.name
        print(f"\n=== {db_path.parent.name} ===")
        print(f"  {label}")
        for table, key, snippet in hits:
            print(f"  [{table}] {key}")
            print(f"    {snippet[:300]}")


def main() -> None:
    for folder in sorted(WS.iterdir()):
        db = folder / "state.vscdb"
        if db.exists():
            scan_db(db)


if __name__ == "__main__":
    main()
