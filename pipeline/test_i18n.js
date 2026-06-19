#!/usr/bin/env node
/**
 * test_i18n.js — Test harness for i18n coverage.
 *
 * For each HTML page, simulates switching to Chinese and detects:
 *   1. Visible English text NOT wrapped in data-i18n
 *   2. data-i18n keys that resolve to English-heavy text in zh mode
 *   3. Meta tags with English content
 *
 * Usage: node pipeline/test_i18n.js
 * Output: JSON array of failures
 */

const fs = require('fs');
const path = require('path');

// ---- Setup i18n ----
global.localStorage = { getItem: () => 'zh' };
global.document = {
  addEventListener: () => {},
  documentElement: { lang: 'en' },
  querySelectorAll: () => [],
};

const prSiteDir = path.join(__dirname, '..', 'pr-site');
const i18nPath = path.join(prSiteDir, 'js', 'i18n.js');
const src = fs.readFileSync(i18nPath, 'utf8').replace('const I18N', 'global.I18N');
eval(src);
I18N.current = 'zh';

// ---- Helpers ----

/** Check if text needs translation (UI text, not game proper nouns) */
function isEnglishHeavy(text) {
  const latin = (text.match(/[a-zA-Z]/g) || []).length;
  const cjk = (text.match(/[一-鿿㐀-䶿]/g) || []).length;
  const total = text.replace(/\s/g, '').length;
  if (total < 8) return false;
  if (cjk > 0 && latin < 10) return false;
  if (latin <= cjk) return false;

  // Game proper nouns that are OK to stay in English:
  // Weapon names: "Crimson Moon's Semblance", "Staff of Homa", "The Catch"
  // Character names: "Raiden Shogun", "Hu Tao", "Arlecchino"
  // Artifact sets: "Emblem of Severed Fate", "Blizzard Strayer"
  // Stats: "ATK", "CRIT Rate", "HP%"
  // These appear in TL;DR and table cells — acceptable
  const properNounPatterns = [
    /^(Crimson|Staff|Primordial|Engulfing|Skyward|Aquila|Favonius|Sacrificial|Mistsplitter|Amenoma|Harbinger|Blackcliff|Deathmatch|White\s+Tassel|Dragon'?s?\s+Bane|Sapwood|Festering|Iron\s+Sting|Xiphos|Freedom-Sworn|Splendor|Tome|Key|Jade|Cinnabar|Fleuve|Prototype)/i,
    /\b(Shogun|Raiden|Furina|Arlecchino|Neuvillette|Kazuha|Nahida|Bennett|Xiangling|Yelan|Zhongli|Albedo|Ayaka|Hu\s+Tao|Xingqiu|Fischl|Gorou|Itto|Shenhe|Kokomi|Mona|Sucrose|Diona|Chevreuse|Layla|Baizhu|Jean|Childe|Ganyu|Yoimiya|Wanderer|Lyney|Navia|Yae|Kuki|Beidou|Nilou|Noelle)\b/i,
    /^\d+$/,  // pure numbers (ATK values)
    /^[⭐]+$/, // rarity stars
  ];

  // If text is mostly game data (weapon table cells, stat values), allow it
  if (properNounPatterns.some(p => p.test(text))) return false;

  // Known acceptable: game terms that appear alone
  if (/^(Sword|Polearm|Claymore|Bow|Catalyst|Pyro|Hydro|Electro|Dendro|Anemo|Geo|Cryo|v\d+\.\d+|ATK|CRIT|HP|DEF|EM|ER|DPS|DMG)$/i.test(text.trim())) return false;

  return latin >= 12;
}

/** Strip HTML tags for text extraction */
function stripTags(html) {
  return html.replace(/<[^>]+>/g, ' ').replace(/&[a-z]+;/g, ' ').replace(/\s+/g, ' ').trim();
}

/** Extract text nodes from HTML (elements without data-i18n covering them) */
function extractVisibleTexts(html) {
  const results = [];

  // Remove scripts and styles
  let cleaned = html.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, '');

  // Find ALL text nodes — elements that have text content
  // We need to identify text that's NOT inside a data-i18n element
  const i18nElements = new Set();
  const i18nRe = /<[^>]*data-i18n="([^"]*)"[^>]*>([\s\S]*?)<\/[^>]+>/gi;
  let m;

  // Find text inside data-i18n elements — these ARE translated
  while ((m = i18nRe.exec(cleaned)) !== null) {
    const key = m[1];
    const fallback = stripTags(m[2]);
    const translated = t(key);
    // Replace the element content with translated text for further checking
    if (translated && translated !== key) {
      const fullMatch = m[0];
      const translatedTag = fullMatch.replace(/>[^<]*<\//, '>' + translated + '</');
      cleaned = cleaned.replace(fullMatch, translatedTag);
    }
  }

  // Now extract remaining text nodes that DON'T have data-i18n covering them
  // Strip all remaining tags
  const remaining = cleaned.replace(/<[^>]+>/g, '\n').replace(/&[a-z]+;/g, '');
  const lines = remaining.split('\n').map(l => l.trim()).filter(l => l.length > 3);

  for (const line of lines) {
    if (isEnglishHeavy(line)) {
      results.push(line.substring(0, 120));
    }
  }

  return results;
}

