# GenshinGuide — Lessons Learned

> Issues encountered and resolved during development. Do not repeat these mistakes.

---

## Issue 1: Shared i18n Keys Contaminated with Character-Specific Text 🔴 Critical

**What happened**: The `guide.*` namespace in `i18n.js` contained Raiden Shogun's text (e.g., `guide.intro` = "Raiden Shogun (Raiden Ei) is one of the most versatile..."). When other guide pages used `data-i18n="guide.intro"`, the `applyI18n()` function replaced their correct HTML fallback text with Raiden's text.

**Root cause**: Shared translation keys were used for character-specific content. The `guide.*` namespace should only contain truly shared UI strings (section headings, table headers, nav, footer).

**Fix applied**: 
1. Removed `data-i18n` from character-specific content on 8 guide pages (185 attributes removed)
2. Added character-specific i18n sections (`hutao.*`, `ayaka.*`, etc.) with proper EN+ZH translations
3. Shared `guide.*` keys now only contain headings and UI labels

**Rule going forward**:
- ✅ Shared keys: headings, table headers, nav, footer, common UI labels
- ❌ Shared keys: intros, weapon notes, artifact descriptions, team descriptions, rotations, mistakes, pro teasers
- ✅ Character-specific keys: `{prefix}.intro`, `{prefix}.w1_notes`, `{prefix}.team1_desc`, etc.

---

## Issue 2: Placeholder Guides with Copied Content 🔴 Critical

**What happened**: 7 guide pages (hutao, ayaka, yelan, nahida, kazuha, zhongli, albedo) were created by copying `guide-raiden.html` and changing only the name. The entire body content — weapons, artifacts, teams, rotation, mistakes — was still Raiden's.

**Root cause**: Rapid prototyping without content quality gates. Placeholders were created structurally correct but content was completely wrong.

**Fix applied**: Expert game knowledge audit + pipeline-based content generation. All 7 guides now have character-correct content.

**Rule going forward**:
- ❌ Never clone a guide page for a new character without rewriting ALL content
- ✅ Use the pipeline: `make.py scaffold {id}` → fill JSON → `make.py render {id}` → verify → publish

---

## Issue 3: i18n.js JavaScript Syntax Error from Unescaped Quotes 🔴 Critical

**What happened**: A translation string contained an unescaped single quote (`'Gladiator's Finale'`) inside a single-quoted JavaScript string. This broke the entire `i18n.js` file — no translations worked at all.

**Root cause**: Manual insertion of translation keys without syntax validation.

**Fix applied**: Changed to double-quoted wrapper (`"Gladiator's Finale"`). Added JS syntax validation step: `node -e "new Function(code)"`.

**Rule going forward**:
- ✅ Always validate JS syntax after editing i18n.js
- ✅ Use double quotes for strings containing single quotes
- ✅ Test language toggle (EN↔ZH) after every i18n.js edit

---

## Issue 4: Workflow Agents Cannot Persist Files 🟡 Medium

**What happened**: Workflow sub-agents consumed 300K+ tokens and made 77 tool calls, but zero files were written to disk. Agents ran in a sandboxed environment without access to the project directory.

**Root cause**: Workflow orchestration is designed for analysis/decision tasks, not file-output tasks. Agent file writes don't persist to the project filesystem.

**Fix applied**: Switched to direct `Write`/`Edit`/`Bash` operations from the main session, with background `Agent` calls for independent parallel tasks.

**Rule going forward**:
- ✅ Workflow: use for analysis, planning, multi-perspective review
- ✅ Direct tools: use for file creation, code writing, content production
- ✅ Background agents: use for independent research/audit tasks

---

## Issue 5: Python 3.9 Type Annotation Compatibility 🟡 Medium

**What happened**: Pipeline scripts used `dict | list` and `str | None` union type syntax (Python 3.10+), but the system runs Python 3.9.7.

**Root cause**: Writing code with newer Python syntax without checking the target version.

**Fix applied**: Replaced `X | Y` with `Optional[X]`/`Union[X, Y]` from `typing`, or removed annotations entirely.

**Rule going forward**:
- ✅ Check Python version first: `python3 --version`
- ✅ Use `from __future__ import annotations` or `typing` module for compatibility

---

## Issue 6: Card Images Using Element Emojis Instead of Character Art 🟡 Medium

**What happened**: Guide listing cards and related-guide cards used element-colored divs with emoji icons (💧, 🔥) instead of actual character portraits.

**Root cause**: Rapid prototyping prioritized structure over visuals.

**Fix applied**: Downloaded character card images from `genshin.jmp.blue` API (`/characters/{id}/card` for portraits, `/characters/{id}/icon` for thumbnails). Replaced all emoji placeholders with `<img>` tags.

**Rule going forward**:
- ✅ Every character page needs: `images/{id}-card.webp` (portrait) and `images/{id}-icon.webp` (thumbnail)
- ✅ Source: `https://genshin.jmp.blue/characters/{id}/card` (free, no API key)
- ❌ Never use emoji or colored divs as character image placeholders

---

## Issue 7: Missing Deploy Path 🟡 Medium

**What happened**: The project had no deploy instructions. The user asked how to get the site live.

**Root cause**: Development focused on content and pipeline, not deployment.

**Fix applied**: Created `DEPLOY.md` with step-by-step instructions for Cloudflare Pages + custom domain. Monthly cost: ~$0.83 (domain only).

**Rule going forward**:
- ✅ Deployment instructions must be part of every project from the start
- ✅ Target platform: Cloudflare Pages (free, static, global CDN)
- ✅ Zero server maintenance

---

## Verification Checklist (Run After Every Change)

- [ ] `i18n.js` passes JS syntax validation
- [ ] Language toggle (EN↔ZH) works on all pages
- [ ] No guide page shows another character's content
- [ ] No guide page has "(Coming Soon)" unless genuinely not written
- [ ] All character images load correctly
- [ ] Pipeline: `python make.py status` reports healthy state
- [ ] All internal links point to correct pages
- [ ] Footer shows: "Fan-made project. Not affiliated with HoYoverse. Game data © Cognosphere."
