"""
sync_wiki.py — Fetch game data from genshin.jmp.blue and cache locally.

Usage:
    python sync_wiki.py              # sync all data
    python sync_wiki.py --character furina  # sync single character

All data is cached as JSON in data/cache/. Incremental detection
compares version metadata to avoid unnecessary re-fetching.
If the API is down, the cache is used as fallback.
"""

import json
import os
import sys
import time
import requests
from pathlib import Path

import config
from typing import Union, Optional

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ensure_cache_dir(subdir: str = "") -> str:
    """Create (if needed) and return the path to a cache subdirectory."""
    path = os.path.join(config.CACHE_DIR, subdir)
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def api_get(endpoint: str):
    """Call the genshin.jmp.blue API with timeout and error handling."""
    url = f"{config.DATA_API_BASE}{endpoint}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        print(f"[WARN] API call failed: {url} — {exc}")
        return None


def load_cache(subdir: str, filename: str):
    """Load a cached JSON file, or None if missing/corrupt."""
    filepath = os.path.join(config.CACHE_DIR, subdir, f"{filename}.json")
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def save_cache(subdir: str, filename: str, data):
    """Save data as JSON to the cache."""
    ensure_cache_dir(subdir)
    filepath = os.path.join(config.CACHE_DIR, subdir, f"{filename}.json")
    with open(filepath, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    print(f"[CACHE] Saved {subdir}/{filename}.json")


# ---------------------------------------------------------------------------
# Sync: Characters
# ---------------------------------------------------------------------------

def sync_characters(character_id: Optional[str] = None) -> list:
    """
    Sync character data. Returns list of character IDs that CHANGED.

    If character_id is given, sync only that character. Otherwise sync all.
    """
    ensure_cache_dir("characters")
    changed: list[str] = []

    # Determine which characters to process
    if character_id:
        char_list = [character_id]
    else:
        char_list_raw = api_get(config.DATA_ENDPOINTS["characters"])
        if char_list_raw is None:
            print("[ERROR] Cannot fetch character list and no cache — aborting.")
            return []
        # The endpoint returns a list of strings (character IDs like "albedo", "raiden", ...)
        char_list = [c for c in char_list_raw if isinstance(c, str)]
        # Save the list itself
        save_cache("characters", "_index", char_list)

    for cid in char_list:
        print(f"[SYNC] Character: {cid}")
        data = api_get(f"{config.DATA_ENDPOINTS['characters']}/{cid}")
        if data is None:
            print(f"  -> API unavailable, checking cache...")
            cached = load_cache("characters", cid)
            if cached is not None:
                print(f"  -> Using cached data for {cid}")
            else:
                print(f"  -> No cache for {cid}, skipping.")
            continue

        # Compare with existing cache
        cached = load_cache("characters", cid)
        if cached is not None:
            # Simple version/name check for change detection
            old_ver = cached.get("version", "")
            new_ver = data.get("version", "")
            if old_ver == new_ver:
                print(f"  -> Unchanged (version {new_ver}), skipped.")
                continue

        save_cache("characters", cid, data)
        changed.append(cid)
        print(f"  -> Updated (version {data.get('version', 'unknown')})")

    return changed


# ---------------------------------------------------------------------------
# Sync: Weapons
# ---------------------------------------------------------------------------

def sync_weapons() -> bool:
    """Sync weapon data. Returns True if data changed."""
    ensure_cache_dir("weapons")
    print("[SYNC] Weapons...")
    data = api_get(config.DATA_ENDPOINTS["weapons"])
    if data is None:
        cached = load_cache("weapons", "_all")
        if cached is not None:
            print("  -> Using cached weapon data.")
            return False
        print("[ERROR] Cannot fetch weapons and no cache.")
        return False

    cached = load_cache("weapons", "_all")
    save_cache("weapons", "_all", data)
    changed = cached is None or json.dumps(cached, sort_keys=True) != json.dumps(data, sort_keys=True)
    print(f"  -> {'Updated' if changed else 'Unchanged'}")
    return changed


# ---------------------------------------------------------------------------
# Sync: Artifacts
# ---------------------------------------------------------------------------

def sync_artifacts() -> bool:
    """Sync artifact data. Returns True if data changed."""
    ensure_cache_dir("artifacts")
    print("[SYNC] Artifacts...")
    data = api_get(config.DATA_ENDPOINTS["artifacts"])
    if data is None:
        cached = load_cache("artifacts", "_all")
        if cached is not None:
            print("  -> Using cached artifact data.")
            return False
        print("[ERROR] Cannot fetch artifacts and no cache.")
        return False

    cached = load_cache("artifacts", "_all")
    save_cache("artifacts", "_all", data)
    changed = cached is None or json.dumps(cached, sort_keys=True) != json.dumps(data, sort_keys=True)
    print(f"  -> {'Updated' if changed else 'Unchanged'}")
    return changed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sync genshin.jmp.blue data to local cache.")
    parser.add_argument("--character", type=str, default=None, help="Sync a single character by ID.")
    args = parser.parse_args()

    print("=" * 50)
    print("GenshinGuide — Wiki Data Sync")
    print(f"Data source: {config.DATA_API_BASE}")
    print("=" * 50)

    changed_characters = sync_characters(args.character)
    weapons_changed = sync_weapons()
    artifacts_changed = sync_artifacts()

    print("\n--- Sync Summary ---")
    print(f"Characters changed: {len(changed_characters)}")
    if changed_characters:
        print(f"  -> {', '.join(changed_characters)}")
    print(f"Weapons changed: {weapons_changed}")
    print(f"Artifacts changed: {artifacts_changed}")

    return changed_characters


if __name__ == "__main__":
    main()
