"""
extract_guide.py — Extract guide content from hand-written HTML into JSON format.

Usage:
    python extract_guide.py --character arlecchino     # extract one
    python extract_guide.py --all                      # extract all hand-written guides
    python extract_guide.py --character arlecchino --render  # extract + render

Output: pipeline/data/guides/{character_id}.json
"""

import json
import os
import re
import sys
import argparse
from pathlib import Path

import config


def extract_guide(html_path: str, character_id: str):
    """Extract guide content from HTML into JSON dict."""
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Remove script/style tags for clean text extraction
    clean = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)

    result = {
        "_character_id": character_id,
        "_game_version": config.CURRENT_VERSION,
    }

    # --- SEO ---
    seo_title = _extract_first(html, r'<title>(.*?)</title>')
    seo_desc = _extract_first(html, r'<meta name="description" content="(.*?)"')
    result["seo"] = {
        "title": seo_title or f"{character_id.title()} Build Guide — GenshinGuide",
        "description": seo_desc or f"Complete {character_id.title()} build guide for Genshin Impact v{config.CURRENT_VERSION}.",
    }

    # --- Element ---
    element = "pyro"
    for el in ["electro", "pyro", "hydro", "dendro", "anemo", "geo", "cryo"]:
        if f'class="character-showcase {el}"' in html or f"class='character-showcase {el}'" in html:
            element = el
            break
    result["_element"] = element

    # --- TL;DR ---
    tldr_values = re.findall(r'<div class="tldr-value">(.*?)</div>', clean, re.DOTALL)
    if len(tldr_values) >= 4:
        result["tldr_weapon"] = _clean_html(tldr_values[0])
        result["tldr_artifact"] = _clean_html(tldr_values[1])
        result["tldr_team"] = _clean_html(tldr_values[2])
        result["tldr_key_stats"] = _clean_html(tldr_values[3])

    # --- Weapon type & role ---
    char_meta = re.findall(r'<div class="char-meta">(.*?)</div>', clean, re.DOTALL)
    if char_meta:
        meta_text = char_meta[0]
        weapon_match = re.search(r'([🔱⚔️🏹📖🗡️])\s*(\w+)', meta_text)
        result["_weapon_type"] = weapon_match.group(2).lower() if weapon_match else "sword"

    # --- Intro paragraph ---
    intro_match = re.search(r'data-i18n="[^"]*\.intro">(.*?)</p>', clean, re.DOTALL)
    if intro_match:
        result["intro"] = _clean_html(intro_match.group(1))
    else:
        # Try any <p> after TL;DR
        tldr_end = clean.find('</div>\n  </div>\n\n  <p')
        if tldr_end == -1:
            tldr_end = clean.find('tldr-box')
        para = re.search(r'<p[^>]*>(.{50,500}?)</p>', clean[tldr_end:], re.DOTALL)
        if para:
            result["intro"] = _clean_html(para.group(1))

    # --- Weapon section ---
    # Bottom line
    bl_match = re.search(r'<strong>Bottom line:</strong>\s*(.*?)\s*</div>', clean, re.DOTALL)
    if bl_match:
        result["weapon_bottom_line"] = _clean_html(bl_match.group(1))

    # Weapon table rows
    weapon_rows = re.findall(r'<tr>(.*?)</tr>', _extract_section(clean, 'weapon-table'), re.DOTALL)
    weapons = []
    for row in weapon_rows:
        if '<th' in row:
            continue  # skip header
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        if len(cells) >= 6:
            rank_text = _clean_html(cells[0])
            try:
                rank = int(rank_text)
            except ValueError:
                continue
            weapons.append({
                "rank": rank,
                "name": _clean_html(cells[1]),
                "rarity": cells[2].count('⭐'),
                "atk": int(re.search(r'\d+', _clean_html(cells[3])).group()) if re.search(r'\d+', _clean_html(cells[3])) else 0,
                "substat": _clean_html(cells[4]),
                "notes": _clean_html(cells[5]),
            })
    if weapons:
        result["weapons"] = sorted(weapons, key=lambda w: w["rank"])

    # --- Artifacts ---
    arti_section = _extract_section_between(clean, r'2\.\s*Best Artifact', r'3\.\s*Best Team')
    if not arti_section:
        arti_section = _extract_section_between(clean, r'sec_artifacts', r'sec_teams')

    best_match = re.search(r'Best:\s*(.*?)</div>', arti_section, re.DOTALL) if arti_section else None
    if best_match:
        result["best_artifact"] = _clean_html(best_match.group(1))
    else:
        # Try emphasis box
        emb = re.findall(r'<div class="emphasis-box[^"]*">(.*?)</div>', arti_section or clean, re.DOTALL)
        if emb:
            best_text = re.search(r'Best:\s*(.{10,80})', emb[0], re.DOTALL)
            if best_text:
                result["best_artifact"] = _clean_html(best_text.group(1))

    why_match = re.search(r'data-i18n="[^"]*\.arti_why">(.*?)</p>', arti_section or clean, re.DOTALL)
    if why_match:
        result["artifact_why"] = _clean_html(why_match.group(1))

    alt_match = re.search(r'Alternative:?\s*(.*?)(?:</div>|</p>)', arti_section or clean, re.DOTALL)
    if alt_match:
        result["artifact_alt"] = _clean_html(alt_match.group(1))

    # --- Main Stats ---
    main_stats_section = _extract_section_between(clean, r'Main Stats', r'Sub-stat')
    stat_rows = re.findall(r'<tr>(.*?)</tr>', main_stats_section, re.DOTALL) if main_stats_section else []
    main_stats = {}
    for row in stat_rows:
        if '<th' in row:
            continue
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL)
        if len(cells) >= 3:
            slot_label = _clean_html(cells[0]).lower()
            stat_value = _clean_html(cells[1])
            note = _clean_html(cells[2])
            if 'sand' in slot_label:
                main_stats["sands"] = stat_value
                main_stats["sands_note"] = note
            elif 'goblet' in slot_label:
                main_stats["goblet"] = stat_value
                main_stats["goblet_note"] = note
            elif 'circlet' in slot_label:
                main_stats["circlet"] = stat_value
                main_stats["circlet_note"] = note
    if main_stats:
        result["main_stats"] = main_stats

    # --- Substat Priority ---
    sub_section = _extract_section_between(clean, r'Sub-stat Priority', r'(?:3\.\s*Best Team|sec_teams)')
    sub_items = re.findall(r'<li[^>]*>(.*?)</li>', sub_section or clean, re.DOTALL)
    if sub_items:
        result["sub_priority"] = [_clean_html(s) for s in sub_items]

    # --- Teams ---
    teams_section = _extract_section_between(clean, r'3\.\s*Best Team', r'4\.\s*Talent')
    if not teams_section:
        teams_section = _extract_section_between(clean, r'sec_teams', r'sec_talent')
    team_boxes = re.findall(r'<div class="emphasis-box[^"]*">(.*?)</div>', teams_section or clean, re.DOTALL)
    teams = []
    for box in team_boxes:
        name_match = re.search(r'<strong[^>]*>(.*?)</strong>', box, re.DOTALL)
        if not name_match:
            continue
        name = _clean_html(name_match.group(1))
        if not name.startswith('Team'):
            continue
        # Get the description (everything after <br>)
        desc_parts = box.split('<br>')
        if len(desc_parts) >= 2:
            desc = _clean_html(''.join(desc_parts[1:]))
        else:
            desc = _clean_html(re.sub(r'<strong[^>]*>.*?</strong>', '', box))
        # Extract members from the members span
        members_match = re.search(r'👥\s*(.*?)(?:<br>|</span>)', box, re.DOTALL)
        members = _clean_html(members_match.group(1)) if members_match else ""
        teams.append({
            "name": name,
            "members": members or _extract_members(desc),
            "desc": desc,
        })
    if teams:
        result["teams"] = teams

    # --- Talent Priority ---
    talent_section = _extract_section_between(clean, r'4\.\s*Talent', r'5\.\s*Rotation')
    if not talent_section:
        talent_section = _extract_section_between(clean, r'sec_talent', r'sec_rotation')
    # Find talent icons, labels, and priorities as separate lists
    talent_icons = re.findall(r'<div class="talent-icon"[^>]*>(\w+)</div>', talent_section or clean)
    talent_labels = re.findall(r'<div class="talent-label"[^>]*>(.*?)</div>', talent_section or clean, re.DOTALL)
    talent_priorities = re.findall(r'<div class="talent-priority[^>]*>(.*?)</div>', talent_section or clean, re.DOTALL)
    talents = []
    for i in range(min(len(talent_icons), len(talent_labels), len(talent_priorities))):
        talents.append({
            "icon": talent_icons[i],
            "label": _clean_html(talent_labels[i]),
            "priority": _clean_html(talent_priorities[i]),
        })
    if talents:
        result["talent_priority"] = talents

    # --- Rotation ---
    rot_section = _extract_section_between(clean, r'5\.\s*Rotation', r'6\.\s*Common')
    if not rot_section:
        rot_section = _extract_section_between(clean, r'sec_rotation', r'sec_mistakes')
    rot_title_match = re.search(r'data-i18n="[^"]*\.rotation_title">(.*?)</div>', rot_section or clean, re.DOTALL)
    if rot_title_match:
        result["rotation_title"] = _clean_html(rot_title_match.group(1))
    else:
        result["rotation_title"] = "Recommended rotation:"

    rot_code_match = re.search(r'<code[^>]*>(.*?)</code>', rot_section or clean, re.DOTALL)
    if rot_code_match:
        result["rotation_code"] = _clean_html(rot_code_match.group(1))
    else:
        result["rotation_code"] = ""

    rot_key_match = re.search(r'data-i18n="[^"]*\.rotation_key">(.*?)</p>', rot_section or clean, re.DOTALL)
    if rot_key_match:
        result["rotation_key"] = _clean_html(rot_key_match.group(1))
    else:
        # Try any <p> after rotation code
        if rot_code_match:
            after_code = clean[rot_code_match.end():rot_code_match.end()+500]
            key_para = re.search(r'<p[^>]*>(⚠️.*?)</p>', after_code, re.DOTALL)
            if key_para:
                result["rotation_key"] = _clean_html(key_para.group(1))

    # --- Mistakes ---
    mistakes_section = _extract_section_between(clean, r'6\.\s*Common Mistake', r'(?:<hr|Pro Deep|related-guides)')
    if not mistakes_section:
        mistakes_section = _extract_section_between(clean, r'sec_mistakes', r'(?:<hr|pro-teaser|pro_teaser|related-guides)')
    mistake_items = re.findall(r'<p[^>]*>(❌.*?)</p>', mistakes_section or clean, re.DOTALL)
    if mistake_items:
        result["mistakes"] = [_clean_html(m) for m in mistake_items]

    # --- Related Guides ---
    related_section = _extract_section_between(clean, r'related-guides', r'</article>')
    related_cards = re.findall(r'<a href="guide-(\w+)\.html"[^>]*>(.*?)</a>', related_section or clean, re.DOTALL)
    related = []
    for rid, card_html in related_cards:
        name_match = re.search(r'<h4[^>]*>(.*?)<span', card_html, re.DOTALL)
        name = _clean_html(name_match.group(1)) if name_match else rid.title()
        desc_match = re.search(r'<p[^>]*>(.*?)</p>', card_html, re.DOTALL)
        desc = _clean_html(desc_match.group(1)) if desc_match else ""
        # Determine element from class
        el_match = re.search(r'guide-card\s+(\w+)', card_html)
        rel_element = el_match.group(1) if el_match else "electro"
        tier_match = re.search(r'grade-(\w)', card_html)
        tier = tier_match.group(1).upper() if tier_match else "S"
        emoji_map = {"electro":"⚡","pyro":"🔥","hydro":"💧","dendro":"🌿","anemo":"🍃","geo":"🪨","cryo":"❄️"}
        related.append({
            "id": rid,
            "name": name,
            "element": rel_element,
            "emoji": emoji_map.get(rel_element, "✦"),
            "tier": tier,
            "desc": desc,
        })
    if related:
        result["related_guides"] = related

    # --- Pro Teaser ---
    pro_section = _extract_section_between(clean, r'pro-teaser', r'related-guides')
    pro_code_match = re.search(r'<pre><code>(.*?)</code></pre>', pro_section or clean, re.DOTALL)
    if pro_code_match:
        result["pro_teaser_code"] = _clean_html(pro_code_match.group(1))
    else:
        result["pro_teaser_code"] = "// Pro DMG simulation — unlock for full data"

    return result


