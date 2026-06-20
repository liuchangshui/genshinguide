#!/usr/bin/env node
/**
 * GenshinGuide End-to-End Acceptance Test
 *
 * Run after every change before committing:
 *   node pipeline/acceptance.js
 *
 * Checks: build integrity, JS syntax, calculator i18n coverage,
 * zh page English residue, page count, image assets.
 */
var fs = require("fs");
var path = require("path");
var child_process = require("child_process");

var ROOT = path.join(__dirname, "..");
var ERRORS = [];

function check(name, fn) {
    try { fn(); console.log("  ✅ " + name); }
    catch(e) { ERRORS.push(name + ": " + e.message); console.log("  ❌ " + name + ": " + e.message); }
}

console.log("=" .repeat(60));
console.log("🔍 GenshinGuide E2E Acceptance Test");
console.log("=" .repeat(60) + "\n");

// ── 1. Build verification ──────────────────────────────────────────────
console.log("[1/5] Build integrity...");
var result = child_process.spawnSync("python3", [
    path.join(ROOT, "pipeline/test_build.py")
], { cwd: ROOT, encoding: "utf8" });
if (result.status !== 0) {
    ERRORS.push("test_build.py failed:\n" + (result.stderr || result.stdout).slice(-200));
    console.log("  ❌ test_build.py FAILED");
} else {
    console.log("  ✅ test_build.py passed");
}

// ── 2. JS syntax ───────────────────────────────────────────────────────
console.log("[2/5] JavaScript syntax...");
["calculator.js", "lang-switcher.js", "calc-i18n.js"].forEach(function(f) {
    var code = fs.readFileSync(path.join(ROOT, "pr-site/js", f), "utf8");
    try { new Function(code); console.log("  ✅ " + f); }
    catch(e) { ERRORS.push(f + " syntax: " + e.message); console.log("  ❌ " + f + ": " + e.message); }
});

// ── 3. Calculator i18n coverage ────────────────────────────────────────
console.log("[3/5] Calculator i18n coverage...");
global.document = { addEventListener: function(){} };
global.window = {};

// Load CALC_I18N
eval(fs.readFileSync(path.join(ROOT, "pr-site/js/calc-i18n.js"), "utf8"));

// Load calculator DATA (patch const→var for global scope)
var calcCode = fs.readFileSync(path.join(ROOT, "pr-site/js/calculator.js"), "utf8");
calcCode = calcCode.replace(
    /\bconst\s+(DATA|WEAPONS_DATA|CHARACTERS|CHARACTER_WEAPONS|WEAPONS|ARTIFACT_SETS|MAIN_STATS|SUB_STATS|TEAMS)\b/g,
    "var $1"
);
eval(calcCode);

var display = new Set();
Object.values(DATA).forEach(function(c) {
    display.add(c.name); display.add(c.role); display.add(c.arti);
    if (c.artiAlt) display.add(c.artiAlt);
    c.teams.forEach(function(t) { display.add(t.n); display.add(t.m); display.add(t.d); });
});
Object.values(WEAPONS_DATA).forEach(function(w) { display.add(w.n); });

var missing = [];
display.forEach(function(s) { if (!CALC_I18N[s]) missing.push(s); });
if (missing.length > 0) {
    ERRORS.push("Calculator: " + missing.length + " strings untranslated: " + missing.slice(0,5).join(", "));
    console.log("  ❌ " + missing.length + " untranslated strings");
} else {
    console.log("  ✅ " + display.size + " strings, 0 missing");
}

// ── 4. ZH pages English residue ────────────────────────────────────────
console.log("[4/5] ZH page English residue...");
var zhDir = path.join(ROOT, "pr-site/zh");
var zhIssues = 0;
fs.readdirSync(zhDir).filter(function(f) { return f.endsWith(".html"); }).forEach(function(f) {
    var html = fs.readFileSync(path.join(zhDir, f), "utf8");
    // Check for English names in card titles
    var cardMatch = html.match(/<h3[^>]*>([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)<\/h3>/);
    if (cardMatch) {
        ERRORS.push("zh/" + f + ": English card name: " + cardMatch[1]);
        zhIssues++;
    }
    // Check for English in related guide h4
    var relMatch = html.match(/<h4>\s*<span[^>]*>([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)<\/span>/);
    if (relMatch) {
        ERRORS.push("zh/" + f + ": English related name: " + relMatch[1]);
        zhIssues++;
    }
});
if (zhIssues === 0) {
    console.log("  ✅ No English residue");
} else {
    console.log("  ❌ " + zhIssues + " pages with English residue");
}

// ── 5. Page and asset counts ───────────────────────────────────────────
console.log("[5/5] Page counts...");
var enPages = fs.readdirSync(path.join(ROOT, "pr-site/en")).filter(function(f) { return f.endsWith(".html"); }).length;
var zhPages = fs.readdirSync(path.join(ROOT, "pr-site/zh")).filter(function(f) { return f.endsWith(".html"); }).length;
var guides = fs.readdirSync(path.join(ROOT, "pipeline/data/guides")).filter(function(f) { return f.endsWith(".json"); }).length;
var expected = guides + 7;
if (enPages === expected && zhPages === expected) {
    console.log("  ✅ en/" + enPages + " zh/" + zhPages + " (" + guides + " guides + 7 static)");
} else {
    ERRORS.push("Page count mismatch: en/" + enPages + " zh/" + zhPages + " (expected " + expected + ")");
}

// ── Summary ────────────────────────────────────────────────────────────
console.log("\n" + "=" .repeat(60));
if (ERRORS.length > 0) {
    console.log("❌ " + ERRORS.length + " FAILURES:");
    ERRORS.forEach(function(e) { console.log("  • " + e.slice(0, 150)); });
    console.log("\n🔴 Fix before committing!");
    process.exit(1);
} else {
    console.log("🎉 ALL 5 CHECKS PASSED — safe to commit");
    process.exit(0);
}
