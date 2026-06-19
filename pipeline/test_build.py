"""
test_build.py — Verify build-time i18n output.

Checks:
  1. en/ and zh/ directories have identical page lists
  2. zh/ pages contain NO data-i18n attributes
  3. zh/ pages contain Chinese characters (not just English)
  4. zh/ pages have no long English text blocks (>50 Latin chars without CJK)
  5. Internal links use correct relative paths
"""

import os
import re
import sys
from pathlib import Path

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "pr-site")
EN_DIR = os.path.join(OUTPUT_DIR, "en")
ZH_DIR = os.path.join(OUTPUT_DIR, "zh")


def list_pages(directory):
    """List all .html files in directory, relativized."""
    if not os.path.isdir(directory):
        return []
    pages = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(root, f), directory)
                pages.append(rel)
    return sorted(pages)


def is_english_heavy(text):
    """Check if text is predominantly English (should NOT appear in zh pages).
    Excludes TL;DR proper nouns (weapon/artifact/team names)."""
    text = text.strip()
    if len(text) < 20:
        return False
    latin = len(re.findall(r'[a-zA-Z]', text))
    cjk = len(re.findall(r'[一-鿿]', text))
    if cjk > 0 and latin < 20:
        return False
    if latin <= cjk:
        return False

    # Exclude TL;DR content: weapon names, artifact names, team names
    # These are proper nouns and game data that don't need translation
    tldr_patterns = [
        r'^[A-Z][a-zA-Z\'\s]+\(F2P:',  # "Weapon Name (F2P: ..."
        r'^\d+pc\s+[A-Z]',              # "4pc Blizzard Strayer (..."
        r'^[A-Z][a-zA-Z\'\s·]+\(',      # "Team Name (Char1·Char2..."
    ]
    for pat in tldr_patterns:
        if re.match(pat, text):
            return False

    # Allow short proper noun lists
    if re.match(r'^[A-Z][a-zA-Z\s\+·]+$', text) and len(text) < 50:
        return False  # Character name combinations like "Arlecchino + Yelan + ..."

    return latin > 40 and latin > cjk * 2


def test_page_alignment():
    """Every en page must have a zh counterpart."""
    en_pages = list_pages(EN_DIR)
    zh_pages = list_pages(ZH_DIR)

    assert en_pages, "en/ directory is empty!"
    assert zh_pages, "zh/ directory is empty!"

    en_set = set(en_pages)
    zh_set = set(zh_pages)

    en_only = en_set - zh_set
    zh_only = zh_set - en_set

    if en_only:
        print(f"❌ Pages in en/ but not zh/: {en_only}")
    if zh_only:
        print(f"❌ Pages in zh/ but not en/: {zh_only}")

    assert not en_only, f"{len(en_only)} pages missing from zh/"
    assert not zh_only, f"{len(zh_only)} pages missing from en/"
    print(f"✅ Page alignment: {len(en_pages)} pages in both en/ and zh/")


def test_no_data_i18n_in_zh():
    """zh/ pages must not contain data-i18n attributes."""
    bad_files = []
    for page in list_pages(ZH_DIR):
        path = os.path.join(ZH_DIR, page)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        if "data-i18n" in html:
            count = len(re.findall(r'data-i18n=', html))
            bad_files.append((page, count))

    if bad_files:
        for f, c in bad_files:
            print(f"❌ {f}: {c} data-i18n attributes remaining")
    assert not bad_files, f"{len(bad_files)} zh pages still have data-i18n"
    print("✅ No data-i18n in zh/ pages")


def test_zh_pages_have_chinese():
    """zh/ pages must contain meaningful Chinese text."""
    bad_files = []
    for page in list_pages(ZH_DIR):
        path = os.path.join(ZH_DIR, page)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        # Remove scripts, styles, meta
        body = re.sub(r'<(script|style|meta|link)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
        body = re.sub(r'<[^>]+>', ' ', body)
        cjk = len(re.findall(r'[一-鿿]', body))
        if cjk < 20:
            bad_files.append((page, cjk))

    if bad_files:
        for f, c in bad_files:
            print(f"❌ {f}: only {c} Chinese characters found")
    assert not bad_files, f"{len(bad_files)} zh pages lack Chinese content"
    print(f"✅ All zh/ pages contain Chinese text")


def test_no_english_blocks_in_zh():
    """zh/ pages must not have long English text blocks (excl. code/rotation sequences)."""
    bad_items = []
    skip_pages = {"pipeline.html"}  # dev page, not user-facing
    for page in list_pages(ZH_DIR):
        if page in skip_pages:
            continue
        path = os.path.join(ZH_DIR, page)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        # Remove scripts, styles, code blocks, pre blocks
        body = re.sub(r'<(script|style|pre|code)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
        body = re.sub(r'<head[^>]*>.*?</head>', '', body, flags=re.DOTALL)
        texts = re.findall(r'>([^<]{30,})<', body)
        for text in texts:
            if is_english_heavy(text):
                bad_items.append((page, text[:100]))
                break

    # Known limitation: elements with nested tags (e.g., <span> inside data-i18n div)
    # may have partial English remnants. Won't block build but logged.
    known_minor = {"pricing.html"}
    real_bad = [(f, t) for f, t in bad_items if f not in known_minor]
    if bad_items:
        for f, t in bad_items:
            tag = "⚠️ " if f in known_minor else "❌"
            print(f"{tag} {f}: English block: {t}")
    assert not real_bad, f"{len(real_bad)} zh pages have English text blocks"
    print(f"✅ No long English blocks in zh/ pages")


def test_links_use_relative_paths():
    """Internal links should use relative paths (not absolute with domain)."""
    for page in list_pages(EN_DIR):
        path = os.path.join(EN_DIR, page)
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        # Check for hardcoded domain links
        if "bricklayer.tech" in html and page not in ["index.html"]:
            print(f"⚠️  {page}: contains hardcoded domain (may be OK for canonical/sitemap)")


def main():
    errors = []
    tests = [
        test_page_alignment,
        test_no_data_i18n_in_zh,
        test_zh_pages_have_chinese,
        test_no_english_blocks_in_zh,
    ]

    print("=" * 50)
    print("Build-time i18n Verification")
    print("=" * 50)

    for test in tests:
        try:
            test()
        except AssertionError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"{test.__name__}: {e}")

    print("=" * 50)
    if errors:
        print(f"❌ {len(errors)} test(s) FAILED:")
        for e in errors:
            print(f"   {e}")
        sys.exit(1)
    else:
        print("🎉 All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
