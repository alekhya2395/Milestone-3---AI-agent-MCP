#!/usr/bin/env python3
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
NEEDLE = "YOUR_API_KEY"
conn = sqlite3.connect(DB)
cur = conn.cursor()

print("=== ItemTable hits ===")
for key, val in cur.execute("SELECT key, value FROM ItemTable"):
    text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
    if NEEDLE in text or ("alphavantage" in text.lower() and "apikey" in text.lower()):
        print(f"\n{key}:")
        print(text[:1500])

print("\n=== cursorDiskKV hits ===")
for key, val in cur.execute("SELECT key, value FROM cursorDiskKV"):
    text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
    if NEEDLE in text or ("alphavantage" in text.lower() and "mcpServers" in text):
        print(f"\n{key}:")
        print(text[:1500])

# applicationUser mcpServers path
app_key = "src.vs.platform.reactivestorage.browser.reactiveStorageServiceImpl.persistentStorage.applicationUser"
row = cur.execute("SELECT value FROM ItemTable WHERE key=?", (app_key,)).fetchone()
if row:
    data = json.loads(row[0])
    print("\n=== applicationUser.mcpServers ===")
    print(json.dumps(data.get("mcpServers", "MISSING"), indent=2)[:2000])

row2 = cur.execute("SELECT value FROM ItemTable WHERE key='mcpService.knownServerIds'").fetchone()
print("\n=== knownServerIds ===")
print(row2[0] if row2 else "none")

conn.close()
