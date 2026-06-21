#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
WS = Path.home() / "AppData/Roaming/Cursor/User/workspaceStorage/2be959de5f50993e975cfdb5cfdfb508/state.vscdb"

for label, db in [("global", DB), ("workspace", WS)]:
    conn = sqlite3.connect(db)
    hits = []
    for key, val in conn.execute("SELECT key, value FROM ItemTable"):
        text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
        low = f"{key} {text}".lower()
        if "google-drive" in low or "google-gmail" in low or "alphavantage" in low or "user-alphavantage" in low:
            hits.append((key, text[:400]))
    conn.close()
    print(f"\n=== {label}: {len(hits)} hits ===")
    for k, v in hits:
        print(f"KEY: {k}")
        print(f"VAL: {v}\n")
