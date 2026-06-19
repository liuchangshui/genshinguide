"""
translate.py — Auto-translate guide content to Chinese via DeepSeek V4 API.

Usage:
    python translate.py --character bennett           # translate one character
    python translate.py --character bennett --dry-run # preview only, no API call
    python translate.py --all                        # translate all guides
    python translate.py --build-js                   # rebuild i18n.js from i18n.json

Architecture:
    pipeline/data/i18n.json  ← canonical translation data (clean JSON)
    pr-site/js/i18n.js       ← generated from i18n.json + runtime functions

Flow:
    1. Read guide JSON → extract English text fields
    2. Read i18n.json → find keys with missing zh translations
    3. Call DeepSeek V4 API to batch-translate missing strings
    4. Write i18n.json → build i18n.js
"""

import json
import os
import sys
import ssl
import hashlib
import argparse
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

import config

# DeepSeek API config — read from env (check both common var names)
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Paths
I18N_JSON = os.path.join(os.path.dirname(__file__), "data", "i18n.json")
CACHE_FILE = os.path.join(os.path.dirname(__file__), "data", "translate_cache.json")


# ---------------------------------------------------------------------------
# i18n data I/O (clean JSON)
# ---------------------------------------------------------------------------

def load_i18n_json():
    """Load canonical translation data from JSON."""
    if not os.path.exists(I18N_JSON):
        print(f"[WARN] {I18N_JSON} not found, starting fresh")
        return {}
    with open(I18N_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_i18n_json(data):
    """Save translation data to JSON."""
    Path(os.path.dirname(I18N_JSON)).mkdir(parents=True, exist_ok=True)
    with open(I18N_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [i18n.json] Written")


def build_i18n_js(output_path=None):
    """
    Generate pr-site/js/i18n.js from i18n.json + runtime template.
    """
    if output_path is None:
        output_path = config.I18N_FILE

    data = load_i18n_json()
    if not data:
        print("[ERROR] No i18n data to build from")
        return

    def format_js(val, indent=0):
        """Format a Python value as clean JS object literal."""
        if val is None:
            return "null"
        if isinstance(val, bool):
            return "true" if val else "false"
        if isinstance(val, (int, float)):
            return str(val)
        if isinstance(val, str):
            escaped = val.replace("\\", "\\\\").replace("'", "\\'")
            return f"'{escaped}'"
        if isinstance(val, dict):
            if not val:
                return "{}"
            keys = list(val.keys())
            # Leaf translation node: { en:..., zh:... }
            if set(keys) == {"en", "zh"} or set(keys) == {"en"}:
                parts = [f"{k}:{format_js(val[k])}" for k in keys]
                return "{ " + ", ".join(parts) + " }"
            # Nested object — multi-line
            pad = "  " * (indent + 1)
            inner_pad = "  " * indent
            lines = ["{"]
            for k, v in val.items():
                lines.append(f"{pad}{k}: {format_js(v, indent + 1)},")
            lines.append(f"{inner_pad}}}")
            return "\n".join(lines)
        return str(val)

    sections_order = [
        "nav", "home", "guide", "calc", "pricing", "guides",
        "footer", "ad", "calcJS",
        # Character sections (alphabetical)
    ]

    # Collect all sections, put known ones first
    all_sections = list(data.keys())
    char_sections = sorted([s for s in all_sections if s not in sections_order])
    ordered_sections = [s for s in sections_order if s in data] + char_sections

    lines = []
    lines.append("const I18N = {")
    lines.append("  current: localStorage.getItem('lang') || 'en',")
    lines.append("")

    for section in ordered_sections:
        section_data = data[section]
        if not isinstance(section_data, dict):
            continue
        # Section header
        lines.append(f"  // ===== {section} =====")
        # Format section content at indent=1, then wrap with section name
        body = format_js(section_data, indent=1)
        body_lines = body.split("\n")
        # Replace opening { with section header
        body_lines[0] = f"  {section}: {{"
        # Append comma to closing brace
        body_lines[-1] = body_lines[-1] + ","
        lines.append("\n".join(body_lines))
        lines.append("")

    lines.append("};")

    # Runtime functions (static, appended verbatim)
    runtime = r"""
// ===== i18n Engine =====
function t(path){
  const keys = path.split('.');
  let obj = I18N;
  for(const k of keys){ obj = obj?.[k]; if(!obj) return path; }
  return obj?.[I18N.current] || obj?.en || path;
}

function switchLang(lang){
  I18N.current = lang;
  localStorage.setItem('lang', lang);
  document.documentElement.lang = lang;
  applyI18n();
  document.querySelectorAll('.lang-toggle').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
  if(typeof updateCalc === 'function') updateCalc();

  // Update <title> and <meta> tags for the new language
  const pageType = document.body.dataset.page;
  if (pageType && I18N[pageType]) {
    const titleKey = pageType + '.title';
    const descKey = pageType + '.desc';
    if (I18N[pageType].title) {
      const tTitle = t(titleKey);
      if (tTitle !== titleKey) document.title = tTitle;
    }
    if (I18N[pageType].desc) {
      const tDesc = t(descKey);
      if (tDesc !== descKey) {
        const descEl = document.querySelector('meta[name="description"]');
        if (descEl) descEl.setAttribute('content', tDesc);
        const ogDescEl = document.querySelector('meta[property="og:description"]');
        if (ogDescEl) ogDescEl.setAttribute('content', tDesc);
      }
    }
  }
}

function applyI18n(){
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if(key) el.placeholder = t(key);
  });
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const text = t(key);
    if(el.tagName === 'INPUT' && el.type === 'email'){
      el.placeholder = text;
    } else if(el.tagName === 'INPUT' || el.tagName === 'TEXTAREA'){
      // skipped
    } else {
      el.innerHTML = text;
    }
  });
}

document.addEventListener('DOMContentLoaded', ()=>{
  applyI18n();
  document.querySelectorAll('.lang-toggle').forEach(btn => {
    btn.addEventListener('click', ()=> switchLang(btn.dataset.lang));
  });
  document.querySelectorAll('.lang-toggle').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === I18N.current);
  });
});
"""

    js_content = "\n".join(lines) + runtime

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"  [i18n.js] Built ({len(js_content)} bytes) → {output_path}")


# ---------------------------------------------------------------------------
# Translation cache
# ---------------------------------------------------------------------------

def _load_cache():
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_cache(cache):
    Path(os.path.dirname(CACHE_FILE)).mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Guide field extraction
# ---------------------------------------------------------------------------

def extract_guide_fields(guide_json, character_id):
    """
    Extract all translatable text fields from a guide JSON.
    Returns: dict of { i18n_key: english_text }
    """
    fields = {}

    def add(key, text):
        if text and isinstance(text, str) and text.strip():
            fields[f"{character_id}.{key}"] = text.strip()

    # Core
    add("intro", guide_json.get("intro", ""))
    add("weapon_bottom_line", guide_json.get("weapon_bottom_line", ""))
    add("rotation_title", guide_json.get("rotation_title", ""))
    add("rotation_code", guide_json.get("rotation_code", ""))
    add("rotation_key", guide_json.get("rotation_key", ""))

    # Weapons
    for i, w in enumerate(guide_json.get("weapons", []), 1):
        add(f"w{i}_notes", w.get("notes", ""))

    # Artifacts
    arti_best = guide_json.get("best_artifact", "")
    if arti_best:
        add("arti_best", f"🎯 Best: {arti_best}")
    add("arti_why", guide_json.get("artifact_why", ""))

    # Main stats
    ms = guide_json.get("main_stats", {})
    add("sands_note", ms.get("sands_note", ""))
    add("goblet_note", ms.get("goblet_note", ""))
    add("circlet_note", ms.get("circlet_note", ""))

    # Substat priority
    for i, sub in enumerate(guide_json.get("sub_priority", []), 1):
        add(f"sub{i}", sub)

    # Teams
    for i, team in enumerate(guide_json.get("teams", []), 1):
        add(f"team{i}_name", team.get("name", ""))
        add(f"team{i}_desc", team.get("desc", ""))

    # Talents
    for i, talent in enumerate(guide_json.get("talent_priority", []), 1):
        add(f"talent{i}_label", talent.get("label", ""))

    # Mistakes
    for i, mistake in enumerate(guide_json.get("mistakes", []), 1):
        add(f"m{i}", mistake)

    # Related guides
    for related in guide_json.get("related_guides", []):
        rid = related.get("id", "")
        desc = related.get("desc", "")
        if rid and desc:
            add(f"related_{rid}", desc)

    # Description (char_role_desc in template, from SEO description)
    desc = guide_json.get("seo", {}).get("description", "")
    if desc:
        add("desc", desc)

    return fields


# ---------------------------------------------------------------------------
# Missing translation detection
# ---------------------------------------------------------------------------

def find_missing_translations(extracted_fields, i18n_data):
    """
    Compare extracted fields against i18n_data.
    Returns: list of (key, english_text, existing_zh_or_None)
    """
    missing = []

    for key, en_text in extracted_fields.items():
        parts = key.split(".")
        obj = i18n_data
        found = True
        for part in parts:
            if isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                found = False
                break

        if not found:
            # Key path doesn't exist
            missing.append((key, en_text, None))
        elif isinstance(obj, dict):
            if "zh" not in obj:
                missing.append((key, obj.get("en", en_text), None))
            elif not obj["zh"]:
                missing.append((key, obj.get("en", en_text), None))
        elif isinstance(obj, str):
            # Legacy bare string — needs {en, zh} format
            missing.append((key, obj, None))

    return missing


# ---------------------------------------------------------------------------
# DeepSeek API
# ---------------------------------------------------------------------------

def call_deepseek_translate(texts, api_key=None):
    """
    Batch-translate English game guide texts to Chinese via DeepSeek V4.

    Args:
        texts: list of (key, english_text) tuples
    Returns:
        dict of { key: chinese_text }
    """
    if not api_key:
        api_key = DEEPSEEK_API_KEY

    if not api_key:
        print("  [WARN] No DEEPSEEK_API_KEY set. Set env var or pass --api-key.")
        return {}

    cache = _load_cache()
    uncached = []
    result = {}

    for key, en_text in texts:
        text_hash = hashlib.md5(en_text.encode()).hexdigest()[:12]
        if text_hash in cache:
            result[key] = cache[text_hash]
        else:
            uncached.append((key, en_text, text_hash))

    if not uncached:
        print(f"  [cache] All {len(texts)} strings cached")
        return result

    print(f"  [API] Translating {len(uncached)} strings...")

    items = "\n".join(
        f"{i+1}. {en_text}"
        for i, (_, en_text, _) in enumerate(uncached)
    )

    prompt = f"""Translate these Genshin Impact game guide texts from English to Chinese (Simplified).

Important context:
- This is for a Genshin Impact (原神) character build guide
- Use official Genshin Impact Chinese terminology:
  - Artifact sets: use official Chinese names (e.g. "Emblem of Severed Fate" = "绝缘之旗印")
  - Weapons: use official Chinese names (e.g. "Engulfing Lightning" = "薙草之稻光")
  - Stats: CRIT Rate = 暴击率, CRIT DMG = 暴击伤害, ATK = 攻击力, HP = 生命值, DEF = 防御力, EM = 元素精通, ER = 元素充能效率
  - Talents: Normal Attack = 普通攻击, Elemental Skill = 元素战技, Elemental Burst = 元素爆发
  - Game terms: Burst = 元素爆发, Skill = 元素战技, DMG = 伤害, DPS = 输出, AoE = 范围伤害
- Keep emoji like ❌ 🎯 ⚡ and formatting markers unchanged
- Keep game version numbers, percentages, and numerical values unchanged
- Keep HTML tags like <span>, <strong> unchanged

Return ONLY a JSON object mapping item numbers to Chinese translations:
{{"1": "中文翻译1", "2": "中文翻译2", ...}}

Texts to translate:
{items}"""

    try:
        req = Request(
            DEEPSEEK_API_URL,
            data=json.dumps({
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You translate Genshin Impact content to Simplified Chinese. Output valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 4096,
            }).encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        ctx = ssl._create_unverified_context()
        resp = urlopen(req, timeout=90, context=ctx)
        resp_data = json.loads(resp.read())
        content = resp_data["choices"][0]["message"]["content"]

        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            translations = json.loads(content[json_start:json_end])
        else:
            print(f"  [ERROR] Cannot parse API response: {content[:200]}")
            return result

        for i, (key, en_text, text_hash) in enumerate(uncached):
            str_idx = str(i + 1)
            if str_idx in translations:
                zh_text = translations[str_idx]
                result[key] = zh_text
                cache[text_hash] = zh_text

        _save_cache(cache)
        print(f"  [API] Got {len(result)} translations ({len(uncached)} new)")

    except URLError as e:
        print(f"  [ERROR] API network error: {e}")
    except Exception as e:
        print(f"  [ERROR] Translation error: {e}")

    return result


# ---------------------------------------------------------------------------
# Apply translations
# ---------------------------------------------------------------------------

def apply_translations(i18n_data, extracted_fields, translations):
    """Merge translations into i18n_data, creating intermediate nodes."""
    for key, en_text in extracted_fields.items():
        parts = key.split(".")
        char_section = parts[0]

        if char_section not in i18n_data:
            i18n_data[char_section] = {}

        obj = i18n_data
        for part in parts[:-1]:
            if part not in obj or not isinstance(obj[part], dict):
                obj[part] = {}
            obj = obj[part]

        leaf_key = parts[-1]
        zh_text = translations.get(key, "")

        obj[leaf_key] = {
            "en": en_text,
            "zh": zh_text if zh_text else en_text,
        }

    return i18n_data


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Auto-translate Genshin guide content to Chinese")
    ap.add_argument("--character", type=str, help="Character ID to translate")
    ap.add_argument("--all", action="store_true", help="Translate all guides")
    ap.add_argument("--dry-run", action="store_true", help="Preview missing translations, no API call")
    ap.add_argument("--api-key", type=str, help="DeepSeek API key")
    ap.add_argument("--build-js", action="store_true", help="Only rebuild i18n.js from i18n.json")
    ap.add_argument("--init-json", action="store_true", help="One-time: extract i18n.json from current i18n.js (requires Node.js)")
    args = ap.parse_args()

    # --init-json: one-time migration from i18n.js → i18n.json
    if args.init_json:
        print("Extracting i18n.json from current i18n.js using Node.js...")
        import subprocess
        script = """
        const fs = require('fs');
        global.localStorage = { getItem: () => 'en' };
        global.document = { addEventListener: () => {}, documentElement: {}, querySelectorAll: () => [] };
        const src = fs.readFileSync('../pr-site/js/i18n.js', 'utf8');
        const i18nEnd = src.indexOf('\\n// ===== i18n Engine =====');
        const decl = src.substring(0, i18nEnd).replace('const I18N = ', 'var I18N = ');
        eval(decl);
        const clean = {...I18N};
        delete clean.current;
        fs.writeFileSync('data/i18n.json', JSON.stringify(clean, null, 2));
        console.log('Written data/i18n.json with sections:', Object.keys(clean).join(', '));
        """
        result = subprocess.run(["node", "-e", script], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return

    # --build-js: rebuild i18n.js from i18n.json
    if args.build_js:
        build_i18n_js()
        return

    # Load translation data
    print("[1/5] Loading i18n.json...")
    i18n_data = load_i18n_json()
    print(f"  {len(i18n_data)} sections loaded")

    # Determine characters
    characters = []
    if args.all:
        guide_dir = os.path.join(os.path.dirname(__file__), "data", "guides")
        if os.path.isdir(guide_dir):
            characters = sorted([f[:-5] for f in os.listdir(guide_dir) if f.endswith(".json")])
    elif args.character:
        characters = [args.character]
    else:
        print("[ERROR] Use --character <id>, --all, --build-js, or --init-json")
        sys.exit(1)

    api_key = args.api_key or DEEPSEEK_API_KEY
    any_missing = False

    for cid in characters:
        print(f"\n[2/5] Processing {cid}...")
        json_path = os.path.join(os.path.dirname(__file__), "data", "guides", f"{cid}.json")
        if not os.path.exists(json_path):
            print(f"  [SKIP] No JSON at {json_path}")
            continue

        with open(json_path, "r", encoding="utf-8") as f:
            guide_json = json.load(f)

        extracted = extract_guide_fields(guide_json, cid)
        print(f"  Extracted {len(extracted)} fields")

        missing = find_missing_translations(extracted, i18n_data)
        print(f"  Missing zh: {len(missing)}")

        if not missing:
            print(f"  ✅ Complete!")
            continue

        any_missing = True

        if args.dry_run:
            print(f"\n  --- Missing keys ---")
            for key, en_text, _ in missing[:30]:
                preview = en_text[:100].replace('\n', ' ')
                print(f"  {key}")
                print(f"    EN: {preview}...")
            if len(missing) > 30:
                print(f"  ... and {len(missing) - 30} more")
            continue

        texts = [(key, en_text) for key, en_text, _ in missing]
        translations = call_deepseek_translate(texts, api_key)

        if translations:
            i18n_data = apply_translations(i18n_data, extracted, translations)
            print(f"  Applied {len(translations)} translations")
        else:
            print(f"  ⚠️  No translations — check API key or network")

    # Save and build
    if not args.dry_run and any_missing:
        print(f"\n[3/5] Saving i18n.json...")
        save_i18n_json(i18n_data)

    if not args.dry_run:
        print(f"\n[{'4' if any_missing else '3'}/5] Building i18n.js...")
        build_i18n_js()
        print("\n✅ Done!")
    else:
        print("\n[Dry run — no files written]")


if __name__ == "__main__":
    main()
