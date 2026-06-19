export const meta = {
  name: 'genshinguide-phase0-phase1',
  description: 'GenshinGuide Phase 0 (Legal + SEO + 3 Manual Guides) + Phase 1 Pipeline',
  phases: [
    { title: 'Legal & Deploy', detail: 'Legal compliance footer updates + SEO infrastructure files' },
    { title: 'Manual Guides', detail: '3 hand-written guides: Furina, Arlecchino, Neuvillette' },
    { title: 'Phase 0 Gate', detail: 'Quality check on all Phase 0 outputs' },
    { title: 'Pipeline Build', detail: 'Python pipeline: config, sync, generate, verify, publish, template, CI' }
  ]
}

const ROOT = '/Users/liucs/CodeingZH/Cc_Projects/genshinguide-deliverables/';

// ============================================================
// PHASE 0 — PARALLEL: Legal + SEO + 3 Manual Guides
// ============================================================

const [phase0Infra, phase0Guides] = await parallel([
  // Track A: Infrastructure (Legal + SEO run sequentially within this track)
  async () => {
    phase('Legal & Deploy');

    const legalPrompt = [
      'Implement legal compliance for the GenshinGuide static site at ' + ROOT,
      'READ corrections-memo.md Section 9 first. Legal research is COMPLETE — risk is LOW.',
      '',
      'TASKS:',
      '1. In ALL 14 HTML files under pr-site/, update the footer to use:',
      '   "Fan-made project. Not affiliated with HoYoverse. Game data (c) Cognosphere."',
      '   Find existing copyright text in <footer> and replace it.',
      '',
      '2. In pr-site/js/i18n.js, add a "legal" key to the "footer" section with EN and ZH translations.',
      '',
      '3. In pricing.html, change any "Genshin Pro" text to "Pro Tools".',
      '',
      '4. Create DOMAIN_RECOMMENDATION.md suggesting domains like buildguide.gg',
      '   Explain why avoiding "genshin" in the primary domain reduces trademark risk.',
      '',
      'OUTPUT: A checklist of every file modified.'
    ].join('\n');

    const seoPrompt = [
      'Set up SEO infrastructure for the GenshinGuide static site at ' + ROOT,
      'READ pr-site/index.html and pr-site/guide-raiden.html first.',
      '',
      'CRITICAL: 7 placeholder guides (hutao, ayaka, yelan, nahida, kazuha, zhongli, albedo) have COPIED Raiden content with wrong meta tags. Fix their meta tags.',
      '',
      'TASKS:',
      '1. CREATE pr-site/sitemap.xml — list all 14 pages with 2026-06-18 dates',
      '2. CREATE pr-site/robots.txt — allow all crawlers, point to sitemap',
      '3. FIX <title> and <meta description> on all guide pages to be UNIQUE per character',
      '4. Add Open Graph tags to index.html and all guide pages',
      '5. Verify schema.org JSON-LD on all pages',
      '6. CREATE DEPLOY_INSTRUCTIONS.md for Cloudflare Pages + GSC + GA4 setup',
      '7. CREATE SEO_CHECKLIST.md with pre-launch verification steps',
      '',
      'OUTPUT: All generated files + instruction documents.'
    ].join('\n');

    const legal = await agent(legalPrompt, {label: 'Legal Compliance'});
    log('Legal: ' + (legal ? 'Done' : 'Failed'));

    const seo = await agent(seoPrompt, {label: 'SEO & Deploy'});
    log('SEO: ' + (seo ? 'Done' : 'Failed'));

    return { legal: !!legal, seo: !!seo };
  },

  // Track B: 3 Manual Guides (parallel within this track)
  async () => {
    phase('Manual Guides');

    const furinaPrompt = [
      'Write a HAND-WRITTEN build guide for Furina in Genshin Impact. Publication quality.',
      'PROJECT ROOT: ' + ROOT,
      '',
      'READ FIRST: pr-site/guide-raiden.html (structure template), pr-site/guide-xiangling.html (quality baseline), pr-site/css/style.css (hydro classes, color #448aff), pr-site/js/i18n.js (key naming)',
      '',
      'CHARACTER: Furina (Focalors) | HYDRO | SWORD | 5-STAR | Sub DPS / Buffer',
      '',
      'KIT (v4.8): E summons 3 Salon Members dealing HP-based Hydro DMG + drain team HP. Q gives massive team DMG buff from HP changes (Fanfare). SCALES WITH HP NOT ATK. Needs team healer for Fanfare. Signature: Splendor of Tranquil Waters (5-star Sword, 542 ATK, CRIT DMG 88.2%). F2P: Fleuve Cendre Ferryman R5 (4-star Sword, 510 ATK, ER 45.9%). Artifact: 4pc Golden Troupe. Main stats: HP%/HP% or Hydro DMG/CRIT. ER: 160-180% solo. Teams: Neuvillette Hypercarry, Noelle Core, Double Hydro Hu Tao. Talent: E > Q >>> NA (skip).',
      '',
      'CREATE: pr-site/guide-furina.html — ALL sections filled, using "hydro" on EVERY element-specific CSS class (.character-showcase.hydro, .tldr-box.hydro, h2.hydro x6, .emphasis-box.hydro, .guide-card.hydro, .guide-card-img.hydro, .elem-icon.hydro). Also UPDATE pr-site/js/i18n.js with Furina-specific translation keys (guide.furina_ prefix).',
      '',
      'CRITICAL: Every word Furina-specific. No copypaste from Raiden/Xiangling. HP scaling emphasized. Verify all weapon ATK values.'
    ].join('\n');

    const arlePrompt = [
      'Write a HAND-WRITTEN build guide for Arlecchino (The Knave) in Genshin Impact.',
      'PROJECT ROOT: ' + ROOT,
      '',
      'READ: pr-site/guide-raiden.html (template), pr-site/guide-xiangling.html (quality), pr-site/css/style.css (pyro #ff5252)',
      '',
      'CHARACTER: Arlecchino | PYRO | POLEARM | 5-STAR | Main DPS',
      '',
      'KIT (v4.8): Bond of Life mechanic — E applies marks, consuming marks grants BoL. NA consume BoL for enhanced Pyro DMG. CANNOT BE HEALED BY ALLIES — only self-heals via Q. Scales with ATK. Signature: Crimson Moon Semblance (5-star Polearm, 674 ATK, CRIT Rate 22.1%). F2P: White Tassel R5 (3-star Polearm, 401 ATK, CRIT Rate 23.4% — yes a 3-star is viable!). Deathmatch (4-star, CRIT Rate 36.8%). Artifact: 4pc Fragment of Harmonic Whimsy OR 4pc Gladiator. Main: ATK%/Pyro DMG/CRIT. Teams: Vape, Mono Pyro, Overload (Chevreuse). NO healers (except Bennett for ATK buff). Talent: NA > E > Q.',
      '',
      'CREATE: pr-site/guide-arlecchino.html (ALL sections, "pyro" on all element CSS classes) + update pr-site/js/i18n.js with Arlecchino keys.',
      'Every word character-specific. Verify weapon ATK values. No copypaste.'
    ].join('\n');

    const neuvPrompt = [
      'Write a HAND-WRITTEN build guide for Neuvillette in Genshin Impact.',
      'PROJECT ROOT: ' + ROOT,
      '',
      'READ: pr-site/guide-raiden.html (template), pr-site/guide-xiangling.html (quality), pr-site/css/style.css (hydro #448aff)',
      '',
      'CHARACTER: Neuvillette | HYDRO | CATALYST | 5-STAR | Main DPS',
      '',
      'KIT (v4.8): Charged ATK Equitable Judgment — massive Hydro beam, main damage. Absorbs droplets from E/Q to speed charge. SCALES WITH HP — NOT ATK. Passive: up to 160% CA DMG bonus from 3 Hydro reactions. Signature: Tome of the Eternal Flow (5-star Catalyst, 542 ATK, CRIT DMG 88.2%). F2P: Prototype Amber R5 (4-star Catalyst, HP% 41.3%, forgeable, very competitive!). Artifact: 4pc Marechaussee Hunter (36% CRIT Rate from HP changes = build more CRIT DMG). Main: HP%/Hydro DMG or HP%/CRIT DMG or HP%. C0 needs shielder. C1 = interruption resistance (huge QoL). Teams: Hypercarry (Furina+Kazuha+Baizhu), Taser, Hyperbloom driver. Talent: NA > E == Q.',
      '',
      'CREATE: pr-site/guide-neuvillette.html (ALL sections, "hydro" on all element CSS classes) + update pr-site/js/i18n.js with Neuvillette keys.',
      'HP scaling must be emphasized throughout. Every word character-specific.'
    ].join('\n');

    const results = await parallel([
      () => agent(furinaPrompt, {label: 'Furina Guide'}),
      () => agent(arlePrompt, {label: 'Arlecchino Guide'}),
      () => agent(neuvPrompt, {label: 'Neuvillette Guide'})
    ]);

    const count = results.filter(Boolean).length;
    log('Manual guides: ' + count + '/3 completed');
    return { guideCount: count, guideResults: results };
  }
]);

