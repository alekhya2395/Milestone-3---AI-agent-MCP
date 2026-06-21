#!/usr/bin/env python3
import json
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# All ItemTable keys with mcp in name
print("=== ItemTable keys containing 'mcp' ===")
for (k,) in cur.execute("SELECT key FROM ItemTable WHERE lower(key) LIKE '%mcp%'"):
    val = cur.execute("SELECT value FROM ItemTable WHERE key=?", (k,)).fetchone()[0]
    text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
    print(f"\n{k} ({len(text)} chars)")
    print(text[:500])

# Search applicationUser for mcpServers subtree
app_key = "src.vs.platform.reactivestorage.browser.reactiveStorageServiceImpl.persistentStorage.applicationUser"
row = cur.execute("SELECT value FROM ItemTable WHERE key=?", (app_key,)).fetchone()
if row:
    data = json.loads(row[0])
    def find_mcp(obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                p = f"{path}.{k}" if path else k
                if "mcp" in k.lower() or k in ("mcpServers", "servers"):
                    print(f"\nFOUND PATH: {p}")
                    print(json.dumps(v, indent=2)[:1500])
                find_mcp(v, p)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                find_mcp(v, f"{path}[{i}]")
    find_mcp(data)

conn.close()
