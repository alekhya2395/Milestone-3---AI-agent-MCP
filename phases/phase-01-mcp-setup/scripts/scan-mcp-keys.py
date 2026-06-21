#!/usr/bin/env python3
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
conn = sqlite3.connect(DB)
cur = conn.cursor()

patterns = ("mcpservice", "mcpserver", "knownserver", "installedmcp", "mcp/server", "oauth")
print("ItemTable key scan:")
for (k,) in cur.execute("SELECT key FROM ItemTable"):
    kl = k.lower()
    if any(p in kl for p in patterns):
        val = cur.execute("SELECT value FROM ItemTable WHERE key=?", (k,)).fetchone()[0]
        text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
        print(f"  {k}: {text[:200]}")

print("\ncursorDiskKV key scan (mcp-related, non-chat):")
for (k,) in cur.execute("SELECT key FROM cursorDiskKV"):
    kl = k.lower()
    if any(x in kl for x in ("mcp", "oauth", "server")) and not kl.startswith(("bubble", "composer", "agentkv", "checkpoint", "ofs")):
        val = cur.execute("SELECT value FROM cursorDiskKV WHERE key=?", (k,)).fetchone()[0]
        text = val.decode("utf-8", errors="replace") if isinstance(val, bytes) else str(val)
        print(f"  {k}: {text[:200]}")

conn.close()