const infraOk = phase0Infra && phase0Infra.legal && phase0Infra.seo;
const guidesOk = phase0Guides && phase0Guides.guideCount >= 2;
log('Phase 0 infrastructure: ' + (infraOk ? 'OK' : 'ISSUES'));
log('Phase 0 guides: ' + (phase0Guides ? phase0Guides.guideCount : 0) + '/3');

// ============================================================
// PHASE 0 QA GATE
// ============================================================
phase('Phase 0 Gate');

const qaPrompt = [
  'You are the Phase 0 Quality Gate reviewer for GenshinGuide at ' + ROOT,
  'Use Bash to verify files exist and contain correct content.',
  '',
  'CHECKS:',
  '1. LEGAL: grep -c "Fan-made project" pr-site/*.html (should be 14+)',
  '2. LEGAL: grep -r "Genshin Pro" pr-site/ (should find nothing in branding)',
  '3. SEO: ls pr-site/sitemap.xml pr-site/robots.txt (both must exist)',
  '4. META: For each guide-*.html, verify unique <title> and <meta description>',
  '5. GUIDES: ls pr-site/guide-furina.html pr-site/guide-arlecchino.html pr-site/guide-neuvillette.html',
  '6. For each new guide: grep the correct element class, count h2 sections (>=6), grep "Raiden" (should be ZERO)',
  '',
  'WRITE pr-site/PHASE0_REPORT.md with PASS/FAIL for each check. List specific issues found.'
].join('\n');

