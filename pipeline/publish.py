"""
publish.py — Publish a generated guide after human review.

Usage:
    python publish.py --character furina

Actions:
    1. Update guides.html grid with the new/updated character card
    2. Update sitemap.xml
    3. Update js/i18n.js with new character-specific keys
    4. Extend js/calculator.js DATA object if possible
    5. Git commit + push (triggers Cloudflare Pages deployment)

IMPORTANT: Only run after human review approves the guide.
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import date

import config
import sync_wiki


def confirm(message: str) -> bool:
    """Ask for user confirmation."""
    answer = input(f"{message} [y/N] ").strip().lower()
    return answer in ("y", "yes")


def update_guides_index(character_id: str, char_name: str, element: str) -> None:
    """Add or update a character card in guides.html."""
    index_path = config.GUIDES_INDEX
    if not os.path.exists(index_path):
        print(f"[WARN] {index_path} not found, skipping.")
        return

    with open(index_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Check if a card already exists for this character
    marker = f'guide-{character_id}.html'
    if marker in content:
        print(f"[INFO] {character_id} already in guides.html, card will be updated on next render.")
        # For now, we rely on guides.html being manually maintained or
        # being fully regenerated from a Jinja2 template later.
        return

    # Insert new card before the closing </div> of #guide-cards
    new_card = f"""    <a href="guide-{character_id}.html" class="guide-card {element}" data-element="{element}" data-filter="{element}">
      <div class="guide-card-img {element}">
        <div class="elem-icon {element}">✦</div>
      </div>
      <div class="guide-card-body">
        <h4>{char_name} <span class="grade grade-s">S</span></h4>
        <p data-i18n="guides.{character_id}_desc">{char_name} build guide — best weapons, artifacts, and team compositions.</p>
      </div>
    </a>\n"""

    insert_marker = '<div class="guides-grid" id="guide-cards">'
    if insert_marker in content:
        # Insert after the opening div
        parts = content.split(insert_marker)
        content = parts[0] + insert_marker + "\n" + new_card + parts[1]
        with open(index_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"[OK] Added {character_id} to guides.html")
    else:
        print("[WARN] Could not find guide-cards div in guides.html.")


def update_sitemap(character_id: str) -> None:
    """Add the new guide URL to sitemap.xml if not already present."""
    sitemap_path = config.SITEMAP_FILE
    if not os.path.exists(sitemap_path):
        print(f"[WARN] {sitemap_path} not found.")
        return

    with open(sitemap_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    url_entry = f"guide-{character_id}.html"
    if url_entry in content:
        print(f"[INFO] {url_entry} already in sitemap.")
        return

    today = date.today().isoformat()
    new_entry = f"""  <url>
    <loc>https://bricklayer.tech/guide-{character_id}.html</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
"""

    insert_marker = "</urlset>"
    content = content.replace(insert_marker, new_entry + insert_marker)
    with open(sitemap_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"[OK] Added {character_id} to sitemap.xml")


def update_calculator_data(character_id: str, guide_data: dict) -> None:
    """Extend the calculator.js DATA object with the new character."""
    calc_path = config.CALCULATOR_FILE
    if not os.path.exists(calc_path):
        print(f"[WARN] {calc_path} not found.")
        return

    with open(calc_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Check if character already exists
    if f"'{character_id}':" in content or f'"{character_id}":' in content:
        print(f"[INFO] {character_id} already in calculator.js.")
        return

    # Extract relevant data for calculator
    weapons_list = [w.get("name", w.get("id", "")) for w in guide_data.get("weapons", [])[:4]]
    best_artifact = guide_data.get("best_artifact", "")
    main_stats = guide_data.get("main_stats", {})
    sub_priority = [s.split(". ")[-1] if ". " in s else s for s in guide_data.get("sub_priority", [])]
    teams = [
        {"n": t.get("name", ""), "m": t.get("members", ""), "d": t.get("desc", "")}
        for t in guide_data.get("teams", [])[:3]
    ]

    char_entry = f"""
  {character_id}: {{
    name:'{{char_name}}',
    element:'{{element}}',
    role:'{{role}}',
    atk:0,
    ascStat:'',
    ascVal:0,
    weapons:{json.dumps(weapons_list)},
    arti:'{best_artifact}',
    artiAlt:'',
    main:{{sands:'{main_stats.get("sands", "")}',goblet:'{main_stats.get("goblet", "")}',circlet:'{main_stats.get("circlet", "")}'}},
    subs:{json.dumps(sub_priority)},
    teams:{json.dumps(teams)}
  }},"""

    # Insert before the closing }; of the DATA object
    insert_marker = "};"  # end of DATA
    # Find the first }; after "const DATA = {"
    data_start = content.find("const DATA = {")
    data_end = content.find("};", data_start)
    if data_end > 0:
        content = content[:data_end] + char_entry + "\n" + content[data_end:]
        with open(calc_path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"[OK] Added {character_id} to calculator.js DATA (fill atk/ascStat manually).")
    else:
        print("[WARN] Could not insert into calculator.js.")


def git_commit_push(character_id: str) -> bool:
    """Commit and push changes."""
    try:
        subprocess.run(["git", "add", "pr-site/", "pipeline/data/"], check=True)
        msg = f"publish: {character_id} guide for v{config.CURRENT_VERSION}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print(f"[OK] Git commit + push: {msg}")
        return True
    except subprocess.CalledProcessError as exc:
        print(f"[WARN] Git operation failed: {exc}")
        print("  You may need to commit manually.")
        return False


def main():
    parser = argparse.ArgumentParser(description="Publish a generated guide after human review.")
    parser.add_argument("--character", type=str, required=True, help="Character ID to publish")
    parser.add_argument("--skip-git", action="store_true", help="Skip git commit + push")
    args = parser.parse_args()

    cid = args.character

    # Load character data
    char_data = sync_wiki.load_cache("characters", cid)
    if char_data is None:
        print(f"[ERROR] No cached data for {cid}. Run sync_wiki.py --character {cid} first.")
        sys.exit(1)

    char_name = char_data.get("name", cid.title())
    element_raw = char_data.get("element", "")
    element = config.ELEMENT_MAP.get(element_raw, "electro")

    # Check if guide HTML exists
    guide_path = os.path.join(config.OUTPUT_DIR, f"guide-{cid}.html")
    if not os.path.exists(guide_path):
        print(f"[ERROR] Guide file not found: {guide_path}")
        print("  Run generate.py --character {cid} first.")
        sys.exit(1)

    # Confirm human review
    print(f"\nPublishing guide for: {char_name} ({cid})")
    print(f"  Guide file: {guide_path}")
    print(f"  Element: {element}")
    if not confirm("\nHas this guide passed HUMAN REVIEW?"):
        print("Aborted.")
        return

    # Publish
    print("\n--- Publishing ---")
    update_guides_index(cid, char_name, element)
    update_sitemap(cid)

    if not args.skip_git:
        print("\n--- Committing ---")
        git_commit_push(cid)
    else:
        print("\n[Skipped] Git commit (--skip-git)")

    print(f"\n[DONE] {char_name} guide published!")


if __name__ == "__main__":
    main()
