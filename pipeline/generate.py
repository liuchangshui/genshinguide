"""
generate.py — Guide scaffold generator (NO AI APIs).

Instead of calling an LLM, this script:
  1. Loads character data from the local cache (sync_wiki.py)
  2. Creates a data-rich scaffold JSON that a HUMAN writer fills in
  3. Or renders a guide from a completed JSON file using the Jinja2 template

Usage:
    python generate.py --character furina --scaffold    # create a scaffold .json for manual editing
    python generate.py --character furina --render       # render HTML from edited JSON
    python generate.py --character furina                # scaffold + render in one pass
"""

import json
import os
import sys
import argparse
from datetime import date
from pathlib import Path

import config
import sync_wiki
import verify
from jinja2 import Environment, FileSystemLoader

_jinja_env = Environment(loader=FileSystemLoader(config.TEMPLATE_DIR), autoescape=False)
_template = _jinja_env.get_template("guide_template.html")


# ---------------------------------------------------------------------------
# Scaffold: build a JSON template pre-filled with known game data
# ---------------------------------------------------------------------------

ELEMENT_EMOJI = {
    "electro": "⚡", "pyro": "🔥", "hydro": "💧", "dendro": "🌿",
    "anemo": "🍃", "geo": "🪨", "cryo": "❄️",
}
ELEMENT_DISPLAY = {
    "electro": "Electro", "pyro": "Pyro", "hydro": "Hydro",
    "dendro": "Dendro", "anemo": "Anemo", "geo": "Geo", "cryo": "Cryo",
}


def build_scaffold(character_id: str):
    """Build a pre-filled scaffold JSON from cached game data."""
    char_data = sync_wiki.load_cache("characters", character_id)
    if char_data is None:
        print(f"[ERROR] No cached data for {character_id}. Run sync_wiki.py first.")
        return None

    char_name = char_data.get("name", character_id.title())
    # API returns 'vision' for element and 'weapon' for weapon type
    char_element_raw = char_data.get("vision") or char_data.get("element", "")
    element_css = config.ELEMENT_MAP.get(char_element_raw, "electro")
    weapon_type = (char_data.get("weapon") or char_data.get("weapon_type", "Sword")).lower()

    weapons_raw = sync_wiki.load_cache("weapons", "_all")
    weapon_list = weapons_raw if isinstance(weapons_raw, list) else list(weapons_raw.values()) if isinstance(weapons_raw, dict) else []
    # Weapons list contains ID strings — list them all as reference
    matching_weapons = weapon_list[:30] if isinstance(weapon_list, list) else []

    artifacts_raw = sync_wiki.load_cache("artifacts", "_all")
    artifact_list = artifacts_raw if isinstance(artifacts_raw, list) else list(artifacts_raw.values()) if isinstance(artifacts_raw, dict) else []

    scaffold = {
        "_character_id": character_id,
        "_element": element_css,
        "_weapon_type": weapon_type,
        "_game_version": config.CURRENT_VERSION,
        "_available_weapons": matching_weapons[:20],
        "_available_artifacts": artifact_list[:20],

        # TL;DR
        "tldr_weapon": f"Best Weapon (F2P: ...)",
        "tldr_artifact": f"4pc Best Set (MainStats)",
        "tldr_team": f"Best Team Name (members)",
        "tldr_key_stats": f"Stat1 threshold · Stat2 threshold · Priority",

        # Intro
        "intro": f"{char_name} is a ... (write one paragraph about role, element, weapon type, and place in current meta).",

        # Weapons
        "weapon_bottom_line": "One sentence weapon choice summary.",
        "weapons": [
            {"rank": 1, "name": "Signature Weapon", "rarity": 5, "atk": 0, "substat": "Stat Type 0%", "notes": "Why this weapon — be specific."},
            {"rank": 2, "name": "Best F2P Option", "rarity": 4, "atk": 0, "substat": "Stat Type 0%", "notes": "Why this is the best free option."},
            {"rank": 3, "name": "Strong Alternative", "rarity": 5, "atk": 0, "substat": "Stat Type 0%", "notes": "When to use this instead."},
        ],

        # Artifacts
        "best_artifact": "4pc Best Set Name",
        "artifact_why": "Why this set is optimal.",
        "artifact_alt": "4pc Alternative Set — when to use",
        "main_stats": {
            "sands": "Stat% / Stat%",
            "sands_note": "When to choose each.",
            "goblet": "Stat% or Stat%",
            "goblet_note": "Which is better and why.",
            "circlet": "Stat% / Stat%",
            "circlet_note": "Depends on weapon and substats.",
        },
        "sub_priority": [
            "1. Most Important Stat — target threshold",
            "2. Second Stat — reason",
            "3. Third Stat",
            "4. Fourth Stat",
        ],

        # Teams
        "teams": [
            {"name": "Team 1: Name", "members": "Char1 + Char2 + Char3 + Char4", "desc": "How it works and what content it excels at."},
            {"name": "Team 2: Name", "members": "Char1 + Char2 + Char3 + Char4", "desc": "How it works."},
            {"name": "Team 3: Name", "members": "Char1 + Char2 + Char3 + Char4", "desc": "How it works."},
        ],

        # Talents
        "talent_priority": [
            {"icon": "Q", "label": "Elemental Burst", "priority": "Priority 1"},
            {"icon": "E", "label": "Elemental Skill", "priority": "Priority 2"},
            {"icon": "NA", "label": "Normal Attack", "priority": "Priority 3"},
        ],

        # Rotation
        "rotation_title": "Recommended rotation:",
        "rotation_code": "Character E → Support Q → ...",
        "rotation_key": "Key tip about the rotation.",

        # Mistakes
        "mistakes": [
            "Common mistake 1 — what and why.",
            "Common mistake 2 — what and why.",
            "Common mistake 3 — what and why.",
            "Common mistake 4 (optional).",
        ],

        # Pro teaser
        "pro_teaser_code": f"// Sample DMG simulation for {char_name}\n// Fill in Pro tool data...",

        # Related guides
        "related_guides": [
            {"id": "raiden", "name": "Raiden Shogun", "element": "electro", "emoji": "⚡", "tier": "S", "desc": "Sub DPS · Emblem set · Engulfing Lightning"},
        ],

        # SEO
        "seo": {
            "title": f"{char_name} Build Guide — Best Weapons, Artifacts, Teams | GenshinGuide",
            "description": f"Complete {char_name} build guide for Genshin Impact v{config.CURRENT_VERSION}. Best weapons ranked, optimal artifacts, team compositions, rotation, and common mistakes.",
        },
    }

    return scaffold