const qaResult = await agent(qaPrompt, {label: 'Phase 0 QA'});
log('QA: ' + (qaResult ? 'Done' : 'Failed'));

// ============================================================
// PHASE 1: Pipeline Build
// ============================================================
if (guidesOk) {
  phase('Pipeline Build');

  const pipelinePrompt = [
    'Build the Python content generation pipeline for GenshinGuide at ' + ROOT,
    'READ: dev-handoff.md Task 1.2, pr-site/guide-raiden.html, pr-site/guide-xiangling.html, pr-site/css/style.css, pr-site/js/i18n.js, pr-site/js/calculator.js',
    '',
    'The Jinja2 template MUST produce HTML structurally identical to guide-raiden.html. Every element CSS class uses {{ element }} variable in 7 positions: character-showcase, tldr-box, h2 (x6), emphasis-box, guide-card, guide-card-img, elem-icon.',
    '',
    'CREATE THESE FILES (write each one with actual content):',
    '',
    '1. pipeline/config.py — DEEPSEEK_MODEL="deepseek-chat", TEMPERATURE=0.3 (gen)/0.0 (verify), TIMEOUT=30, MAX_RETRIES=2, DATA_API="https://genshin.jmp.blue", VERSION="4.8". Load API keys from env vars.',
    '',
    '2. pipeline/sync_wiki.py — Fetch characters/weapons/artifacts from genshin.jmp.blue. Cache as JSON to data/cache/. Incremental detection. API down -> use cache.',
    '',
    '3. pipeline/templates/guide_template.html — Jinja2 template. Variables: element, char_name, char_role, weapons[], best_artifact, teams[], talent_priority[], rotation_code, mistakes[], seo_title, seo_description. Include schema.org JSON-LD, OG tags, legal footer, CSS/JS refs. CRITICAL: {{ element }} in all 7 CSS positions listed above.',
    '',
    '4. pipeline/generate.py — 7-step: load cache -> build prompt -> call DeepSeek (json_object, temp 0.3) -> parse -> verify (retry 2x) -> render Jinja2 -> write HTML. Fallback to GPT-4o-mini on timeout. Args: --character, --all, --changed-only.',
    '',
    '5. pipeline/verify.py — Two passes: (a) LLM at temp 0.0 checks weapon ATK/rarity, artifact names, element, team members. (b) Hard checks: JSON schema, ATK 200-750 range, rarity 3-5, element valid, teams >= 2. Return {errors, warnings, passed}.',
    '',
    '6. pipeline/publish.py — Update guides.html, sitemap.xml, i18n.js, calculator.js DATA. Git commit+push. Require confirmation prompt.',
    '',
    '7. .github/workflows/daily-sync.yml — GitHub Actions, daily cron, sync + generate + git push. Use GitHub secrets for API keys.',
    '',
    'ALSO: pipeline/requirements.txt (requests, jinja2, openai, python-dotenv) and pipeline/PIPELINE_README.md',
    '',
    'VERIFY after: template has {{ element }} in 7 positions, generate.py has 7-step flow, verify.py has both check types, CI uses secrets.'
  ].join('\n');

  const pipelineResult = await agent(pipelinePrompt, {label: 'Pipeline Build'});
  log('Pipeline: ' + (pipelineResult ? 'Done' : 'Failed'));
} else {
  log('Skipping Phase 1 — Phase 0 guides not ready');
}

log('\n============================================================');
log('WORKFLOW COMPLETE');
log('Infrastructure: ' + (infraOk ? 'OK' : 'CHECK ISSUES'));
log('Guides: ' + (phase0Guides ? phase0Guides.guideCount : 0) + '/3');
log('QA: ' + (qaResult ? 'Done' : 'Failed'));
if (guidesOk) log('Pipeline: ' + (typeof pipelineResult !== 'undefined' ? 'Done' : 'Skipped'));
log('============================================================');
