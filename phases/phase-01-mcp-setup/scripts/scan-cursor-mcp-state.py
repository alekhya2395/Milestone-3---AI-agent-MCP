#!/usr/bin/env python3
"""Deep scan Cursor state for MCP server references."""
import json
import sqlite3
from pathlib import Path

GLOBAL_DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
WS_ID = "2be959de5f50993e975cfdb5cfdfb508"
WS_DB = Path.home() / f"AppData/Roaming/Cursor/User/workspaceStorage/{WS_ID}/state.vscdb"

NEEDLES = ("alphavantage", "google-drive", "google-gmail", "google_drive", "google_gmail", "mcpServers")


def scan_db(path: Path, label: str) -> None:
    if not path.exists():
        print(f"\n[{label}] missing: {path}")
        return
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in cur.fetchall()]
    print(f"\n[{label}] {path}")
    for table in tables:
        try:
            cur.execute(f"SELECT key, value FROM {table}")
            hits = []
            for key, val in cur.fetchall():
                text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
                blob = f"{key} {text}"
                if any(n in blob.lower() for n in NEEDLES):
                    hits.append((key, text[:300]))
            if hits:
                print(f"  table {table}: {len(hits)} hit(s)")
                for k, preview in hits[:15]:
                    print(f"    KEY: {k}")
                    print(f"    VAL: {preview[:200]}...")
        except Exception as e:
            print(f"  table {table}: error {e}")
    conn.close()


def read_key(db: Path, key: str) -> None:
    conn = sqlite3.connect(db)
    row = conn.execute("SELECT value FROM ItemTable WHERE key=?", (key,)).fetchone()
    conn.close()
    print(f"\n=== {key} ===")
    if not row:
        print("(missing)")
        return
    val = row[0].decode() if isinstance(row[0], bytes) else row[0]
    print(val[:3000] if len(val) > 3000 else val)


if __name__ == "__main__":
    scan_db(GLOBAL_DB, "global")
    scan_db(WS_DB, "workspace")
    read_key(GLOBAL_DB, "mcpService.knownServerIds")
    read_key(
        GLOBAL_DB,
        "src.vs.platform.reactivestorage.browser.reactiveStorageServiceImpl.persistentStorage.applicationUser",
    )
