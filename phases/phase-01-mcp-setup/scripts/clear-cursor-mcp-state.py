#!/usr/bin/env python3
"""Remove stale MCP servers from Cursor internal state and local mcps cache."""
import json
import shutil
import sqlite3
from pathlib import Path

DB = Path.home() / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
REMOVE_IDS = {
    "user-alphavantage",
    "alphavantage",
    "google-drive",
    "google-gmail",
    "project-0-MILESTONE 3 - AI AGENT WITH MCP-google-drive",
    "project-0-MILESTONE 3 - AI AGENT WITH MCP-google-gmail",
}
REMOVE_NAME_FRAGMENTS = ("alphavantage", "google-drive", "google-gmail")

KEYS_TO_CLEAR_PREFIX = (
    "mcpOAuth.global.",
    "mcpService.",
    "cursor/approvedProjectMcpServers",
)


def should_remove_server_id(sid: str) -> bool:
    if sid in REMOVE_IDS:
        return True
    return any(frag in sid for frag in REMOVE_NAME_FRAGMENTS)


def clean_known_server_ids(raw: str) -> tuple[str, bool]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw, False

    changed = False
    if isinstance(data, list):
        new = [x for x in data if not should_remove_server_id(str(x))]
        changed = len(new) != len(data)
        return json.dumps(new), changed
    if isinstance(data, dict):
        new = {k: v for k, v in data.items() if not should_remove_server_id(str(k))}
        changed = len(new) != len(data)
        return json.dumps(new), changed
    return raw, False


def clean_application_user(raw: str) -> tuple[str, bool]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return raw, False

    changed = False

    # Cursor stores MCP servers in various nested paths; scrub known shapes
    def scrub(obj):
        nonlocal changed
        if isinstance(obj, dict):
            for key in list(obj.keys()):
                if should_remove_server_id(str(key)) or any(
                    f in str(key).lower() for f in REMOVE_NAME_FRAGMENTS
                ):
                    del obj[key]
                    changed = True
                else:
                    scrub(obj[key])
        elif isinstance(obj, list):
            kept = []
            for item in obj:
                if isinstance(item, str) and should_remove_server_id(item):
                    changed = True
                    continue
                if isinstance(item, dict):
                    name = item.get("name") or item.get("serverName") or item.get("identifier")
                    if name and should_remove_server_id(str(name)):
                        changed = True
                        continue
                scrub(item)
                kept.append(item)
            if len(kept) != len(obj):
                obj.clear()
                obj.extend(kept)

    scrub(data)
    return json.dumps(data), changed


def main() -> None:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    deleted = 0
    updated = 0

    # Delete OAuth + MCP service keys
    cur.execute("SELECT key FROM ItemTable")
    all_keys = [r[0] for r in cur.fetchall()]
    for key in all_keys:
        if key == "mcpService.knownServerIds":
            continue
        if any(key.startswith(p) for p in KEYS_TO_CLEAR_PREFIX) or (
            "alphavantage" in key.lower()
            or "google-drive" in key.lower()
            or "google-gmail" in key.lower()
        ):
            cur.execute("DELETE FROM ItemTable WHERE key = ?", (key,))
            deleted += 1
            print(f"deleted: {key}")

    # Clean knownServerIds
    cur.execute("SELECT value FROM ItemTable WHERE key = 'mcpService.knownServerIds'")
    row = cur.fetchone()
    if row:
        new_val, changed = clean_known_server_ids(row[0].decode() if isinstance(row[0], bytes) else row[0])
        if changed:
            cur.execute(
                "UPDATE ItemTable SET value = ? WHERE key = 'mcpService.knownServerIds'",
                (new_val,),
            )
            updated += 1
            print("updated: mcpService.knownServerIds")
        else:
            print("knownServerIds unchanged:", new_val[:200])

    # Clean applicationUser persistent storage (UI MCP list)
    app_key = "src.vs.platform.reactivestorage.browser.reactiveStorageServiceImpl.persistentStorage.applicationUser"
    cur.execute("SELECT value FROM ItemTable WHERE key = ?", (app_key,))
    row = cur.fetchone()
    if row:
        raw = row[0].decode() if isinstance(row[0], bytes) else row[0]
        new_val, changed = clean_application_user(raw)
        if changed:
            cur.execute("UPDATE ItemTable SET value = ? WHERE key = ?", (new_val, app_key))
            updated += 1
            print("updated: applicationUser persistent storage")

    conn.commit()
    conn.close()

    # Remove cached MCP tool descriptors (Settings can keep showing these while Cursor runs)
    cache_removed = 0
    projects_root = Path.home() / ".cursor" / "projects"
    cache_name_fragments = ("alphavantage", "google-drive", "google-gmail")
    if projects_root.is_dir():
        for mcps_dir in projects_root.glob("*/mcps"):
            for child in list(mcps_dir.iterdir()):
                name = child.name.lower()
                if any(frag in name for frag in cache_name_fragments):
                    shutil.rmtree(child, ignore_errors=True)
                    cache_removed += 1
                    print(f"removed cache: {child}")

    print(f"\nDone. deleted={deleted}, updated={updated}, cache_dirs_removed={cache_removed}")
    print("Fully quit Cursor (File > Exit), then reopen. Reload Window is not enough.")


if __name__ == "__main__":
    main()
