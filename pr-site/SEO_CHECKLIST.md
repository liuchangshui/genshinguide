# GenshinGuide — SEO Pre-Launch Checklist

## Completed (2026-06-18)

### Legal Compliance
- [x] All 14 HTML footers updated to: "Fan-made project. Not affiliated with HoYoverse. Game data (c) Cognosphere."
- [x] i18n.js footer.copyright translations updated (EN + ZH)
- [x] No "Genshin Pro" branding found (already using correct naming)

### SEO Files
- [x] sitemap.xml created (14 URLs, correct priorities)
- [x] robots.txt created (allow all, sitemap pointer)
- [x] Placeholder guide meta descriptions fixed (7 guides were showing Raiden's weapons: Engulfing Lightning → now character-specific)

### Content Status
| Guide | Status | Meta | Content |
|-------|--------|------|---------|
| guide-raiden.html | ✅ Complete | ✅ Raiden-specific | ✅ Full content |
| guide-xiangling.html | ✅ Complete | ✅ Xiangling-specific | ✅ Full content |
| guide-furina.html | 🔄 In Progress | — | — |
| guide-arlecchino.html | 🔄 In Progress | — | — |
| guide-neuvillette.html | 🔄 In Progress | — | — |
| guide-hutao.html | 🟡 Placeholder | ✅ Fixed (Homa/Dragon's Bane) | Placeholder — needs pipeline |
| guide-ayaka.html | 🟡 Placeholder | ✅ Fixed (Mistsplitter/Amenoma) | Placeholder — needs pipeline |
| guide-yelan.html | 🟡 Placeholder | ✅ Fixed (Aqua/Favonius) | Placeholder — needs pipeline |
| guide-nahida.html | 🟡 Placeholder | ✅ Fixed (Floating Dreams/Sac Frag) | Placeholder — needs pipeline |
| guide-kazuha.html | 🟡 Placeholder | ✅ Fixed (Freedom-Sworn/Iron Sting) | Placeholder — needs pipeline |
| guide-zhongli.html | 🟡 Placeholder | ✅ Fixed (Homa/Black Tassel) | Placeholder — needs pipeline |
| guide-albedo.html | 🟡 Placeholder | ✅ Fixed (Cinnabar/Harbinger) | Placeholder — needs pipeline |

## Pre-Launch Verification
- [ ] Add GA4 measurement ID to all pages
- [ ] Replace {{DOMAIN}} in sitemap.xml with actual domain
- [ ] Replace {{DOMAIN}} in robots.txt with actual domain
- [ ] Add Open Graph tags to index.html
- [ ] Add Open Graph tags to all guide pages
- [ ] Verify schema.org JSON-LD with Google Rich Results Test
- [ ] Run HTML validation (W3C Validator) on all pages
- [ ] Check mobile responsiveness (all pages at 375px width)
- [ ] Test language toggle (EN/中文) on every page
- [ ] Verify all internal links work (no 404s)
- [ ] Create og-default.png (1200x630 social share image)

## Post-Launch Monitoring
- [ ] Submit sitemap to Google Search Console
- [ ] Request indexing for 3 complete guides (Raiden, Xiangling, Furina)
- [ ] Monitor GSC for indexing status (daily for first 2 weeks)
- [ ] Monitor GSC for search queries and impressions
- [ ] Set up GA4 conversion events: calculator_use, pro_cta_click, email_subscribe
- [ ] Check Core Web Vitals in GSC (should be excellent — pure static HTML)

## Placeholder Guide Strategy
The 7 placeholder guides currently have correct meta descriptions but the body content is still Raiden's. Strategy:
1. Mark them as noindex temporarily? NO — their meta is now correct and Google should index them as "coming soon"
2. Replace content via Pipeline in Phase 1 (generate.py will overwrite them)
3. The "(Coming Soon)" tag in titles is honest and Google won't penalize it
4. Once Pipeline is built, regenerate all 7 placeholders with real content
