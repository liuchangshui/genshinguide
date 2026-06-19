# GenshinGuide — Content Production Standards

> Every guide must meet these standards before publishing.
> Timeline: new character guides must be live within 24h of official release.

---

## Quality Checklist (per guide)

### Accuracy — Non-negotiable
- [ ] Weapon base ATK values match official game data (verify against genshin.jmp.blue cache)
- [ ] Weapon rarities correct (3★/4★/5★)
- [ ] Weapon substat types and values correct
- [ ] Artifact set names are real Genshin Impact sets (no fabricated names)
- [ ] All team members are real playable characters
- [ ] Character element matches official data
- [ ] Character weapon type matches official data
- [ ] HP-scaling characters do NOT recommend ATK% main stats (e.g., Neuvillette, Furina, Yelan)
- [ ] ATK-scaling characters do NOT recommend HP% main stats (e.g., Arlecchino, Hu Tao, Raiden)
- [ ] Talent priority matches current meta consensus

### Structure — Every guide must have
- [ ] TL;DR box (4 items: weapon, artifact, team, key stats)
- [ ] Weapons table (minimum 3 ranked entries, must include F2P option)
- [ ] Artifact section (best set + alternative + main stats table + sub-stat priority)
- [ ] Teams section (minimum 3 team compositions)
- [ ] Talent priority (3 abilities, correct priority order)
- [ ] Rotation guide (executable in-game ability sequence)
- [ ] Common mistakes (minimum 3, with explanations)
- [ ] Related guides (minimum 3 cross-links)
- [ ] Schema.org JSON-LD Article markup
- [ ] Unique SEO title (format: "{Name} Build Guide — Best Weapons, Artifacts, Teams | GenshinGuide")
- [ ] Unique meta description (120-160 chars, contains character name + key gear)

### Visual — CSS correctness
- [ ] Character showcase uses correct element CSS class (`.character-showcase.{element}`)
- [ ] All 6 section headings use correct element class (`h2.{element}`)
- [ ] TL;DR box uses correct element class (`.tldr-box.{element}`)
- [ ] Emphasis boxes use correct element class (`.emphasis-box.{element}`)
- [ ] Element tag displays correct element name and color
- [ ] Character portrait image exists in `images/` directory
- [ ] Related guide cards use correct element classes

### i18n — Bilingual support
- [ ] Character-specific keys use consistent prefix (first 4 letters of character ID)
- [ ] EN translation keys exist in `js/i18n.js`
- [ ] ZH translation keys exist in `js/i18n.js`
- [ ] Shared keys reused where possible (nav, footer, ad, common guide sections)

---

## Content Priority Tiers

Guide production follows search-volume priority:

### Tier P0 — Immediate (within 24h of character release)
Must have complete, accurate guides for top meta characters:
- Furina, Neuvillette, Arlecchino, Raiden Shogun, Bennett, Kazuha, Nahida, Yelan, Zhongli, Hu Tao

### Tier P1 — Week 1 (within 1 week)
Strong but slightly lower search volume:
- Xiangling, Ayaka, Albedo, Xingqiu, Fischl, Xiangling, Kuki Shinobu

### Tier P2 — Week 2-4 (within 1 month)
Fill out the roster:
- All remaining 5-star characters
- Key 4-star supports (Gorou, Faruzan, Sara, Chevreuse)

### New Character — within 24h of official release
1. Data available on genshin.jmp.blue? → `python sync_wiki.py --character {id}`
2. Generate scaffold → `python generate.py --character {id} --scaffold`
3. Write content using scaffold + game knowledge
4. Render → `python generate.py --character {id} --render`
5. Review against this checklist
6. Publish → `python publish.py --character {id}`

---

## Version Update Protocol

Every 6 weeks when a new Genshin version drops:

1. **Run sync**: `python sync_wiki.py` (pulls latest data)
2. **Check diff**: which characters/weapons/artifacts changed?
3. **Priority update**: P0 characters with changed data
4. **Update JSONs**: edit `data/guides/{id}.json` with new recommendations
5. **Regenerate HTML**: `python generate.py --character {id} --render`
6. **Review + publish**

New artifact sets? New weapons? Update all affected guides.

---

## Prohibited Content

Never include:
- ❌ Fabricated weapon/character/artifact names
- ❌ Estimated weapon stats (always use exact values from game data)
- ❌ Leaked/beta content (strictly forbidden — see compliance docs)
- ❌ "Best in slot" claims without context (say "BiS for Main DPS build" not just "BiS")
- ❌ AI-generated text published without human review
- ❌ Copied content from other guide sites (write original analysis)

---

## Review Process

1. **Self-review**: Writer checks all Accuracy items above
2. **Script verify**: `generate.py --render` runs `verify.py` automatically (catches schema/range errors)
3. **Browser review**: Open rendered HTML, check all sections render correctly
4. **i18n test**: Toggle EN→中文, verify no key-strings showing
5. **Cross-link check**: Click all related guide links, verify they go to correct pages
