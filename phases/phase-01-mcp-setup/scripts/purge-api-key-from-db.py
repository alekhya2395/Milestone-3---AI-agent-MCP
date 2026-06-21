#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
NEEDLE = "YOUR_API_KEY"
conn = sqlite3.connect(DB)
cur = conn.cursor()
removed = 0
for (key,) in cur.execute("SELECT key FROM cursorDiskKV"):
    val = cur.execute("SELECT value FROM cursorDiskKV WHERE key=?", (key,)).fetchone()[0]
    text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
    if NEEDLE in text:
        cur.execute("DELETE FROM cursorDiskKV WHERE key=?", (key,))
        removed += 1
        print(f"deleted: {key[:100]}")
conn.commit()
conn.close()
print(f"removed {removed} rows containing API key")
