#!/usr/bin/env python3
"""
make.py — GenshinGuide Content Pipeline Master Script
======================================================
One command to rule them all. No AI APIs. Zero cost.

Usage:
    python make.py sync                     # Sync latest game data
    python make.py scaffold {character}     # Create scaffold JSON for editing
    python make.py render {character}       # Render HTML from edited JSON
    python make.py publish {character}      # Publish after human review
    python make.py new {character}          # Full flow: scaffold (you edit) -> ready to render
    python make.py update-all               # Re-render all guides from JSONs
    python make.py list                     # List all cached characters
    python make.py status                   # Show pipeline status
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Ensure we're in the pipeline directory
SCRIPT_DIR = Path(__file__).parent
os.chdir(SCRIPT_DIR)

import config
import sync_wiki
import generate


def cmd_sync():
    """Pull latest game data from genshin.jmp.blue."""
    print("\n📡 Syncing game data from genshin.jmp.blue...")
    changed = sync_wiki.main()
    if changed:
        print(f"\n✅ {len(changed)} characters updated:")
        for c in changed:
            print(f"   - {c}")
    else:
        print("\n✅ Data is up to date.")
    return changed


def cmd_scaffold(character_id: str):
    """Create a scaffold JSON for manual content writing."""
    print(f"\n📝 Creating scaffold for {character_id}...")
    # Ensure data exists
    char_data = sync_wiki.load_cache("characters", character_id)
    if char_data is None:
        print(f"   Syncing {character_id} data first...")
        sync_wiki.sync_characters(character_id)

    scaffold = generate.build_scaffold(character_id)
    if scaffold is None:
        print(f"❌ Failed to create scaffold for {character_id}")
        return

    guide_dir = Path("data/guides")
    guide_dir.mkdir(parents=True, exist_ok=True)
    json_path = guide_dir / f"{character_id}.json"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(scaffold, f, ensure_ascii=False, indent=2)

    print(f"✅ Scaffold: {json_path}")
    print(f"\n📋 Next steps:")
    print(f"   1. Edit {json_path}")
    print(f"   2. Fill in ALL sections (weapons, artifacts, teams, talents, rotation, mistakes)")
    print(f"   3. Use _available_weapons and _available_artifacts in the file as reference")
    print(f"   4. Run: python make.py render {character_id}")
    print(f"   5. Review in browser")
    print(f"   6. Run: python make.py publish {character_id}")


def cmd_render(character_id: str):
    """Render guide HTML from edited JSON."""
    print(f"\n🎨 Rendering guide for {character_id}...")

    json_path = Path("data/guides") / f"{character_id}.json"
    if not json_path.exists():
        print(f"❌ Guide JSON not found: {json_path}")
        print(f"   Run: python make.py scaffold {character_id}")
        return

    char_data = sync_wiki.load_cache("characters", character_id)
    if char_data is None:
        sync_wiki.sync_characters(character_id)
        char_data = sync_wiki.load_cache("characters", character_id)

    with open(json_path, "r", encoding="utf-8") as f:
        guide_data = json.load(f)

    # Verify
    element = guide_data.get("_element", "electro")
    import verify
    result = verify.verify_guide(guide_data, character_id=character_id, expected_element=element)
    if not result.get("passed"):
        print(f"\n⚠️  Verification warnings/errors — review before publishing:")
        for e in result.get("errors", []):
            print(f"   ❌ {e}")
        for w in result.get("warnings", []):
            print(f"   ⚠️  {w}")

    html = generate.render_guide(guide_data, character_id, char_data)
    output_path = Path(config.OUTPUT_DIR) / f"guide-{character_id}.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"✅ Rendered: {output_path} ({len(html)} bytes)")
    print(f"\n📋 Next: Open in browser to review, then:")
    print(f"   python make.py publish {character_id}")


def cmd_publish(character_id: str):
    """Publish a guide after human review."""
    print(f"\n🚀 Publishing {character_id}...")
    print(f"⚠️  Confirm: has this guide passed HUMAN REVIEW?")
    confirm = input("   Type 'yes' to publish: ").strip().lower()
    if confirm != "yes":
        print("   Aborted.")
        return

    # Run publish.py
    result = subprocess.run(
        [sys.executable, "publish.py", "--character", character_id, "--skip-git"],
        capture_output=False
    )
    if result.returncode != 0:
        print(f"❌ Publish failed.")
        return

    print(f"\n✅ {character_id} guide published!")
    print(f"\n📋 To deploy to live site:")
    print(f"   git add . && git commit -m 'publish: {character_id} guide' && git push")


def cmd_new(character_id: str):
    """Full flow: sync -> scaffold (user edits) -> ready for render."""
    print(f"\n🆕 Creating new guide for {character_id}...")
    cmd_sync()
    cmd_scaffold(character_id)
    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ Pipeline is ready for you.")
    print(f"   Now edit: pipeline/data/guides/{character_id}.json")
    print(f"   Then:     python make.py render {character_id}")
    print(f"   Then:     python make.py publish {character_id}")


def cmd_update_all():
    """Re-render all guides that have JSON files."""
    guide_dir = Path("data/guides")
    if not guide_dir.exists():
        print("❌ No guide JSONs found. Run 'make.py scaffold {id}' first.")
        return

    json_files = list(guide_dir.glob("*.json"))
    print(f"\n🔄 Re-rendering {len(json_files)} guides...")
    for jf in sorted(json_files):
        cid = jf.stem
        try:
            cmd_render(cid)
        except Exception as exc:
            print(f"   ❌ {cid}: {exc}")


def cmd_list():
    """List all characters with cached data."""
    print("\n📋 Cached characters:")
    char_dir = Path(config.CACHE_DIR) / "characters"
    if not char_dir.exists():
        print("   (none — run sync first)")
        return

    for f in sorted(char_dir.glob("*.json")):
        if f.stem.startswith("_"):
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            name = data.get("name", f.stem)
            element = data.get("element", "?")
            weapon = data.get("weapon_type", "?")
            print(f"   {f.stem:20s} {name:30s} {element:8s} {weapon}")
        except:
            print(f"   {f.stem:20s} (unreadable)")


def cmd_status():
    """Show pipeline status."""
    print("\n📊 Pipeline Status")
    print("=" * 50)

    # Game data
    char_dir = Path(config.CACHE_DIR) / "characters"
    weapon_file = Path(config.CACHE_DIR) / "weapons" / "_all.json"
    artifact_file = Path(config.CACHE_DIR) / "artifacts" / "_all.json"

    chars = len(list(char_dir.glob("*.json"))) if char_dir.exists() else 0
    weapons = "✅" if weapon_file.exists() else "❌"
    artifacts = "✅" if artifact_file.exists() else "❌"

    print(f"   Game data cached:  {chars} characters | weapons {weapons} | artifacts {artifacts}")

    # Guide JSONs
    guide_dir = Path("data/guides")
    guides = len(list(guide_dir.glob("*.json"))) if guide_dir.exists() else 0
    print(f"   Guide JSONs:        {guides} ready to render")

    # Rendered HTMLs
    site_dir = Path(config.OUTPUT_DIR)
    htmls = len(list(site_dir.glob("guide-*.html"))) if site_dir.exists() else 0
    print(f"   Rendered HTMLs:     {htmls} guide pages")

    print(f"   Template:           {'✅' if Path(config.TEMPLATE_FILE).exists() else '❌'}")
    print(f"   Config:             {config.CURRENT_VERSION}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
COMMANDS = {
    "sync":       (cmd_sync,        "Sync latest game data from genshin.jmp.blue"),
    "scaffold":   (cmd_scaffold,    "Create scaffold JSON for character (arg: id)"),
    "render":     (cmd_render,      "Render guide HTML from JSON (arg: id)"),
    "publish":    (cmd_publish,     "Publish guide after review (arg: id)"),
    "new":        (cmd_new,         "Full new guide flow (arg: id)"),
    "update-all": (cmd_update_all,  "Re-render all guides from JSONs"),
    "list":       (cmd_list,        "List all cached characters"),
    "status":     (cmd_status,      "Show pipeline status"),
}


def print_help():
    print("\nGenshinGuide Content Pipeline")
    print("=" * 50)
    for name, (_, desc) in COMMANDS.items():
        print(f"  {name:15s} {desc}")
    print()


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    cmd_name = sys.argv[1]
    if cmd_name in ("-h", "--help", "help"):
        print_help()
        return

    if cmd_name not in COMMANDS:
        print(f"Unknown command: {cmd_name}")
        print_help()
        sys.exit(1)

    func, _ = COMMANDS[cmd_name]

    # Commands that take a character argument
    needs_arg = {"scaffold", "render", "publish", "new"}
    if cmd_name in needs_arg:
        if len(sys.argv) < 3:
            print(f"Usage: python make.py {cmd_name} <character_id>")
            sys.exit(1)
        func(sys.argv[2])
    else:
        func()


if __name__ == "__main__":
    main()
