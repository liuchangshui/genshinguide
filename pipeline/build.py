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
    # Track replacements to handle nested data-i18n carefully
    replacements = []

    # Find all elements with data-i18n and their key
    for m in re.finditer(r'(<[^>]*data-i18n="([^"]*)"[^>]*>)(.*?)(</[^>]+>)', html, re.DOTALL):
        full_tag_start = m.group(1)
        key = m.group(2)
        inner = m.group(3)
        close_tag = m.group(4)

        zh_text = resolve_key(i18n, key, "zh")
        if zh_text is None:
            continue

        # Build replacement: tag start (without data-i18n) + zh text + close tag
        clean_start = re.sub(r'\s*data-i18n="[^"]*"', '', full_tag_start)
        replacements.append((m.group(0), clean_start + zh_text + close_tag))

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
        f.write("""// GenshinGuide Language Switcher
(function(){
  var currentLang = document.documentElement.lang.startsWith('zh') ? 'zh' : 'en';

  function switchTo(lang) {
    localStorage.setItem('lang', lang);
    var path = location.pathname.replace(/\\/$/, '');
    if (path.startsWith('/en')) path = path.replace(/^\\/en/, '/zh');
    else if (path.startsWith('/zh')) path = path.replace(/^\\/zh/, '/en');
    else path = (lang === 'zh' ? '/zh' : '/en') + path;
    if (path === '/en' || path === '/zh') path += '/';
    location.href = path;
  }

  // DOM already loaded (script at end of body)
  document.querySelectorAll('.lang-toggle').forEach(function(btn){
    btn.addEventListener('click', function(){
      var lang = btn.dataset.lang;
      if (lang && lang !== currentLang) switchTo(lang);
    });
  });
})();
""")

    print(f"  ✅ Root redirect and lang-switcher.js generated")
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
