"""
build.py — Build-time i18n: generate en/ and zh/ static HTML from data-i18n templates.

Usage:
    python build.py          # Full build
    python build.py --dry-run # Preview only

Flow:
    1. Render guide pages once (English, with data-i18n)
    2. Localize each page: en (keep English, strip data-i18n) + zh (inject Chinese, strip data-i18n)
    3. Copy shared assets (css, js, images)
    4. Generate root index.html (language redirect)
    5. Generate language switcher JS
"""

import json
import os
import re
import shutil
import sys
import argparse
from pathlib import Path

import config

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "pr-site")
EN_DIR = os.path.join(OUTPUT_DIR, "en")
ZH_DIR = os.path.join(OUTPUT_DIR, "zh")
I18N_JSON = os.path.join(os.path.dirname(__file__), "data", "i18n.json")

SHARED_DIRS = ["css", "js", "images"]


# ---------------------------------------------------------------------------
# i18n resolution
# ---------------------------------------------------------------------------

def load_i18n():
    with open(I18N_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_key(i18n, key, lang):
    """Walk i18n dict tree to resolve a dotted key to its translation."""
    parts = key.split(".")
    obj = i18n
    for part in parts:
        if isinstance(obj, dict) and part in obj:
            obj = obj[part]
        else:
            return None
    if isinstance(obj, dict):
        return obj.get(lang) or obj.get("en", "")
    return str(obj) if obj else None


def _find_matching_close(html, tag_start_pos, tag_name):
    """Find end position (exclusive) of matching </tag_name> for <tag_name> at tag_start_pos.
    Handles nested same-name tags (e.g. div inside div). Returns -1 if not found."""
    open_marker = f'<{tag_name}'
    close_marker = f'</{tag_name}>'

    depth = 1
    pos = html.find('>', tag_start_pos) + 1  # skip past the opening '>'
    while depth > 0 and pos < len(html):
        next_open = html.find(open_marker, pos)
        next_close = html.find(close_marker, pos)

        if next_close == -1:
            return -1

        # Check if <tag_name appears before </tag_name> (nested same tag)
        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + len(open_marker)
        else:
            depth -= 1
            if depth == 0:
                return next_close + len(close_marker)
            pos = next_close + len(close_marker)

    return -1


def localize_html(html, i18n, lang):
    """
    Convert HTML with data-i18n attributes to fully localized HTML.
    - Replaces element content with translation
    - Removes data-i18n and data-i18n-placeholder attributes
    - Updates <html lang="...">
    """
    if lang == "en":
        # For English: strip data-i18n, keep content, set EN button active
        html = re.sub(r'\s*data-i18n="[^"]*"', '', html)
        html = re.sub(r'\s*data-i18n-placeholder="[^"]*"', '', html)
        html = html.replace('<html lang="en">', '<html lang="en">')
        html = html.replace(
            '<button class="lang-toggle" data-lang="en">EN</button>',
            '<button class="lang-toggle active" data-lang="en">EN</button>'
        )
        return html

    # For Chinese: replace content with zh translations
    replacements = []

    # Find all elements with data-i18n attribute.  Match only the opening tag
    # first, then use depth-tracking to find the real matching close tag.
    for m in re.finditer(r'<(\w+)([^>]*\sdata-i18n="([^"]*)"[^>]*)>', html):
        tag_name = m.group(1)
        key = m.group(3)
        full_tag_start = m.group(0)

        zh_text = resolve_key(i18n, key, "zh")
        if zh_text is None:
            continue

        # Find matching closing tag (handles nested tags like <span> inside <div>)
        close_end = _find_matching_close(html, m.start(), tag_name)
        if close_end == -1:
            continue

        full_element = html[m.start():close_end]

        # Build replacement: clean start tag + zh text + close tag
        clean_start = re.sub(r'\s*data-i18n="[^"]*"', '', full_tag_start)
        new_element = clean_start + zh_text + f'</{tag_name}>'

        replacements.append((full_element, new_element))

    # Apply replacements (longest first to avoid partial matches)
    replacements.sort(key=lambda x: -len(x[0]))
    for old, new in replacements:
        html = html.replace(old, new)

    # Handle data-i18n-placeholder for inputs
    for m in re.finditer(r'<input[^>]*data-i18n-placeholder="([^"]*)"[^>]*>', html):
        key = m.group(1)
        zh_text = resolve_key(i18n, key, "zh")
        if zh_text:
            old_tag = m.group(0)
            new_tag = re.sub(r'\s*data-i18n-placeholder="[^"]*"', '', old_tag)
            new_tag = new_tag.replace('placeholder="', f'placeholder="{zh_text}"')
            html = html.replace(old_tag, new_tag)

    # Swap lang-toggle active state
    html = html.replace('class="lang-toggle" data-lang="en">EN</button>',
                        'class="lang-toggle" data-lang="en">EN</button>')
    html = html.replace('class="lang-toggle" data-lang="zh">中</button>',
                        'class="lang-toggle active" data-lang="zh">中</button>')

    # Update lang attribute
    html = html.replace('<html lang="en">', '<html lang="zh-CN">')

    # Remove any remaining data-i18n attributes (e.g., on elements that didn't match)
    html = re.sub(r'\s*data-i18n="[^"]*"', '', html)
    html = re.sub(r'\s*data-i18n-placeholder="[^"]*"', '', html)

    # Update meta description if possible
    for key in ["home.desc", "guides.desc", "calc.desc"]:
        desc_zh = resolve_key(i18n, key, "zh")
        if desc_zh:
            # Replace in meta description
            html = re.sub(
                r'<meta name="description" content="[^"]*">',
                f'<meta name="description" content="{desc_zh}">',
                html,
                count=1
            )

    return html


# ---------------------------------------------------------------------------
# Guide rendering
# ---------------------------------------------------------------------------

def render_guides():
    """Render all guide pages using generate.py as subprocess."""
    import subprocess as _sp
    pipeline_dir = os.path.dirname(os.path.abspath(__file__))

    guide_dir = os.path.join(pipeline_dir, "data", "guides")
    guides = [f[:-5] for f in os.listdir(guide_dir) if f.endswith(".json")]

    for cid in guides:
        result = _sp.run(
            ["python3", "generate.py", "--character", cid, "--render"],
            capture_output=True, text=True, cwd=pipeline_dir, timeout=60
        )
        if result.returncode == 0:
            print(f"  ✅ guide-{cid}.html")
        else:
            err = result.stderr.strip()[:150]
            print(f"  ❌ guide-{cid}.html: {err}")
            # Clean up stale file so it doesn't pollute localization
            stale = os.path.join(OUTPUT_DIR, f"guide-{cid}.html")
            if os.path.exists(stale):
                os.remove(stale)
                print(f"     Removed stale {stale}")


# ---------------------------------------------------------------------------
# Static page processing
# ---------------------------------------------------------------------------

STATIC_PAGES = [
    "index.html", "guides.html", "calculator.html", "pricing.html",
    "about.html", "privacy.html", "pipeline.html",
]


def process_static_pages(i18n):
    """Ensure all static pages exist at pr-site root (with data-i18n)."""
    for page in STATIC_PAGES:
        path = os.path.join(OUTPUT_DIR, page)
        if not os.path.exists(path):
            print(f"  ⚠️  {page} not found, skipping")
        else:
            print(f"  ✓ {page} ready for localization")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def generate_calc_i18n(i18n):
    """Generate calc-i18n.js from i18n.json — character/weapon/artifact/team translations."""
    calc = {}

    # Character names
    char_ids = ['raiden','hutao','yelan','nahida','kazuha','zhongli','furina','arlecchino',
                'neuvillette','bennett','xiangling','ayaka','albedo','ganyu','xiao']
    for cid in char_ids:
        if cid in i18n and 'name' in i18n[cid]:
            calc[i18n[cid]['name']['en']] = i18n[cid]['name']['zh']

    # Weapon names
    for key, val in i18n.get('wpn', {}).items():
        calc[val['en']] = val['zh']

    # Artifact names
    for key, val in i18n.get('arti_names', {}).items():
        calc[val['en']] = val['zh']

    # Character roles
    for en, zh in {
        'Sub DPS / Battery': '副C / 充能辅助', 'Main DPS': '主C', 'Sub DPS / Support': '副C / 辅助',
        'Sub DPS / Buffer': '副C / 增伤辅助', 'Support / CC': '辅助 / 聚怪',
        'Shield / Support': '护盾 / 辅助', 'Support / Healer': '辅助 / 治疗', 'Sub DPS': '副C',
    }.items():
        calc[en] = zh

    # Team names from i18n character sections
    for cid in char_ids:
        if cid not in i18n:
            continue
        for i in range(1, 6):
            for suffix in ['_name', '_desc']:
                key = f'team{i}{suffix}'
                if key in i18n[cid]:
                    calc[i18n[cid][key]['en']] = i18n[cid][key]['zh']

    # Write JS file
    entries = []
    for en, zh in sorted(calc.items()):
        en_safe = en.replace('\\', '\\\\').replace("'", "\\'")
        zh_safe = zh.replace('\\', '\\\\').replace("'", "\\'")
        entries.append(f"  '{en_safe}': ['{en_safe}', '{zh_safe}']")

    out_path = os.path.join(OUTPUT_DIR, "js", "calc-i18n.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("// Auto-generated by build.py — do not edit\nvar CALC_I18N = {\n")
        f.write(",\n".join(entries))
        f.write("\n};\n")

    return len(entries)


def build():
    """Main build function."""
    i18n = load_i18n()
    print(f"[1/5] Loaded i18n: {len(i18n)} sections")

    # Create output dirs
    os.makedirs(EN_DIR, exist_ok=True)
    os.makedirs(ZH_DIR, exist_ok=True)
    print(f"[2/5] Created en/ and zh/ directories")

    # Render guides
    print(f"[3/5] Rendering guides...")
    # Clean all stale guide files first (prevents old CSS paths and wrong active states)
    for f in Path(OUTPUT_DIR).glob("guide-*.html"):
        f.unlink()
    render_guides()
    process_static_pages(i18n)

    # Localize all pages - read source content FIRST before overwriting
    print(f"[4/5] Localizing pages...")
    # Restore homepage from template (pr-site/index.html is the redirect from last build)
    home_template = os.path.join(os.path.dirname(__file__), "templates", "home.html")
    home_dest = os.path.join(OUTPUT_DIR, "index.html")
    if os.path.exists(home_template):
        shutil.copy(home_template, home_dest)
        print(f"  Restored homepage from template")

    all_source_html = list(Path(OUTPUT_DIR).glob("*.html"))

    # Save source content in memory (we'll overwrite index.html later)
    source_cache = {}
    for html_path in all_source_html:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "data-i18n" in content:
            source_cache[html_path.name] = content

    en_count = 0
    zh_count = 0

    for filename, html in source_cache.items():
        # EN version: strip data-i18n, keep English
        en_html = localize_html(html, i18n, "en")
        en_out = os.path.join(EN_DIR, filename)
        with open(en_out, "w", encoding="utf-8") as f:
            f.write(en_html)
        en_count += 1

        # ZH version: replace with translations
        zh_html = localize_html(html, i18n, "zh")
        zh_out = os.path.join(ZH_DIR, filename)
        with open(zh_out, "w", encoding="utf-8") as f:
            f.write(zh_html)
        zh_count += 1

    print(f"  ✅ {en_count} en pages, {zh_count} zh pages")

    # Generate root index.html (language redirect) — AFTER localization
    print(f"[5/5] Generating root redirect and language switcher...")
    root_index = os.path.join(OUTPUT_DIR, "index.html")
    with open(root_index, "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="google-adsense-account" content="ca-pub-8260551090770188">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GenshinGuide</title>
<script>
(function(){
  var lang = (navigator.language || 'en').toLowerCase();
  var saved = localStorage.getItem('lang');
  if (saved) lang = saved;
  var target = lang.startsWith('zh') ? '/zh/' : '/en/';
  window.location.replace(target);
})();
</script>
</head>
<body>
<p><a href="/en/">English</a> | <a href="/zh/">中文</a></p>
</body>
</html>""")

    # Generate language switcher JS
    switcher_js = os.path.join(OUTPUT_DIR, "js", "lang-switcher.js")
    os.makedirs(os.path.dirname(switcher_js), exist_ok=True)
    with open(switcher_js, "w", encoding="utf-8") as f:
        f.write("""// GenshinGuide Language Switcher + minimal i18n
(function(){
  var currentLang = document.documentElement.lang.startsWith('zh') ? 'zh' : 'en';
  var zh = currentLang === 'zh';

  function switchTo(lang) {
    localStorage.setItem('lang', lang);
    var path = location.pathname.replace(/\\/$/, '');
    if (path.startsWith('/en')) path = path.replace(/^\\/en/, '/zh');
    else if (path.startsWith('/zh')) path = path.replace(/^\\/zh/, '/en');
    else path = (lang === 'zh' ? '/zh' : '/en') + path;
    if (path === '/en' || path === '/zh') path += '/';
    location.href = path;
  }

  document.querySelectorAll('.lang-toggle').forEach(function(btn){
    btn.addEventListener('click', function(){
      var lang = btn.dataset.lang;
      if (lang && lang !== currentLang) switchTo(lang);
    });
  });

  // Minimal t() polyfill — replaces 162KB i18n.js
  var DICT = {
    'calcJS.sands_label':         [ 'Sands', '\\u65f6\\u4e4b\\u6c99' ],
    'calcJS.goblet_label':        [ 'Goblet', '\\u7a7a\\u4e4b\\u676f' ],
    'calcJS.circlet_label':       [ 'Circlet', '\\u7406\\u4e4b\\u51a0' ],
    'calcJS.build_summary':       [ 'Build Summary', 'Build\\u603b\\u7ed3' ],
    'calcJS.build_grade':         [ 'Build Grade', 'Build\\u8bc4\\u7ea7' ],
    'calcJS.optimal_meta':        [ 'Optimal \\u2014 Meta choice', '\\u6700\\u4f18 \\u2014 \\u7248\\u672c\\u7b54\\u6848' ],
    'calcJS.strong_viable':       [ 'Strong \\u2014 Viable in all content', '\\u5f3a\\u529b \\u2014 \\u5168\\u5185\\u5bb9\\u53ef\\u7528' ],
    'calcJS.functional_budget':   [ 'Functional \\u2014 Budget build', '\\u53ef\\u7528 \\u2014 \\u5e73\\u6c11\\u914d\\u88c5' ],
    'calcJS.best_arti':           [ 'Best Artifact Set', '\\u6700\\u4f73\\u5723\\u9057\\u7269' ],
    'calcJS.total_atk':           [ 'Total ATK', '\\u603b\\u653b\\u51fb\\u529b' ],
    'calcJS.char_atk':            [ 'char', '\\u89d2\\u8272' ],
    'calcJS.weapon_atk':          [ 'wpn', '\\u6b66\\u5668' ],
    'calcJS.wpn_substat':         [ 'Weapon Sub-stat', '\\u6b66\\u5668\\u526f\\u8bcd\\u6761' ],
    'calcJS.main_priority':       [ 'Main Stats Priority', '\\u4e3b\\u8bcd\\u6761\\u4f18\\u5148\\u7ea7' ],
    'calcJS.sub_priority':        [ 'Sub-stat Priority', '\\u526f\\u8bcd\\u6761\\u4f18\\u5148\\u7ea7' ],
    'calcJS.best_teams':          [ 'Best Teams', '\\u6700\\u4f73\\u914d\\u961f' ],
    'home.calc_wpn_placeholder':  [ '\\u2014 Select Weapon \\u2014', '\\u2014 \\u9009\\u62e9\\u6b66\\u5668 \\u2014' ],
    'home.calc_hint':             [ '\\u261b Select a character to see build recommendations', '\\u261b \\u9009\\u62e9\\u89d2\\u8272\\u67e5\\u770bBuild\\u63a8\\u8350' ],
    'home.calc_placeholder':      [ '\\u2014 Select Character \\u2014', '\\u2014 \\u9009\\u62e9\\u89d2\\u8272 \\u2014' ],
    'guide.pro_lock_desc':        [ 'Unlock full damage simulation and build optimization.', '\\u89e3\\u9501\\u5b8c\\u6574\\u4f24\\u5bb3\\u6a21\\u62df\\u4e0eBuild\\u4f18\\u5316\\u3002' ],
    'guide.pro_lock_btn':         [ 'Unlock Pro \\u2014 $5/month', '\\u5f00\\u901aPro \\u2014 $5/\\u6708' ],
    'pricing.checkout_soon':      [ 'Pro checkout coming soon \\u2014 thank you for your interest!', 'Pro\\u652f\\u4ed8\\u5373\\u5c06\\u4e0a\\u7ebf\\uff0c\\u611f\\u8c22\\u5173\\u6ce8\\uff01' ],
  };
  window.t = function(key){
    var entry = DICT[key];
    if (entry) return entry[zh ? 1 : 0];
    if (typeof CALC_I18N !== 'undefined') {
      entry = CALC_I18N[key];
      if (entry) return entry[zh ? 1 : 0];
    }
    return key;
  };
})();
""")

    # Generate calculator i18n data
    n_calc = generate_calc_i18n(i18n)
    print(f"  ✅ Root redirect, lang-switcher.js, calc-i18n.js ({n_calc} entries) generated")
    print(f"\n🎉 Build complete!")
    print(f"   en/: {en_count} pages")
    print(f"   zh/: {zh_count} pages")


def main():
    ap = argparse.ArgumentParser(description="Build-time i18n static site generator")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing")
    args = ap.parse_args()

    if args.dry_run:
        print("Dry run — checking what would be built...")
        guides = [f[:-5] for f in os.listdir(os.path.join(os.path.dirname(__file__), "data", "guides")) if f.endswith(".json")]
        print(f"  Guides: {len(guides)} characters")
        print(f"  Static: {len(STATIC_PAGES)} pages")
        print(f"  Output: {len(guides) + len(STATIC_PAGES)} pages × 2 languages = {2*(len(guides)+len(STATIC_PAGES))} files")
        return

    build()


if __name__ == "__main__":
    main()
