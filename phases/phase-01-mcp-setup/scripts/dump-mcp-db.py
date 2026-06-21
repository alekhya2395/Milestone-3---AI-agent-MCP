#!/usr/bin/env python3
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
conn = sqlite3.connect(DB)
cur = conn.cursor()

print("=== All ItemTable keys with mcp/oauth/alphavantage ===")
for (k,) in cur.execute("SELECT key FROM ItemTable"):
    kl = k.lower()
    if "mcp" in kl or "oauth" in kl or "alphavantage" in kl:
        val = cur.execute("SELECT value FROM ItemTable WHERE key=?", (k,)).fetchone()[0]
        text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
        print(f"\n{k} ({len(text)} chars):")
        print(text[:1000])

print("\n=== cursorDiskKV: mcp.json ofsContent ===")
for (k,) in cur.execute("SELECT key FROM cursorDiskKV WHERE key LIKE '%mcp.json%'"):
    val = cur.execute("SELECT value FROM cursorDiskKV WHERE key=?", (k,)).fetchone()[0]
    text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
    print(f"\n{k} ({len(text)} chars):")
    print(text)

print("\n=== cursorDiskKV: alphavantage in value ===")
for (k,) in cur.execute("SELECT key FROM cursorDiskKV"):
    val = cur.execute("SELECT value FROM cursorDiskKV WHERE key=?", (k,)).fetchone()[0]
    text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
    if "YOUR_API_KEY" in text or ("alphavantage" in text.lower() and "mcpServers" in text):
        print(f"\n{k}:")
        print(text[:800])

conn.close()
