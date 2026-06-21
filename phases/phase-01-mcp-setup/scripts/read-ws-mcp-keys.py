#!/usr/bin/env python3
import sqlite3
from pathlib import Path

WS = Path.home() / "AppData/Roaming/Cursor/User/workspaceStorage/2be959de5f50993e975cfdb5cfdfb508/state.vscdb"
conn = sqlite3.connect(WS)
cur = conn.cursor()
print("ItemTable keys with mcp/cursor:")
for (k,) in cur.execute("SELECT key FROM ItemTable WHERE lower(key) LIKE '%mcp%' OR lower(key) LIKE '%cursor/%'"):
    val = cur.execute("SELECT value FROM ItemTable WHERE key=?", (k,)).fetchone()[0]
    text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
    print(f"\n{k} ({len(text)} chars):\n{text[:800]}")
conn.close()