# ---------------------------------------------------------------------------
# Render: produce HTML from a completed guide JSON
# ---------------------------------------------------------------------------

def render_guide(guide_data, character_id, char_data):
    """Render a guide JSON into HTML using the Jinja2 template."""
    element_css = guide_data.get("_element", "electro")
    color_hex = config.ELEMENT_COLORS.get(element_css, "#448aff")
    color_clean = color_hex.lstrip("#")
    r, g, b = int(color_clean[0:2], 16), int(color_clean[2:4], 16), int(color_clean[4:6], 16)

    template_vars = {
        "char_id": character_id,
        "prefix": character_id,
        "char_name": char_data.get("name", character_id.title()),
        "char_role": char_data.get("role", "Support"),
        "char_weapon_type": char_data.get("weapon_type", "Sword").title(),
        "char_role_desc": char_data.get("description", ""),
        "element": element_css,
        "element_display": ELEMENT_DISPLAY.get(element_css, element_css.title()),
        "element_emoji": ELEMENT_EMOJI.get(element_css, "✦"),
        "element_color_hex": color_hex,
        "element_color_rgb": f"{r},{g},{b}",
        "version": config.CURRENT_VERSION,
        "date_modified": date.today().isoformat(),

        "tldr_weapon": guide_data.get("tldr_weapon", ""),
        "tldr_artifact": guide_data.get("tldr_artifact", ""),
        "tldr_team": guide_data.get("tldr_team", ""),
        "tldr_key_stats": guide_data.get("tldr_key_stats", ""),
        "intro": guide_data.get("intro", ""),
        "weapon_bottom_line": guide_data.get("weapon_bottom_line", ""),
        "weapons": guide_data.get("weapons", []),
        "best_artifact": guide_data.get("best_artifact", ""),
        "artifact_why": guide_data.get("artifact_why", ""),
        "artifact_alt": guide_data.get("artifact_alt", ""),
        "main_stats": guide_data.get("main_stats", {}),
        "sub_priority": guide_data.get("sub_priority", []),
        "teams": guide_data.get("teams", []),
        "talent_priority": guide_data.get("talent_priority", []),
        "rotation_title": guide_data.get("rotation_title", ""),
        "rotation_code": guide_data.get("rotation_code", ""),
        "rotation_key": guide_data.get("rotation_key", ""),
        "mistakes": guide_data.get("mistakes", []),
        "pro_teaser_code": guide_data.get("pro_teaser_code", ""),
        "related_guides": guide_data.get("related_guides", []),
        "seo_title": guide_data.get("seo", {}).get("title", ""),
        "seo_description": guide_data.get("seo", {}).get("description", ""),
    }

    return _template.render(**template_vars)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate guide scaffold or render from JSON.")
    parser.add_argument("--character", type=str, required=True, help="Character ID")
    parser.add_argument("--scaffold", action="store_true", help="Create scaffold JSON for manual editing")
    parser.add_argument("--render", action="store_true", help="Render HTML from character JSON file")
    parser.add_argument("--translate", action="store_true", help="Auto-translate missing Chinese after render")
    parser.add_argument("--api-key", type=str, help="DeepSeek API key for translation")
    parser.add_argument("--data-dir", type=str, default="data/guides", help="Directory for guide JSON files")
    args = parser.parse_args()

    cid = args.character

    # Ensure data is cached
    char_data = sync_wiki.load_cache("characters", cid)
    if char_data is None:
        print(f"[INFO] Syncing {cid} data first...")
        sync_wiki.sync_characters(cid)
        char_data = sync_wiki.load_cache("characters", cid)
    if char_data is None:
        print(f"[ERROR] Cannot load data for {cid}")
        sys.exit(1)

    scaffold_dir = args.data_dir
    Path(scaffold_dir).mkdir(parents=True, exist_ok=True)
    json_path = os.path.join(scaffold_dir, f"{cid}.json")

    # Scaffold mode: create JSON for manual editing
    if args.scaffold:
        scaffold = build_scaffold(cid)
        if scaffold is None:
            sys.exit(1)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(scaffold, f, ensure_ascii=False, indent=2)
        print(f"[DONE] Scaffold written to {json_path}")
        print(f"  Edit this file to fill in the guide content.")
        print(f"  Then run: python generate.py --character {cid} --render")
        return

    # Render mode: produce HTML from completed JSON
    if args.render:
        if not os.path.exists(json_path):
            print(f"[ERROR] Guide JSON not found: {json_path}")
            print(f"  Run: python generate.py --character {cid} --scaffold")
            sys.exit(1)
        with open(json_path, "r", encoding="utf-8") as f:
            guide_data = json.load(f)

        # Verify first
        element_css = guide_data.get("_element", "electro")
        result = verify.verify_guide(guide_data, character_id=cid, expected_element=element_css)
        if not result.get("passed"):
            print("[WARN] Verification found issues. Fix them before publishing.")

        html = render_guide(guide_data, cid, char_data)
        output_path = os.path.join(config.OUTPUT_DIR, f"guide-{cid}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"[DONE] Guide rendered to {output_path} ({len(html)} bytes)")

        # Auto-translate if requested
        if args.translate:
            print(f"\n[TRANSLATE] Auto-translating missing Chinese for {cid}...")
            import translate as tr
            i18n_data = tr.load_i18n_json()
            extracted = tr.extract_guide_fields(guide_data, cid)
            missing = tr.find_missing_translations(extracted, i18n_data)
            if missing:
                print(f"  {len(missing)} keys need translation")
                texts = [(key, en_text) for key, en_text, _ in missing]
                translations = tr.call_deepseek_translate(texts, args.api_key)
                if translations:
                    i18n_data = tr.apply_translations(i18n_data, extracted, translations)
                    tr.save_i18n_json(i18n_data)
                    tr.build_i18n_js()
                    print(f"  ✅ Translated {len(translations)} strings and rebuilt i18n.js")
            else:
                print(f"  ✅ All translations complete!")
        return

    # Default: scaffold + render in one pass
    scaffold = build_scaffold(cid)
    if scaffold is None:
        sys.exit(1)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(scaffold, f, ensure_ascii=False, indent=2)
    print(f"[1/2] Scaffold: {json_path}")
    print(f"  ⚠️  This is a TEMPLATE — edit the JSON before publishing.")
    print(f"  Then run: python generate.py --character {cid} --render")


if __name__ == "__main__":
    main()