def _extract_first(text, pattern):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


def _extract_section(text, class_name):
    """Extract content between a table/div with class_name."""
    m = re.search(rf'<[^>]+class="[^"]*{class_name}[^"]*"[^>]*>(.*?)</(?:table|div)>', text, re.DOTALL)
    return m.group(1) if m else ""


def _extract_section_between(text, start_pattern, end_pattern):
    """Extract content between two regex patterns."""
    start = re.search(start_pattern, text)
    if not start:
        return ""
    end = re.search(end_pattern, text[start.end():])
    if not end:
        return text[start.end():]
    return text[start.end():start.end() + end.start()]


def _clean_html(html_text):
    """Strip HTML tags and clean whitespace."""
    text = re.sub(r'<[^>]+>', ' ', html_text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Decode HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    return text


def _extract_members(text):
    """Try to extract team member names from description."""
    # Look for patterns like "Char1 + Char2 + Char3 + Char4"
    m = re.search(r'([A-Z][a-z]+\s*(?:\+\s*[A-Z][a-z]+)+)', text)
    return m.group(1) if m else ""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Extract guide JSON from hand-written HTML")
    ap.add_argument("--character", type=str, help="Character ID")
    ap.add_argument("--all", action="store_true", help="Extract all hand-written guides")
    ap.add_argument("--render", action="store_true", help="Also render after extraction")
    args = ap.parse_args()

    # Hand-written characters (these have HTML but no JSON yet)
    hand_written = [
        "arlecchino", "furina", "neuvillette", "raiden",
        "hutao", "yelan", "ayaka", "zhongli", "albedo", "xiangling",
    ]

    characters = []
    if args.all:
        characters = hand_written
    elif args.character:
        if args.character in hand_written:
            characters = [args.character]
        else:
            print(f"[WARN] {args.character} might already have JSON — extracting anyway")
            characters = [args.character]
    else:
        print("[ERROR] Use --character <id> or --all")
        sys.exit(1)

    output_dir = os.path.join(os.path.dirname(__file__), "data", "guides")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    for cid in characters:
        html_path = os.path.join(config.OUTPUT_DIR, f"guide-{cid}.html")
        if not os.path.exists(html_path):
            print(f"  [SKIP] {html_path} not found")
            continue

        print(f"\n[{cid}] Extracting from {html_path}...")
        guide_data = extract_guide(html_path, cid)

        json_path = os.path.join(output_dir, f"{cid}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(guide_data, f, ensure_ascii=False, indent=2)
        print(f"  ✅ Written to {json_path}")

        # Show summary
        sections = [k for k in guide_data if not k.startswith("_")]
        print(f"  Sections: {', '.join(sections)}")
        print(f"  Weapons: {len(guide_data.get('weapons', []))}")
        print(f"  Teams: {len(guide_data.get('teams', []))}")
        print(f"  Mistakes: {len(guide_data.get('mistakes', []))}")

        # Render if requested
        if args.render:
            import generate
            import sync_wiki
            cdata = sync_wiki.load_cache("characters", cid)
            if cdata is None:
                sync_wiki.sync_characters(cid)
                cdata = sync_wiki.load_cache("characters", cid)
            if cdata:
                html = generate.render_guide(guide_data, cid, cdata)
                out = os.path.join(config.OUTPUT_DIR, f"guide-{cid}.html")
                with open(out, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"  ✅ Rendered to {out} ({len(html)} bytes)")
            else:
                print(f"  ⚠️  No character data for {cid}, skipping render")


if __name__ == "__main__":
    main()