/** Check data-i18n keys that resolve to English in zh mode */
function checkI18nKeys(html) {
  const failures = [];
  const seen = new Set();
  const re = /data-i18n="([^"]+)"/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    const key = m[1];
    if (seen.has(key)) continue;
    seen.add(key);

    const resolved = t(key);
    if (resolved === key) {
      failures.push({ key, issue: 'KEY_NOT_FOUND', resolved: '(key path not in I18N)' });
    } else if (isEnglishHeavy(resolved)) {
      failures.push({ key, issue: 'ENGLISH_HEAVY', resolved: resolved.substring(0, 100) });
    }
  }
  return failures;
}

/** Check meta tags */
function checkMeta(html) {
  const failures = [];
  const titleMatch = html.match(/<title>([^<]+)<\/title>/);
  if (titleMatch && isEnglishHeavy(titleMatch[1])) {
    failures.push({ tag: 'title', text: titleMatch[1] });
  }
  const descMatch = html.match(/<meta name="description" content="([^"]+)"/);
  if (descMatch && isEnglishHeavy(descMatch[1])) {
    failures.push({ tag: 'meta description', text: descMatch[1].substring(0, 100) });
  }
  const ogTitleMatch = html.match(/<meta property="og:title" content="([^"]+)"/);
  if (ogTitleMatch && isEnglishHeavy(ogTitleMatch[1])) {
    failures.push({ tag: 'og:title', text: ogTitleMatch[1] });
  }
  return failures;
}

// ---- Main ----

const pages = fs.readdirSync(prSiteDir).filter(f => f.endsWith('.html'));
const allResults = [];

for (const page of pages.sort()) {
  const htmlPath = path.join(prSiteDir, page);
  const html = fs.readFileSync(htmlPath, 'utf8');

  const visibleEnglish = extractVisibleTexts(html);
  const keyFailures = checkI18nKeys(html);
  const metaFailures = checkMeta(html);

  const totalFailures = visibleEnglish.length + keyFailures.length + metaFailures.length;

  if (totalFailures > 0) {
    allResults.push({
      page,
      totalFailures,
      visibleEnglish: visibleEnglish.slice(0, 15),
      keyFailures: keyFailures.slice(0, 20),
      metaFailures,
    });
  }
}

// Summary
let totalFails = 0;
for (const r of allResults) {
  console.log(`\n❌ ${r.page} — ${r.totalFailures} failures`);
  totalFails += r.totalFailures;

  if (r.visibleEnglish.length > 0) {
    console.log('  [Visible English text]');
    r.visibleEnglish.forEach(t => console.log(`    "${t}"`));
  }
  if (r.keyFailures.length > 0) {
    console.log('  [Key failures]');
    r.keyFailures.forEach(k => console.log(`    ${k.key} (${k.issue}): ${k.resolved}`));
  }
  if (r.metaFailures.length > 0) {
    console.log('  [Meta failures]');
    r.metaFailures.forEach(m => console.log(`    <${m.tag}>: ${m.text}`));
  }
}

const passingCount = pages.length - allResults.length;
console.log(`\n${'='.repeat(50)}`);
console.log(`✅ ${passingCount}/${pages.length} pages clean | ❌ ${allResults.length} pages with issues`);
console.log(`Total failures: ${totalFails}`);
if (totalFails === 0) console.log('🎉 ALL PAGES PASS!');

process.exit(totalFails > 0 ? 1 : 0);
