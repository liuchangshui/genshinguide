# GenshinGuide — Deployment Instructions

## Prerequisites
- A GitHub/GitLab account
- Domain name (recommended: use independent brand name like `buildguide.gg`, `teyvatguides.com`)
- Cloudflare account (free tier)

## Step 1: Register Domain
1. Buy domain from registrar (Namecheap, Cloudflare, etc.)
2. Recommended: `buildguide.gg` or `teyvatguides.com`
3. Avoid `genshin` as primary domain (trademark separation)
4. Set nameservers to Cloudflare's (if using Cloudflare registrar, this is automatic)

## Step 2: Set Up Git Repository
```bash
cd /Users/liucs/CodeingZH/Cc_Projects/genshinguide-deliverables
git init
git add pr-site/
git commit -m "Initial commit: GenshinGuide static site"
git remote add origin https://github.com/YOUR_USERNAME/genshinguide.git
git push -u origin main
```

## Step 3: Cloudflare Pages
1. Go to https://dash.cloudflare.com/
2. Navigate to **Workers & Pages** > **Pages**
3. Click **Create a project** > **Connect to Git**
4. Select your GitHub/GitLab repository
5. Configure:
   - **Build command**: (leave empty — static site)
   - **Build output directory**: `pr-site/`
   - **Root directory**: (leave empty)
6. Click **Save and Deploy**
7. In **Custom domains**, add your domain
8. Cloudflare automatically provisions SSL

## Step 4: Google Search Console
1. Go to https://search.google.com/search-console
2. Add property (Domain or URL prefix)
3. Verify ownership:
   - Option A: DNS TXT record (recommended — permanent)
   - Option B: HTML file upload (add to pr-site/, then git push to deploy)
4. Submit sitemap: go to **Sitemaps** > enter `sitemap.xml` > **Submit**
5. Use **URL Inspection** to request indexing for key pages

## Step 5: Google Analytics 4
1. Go to https://analytics.google.com/
2. Create account > Create property (Google Analytics 4)
3. Copy Measurement ID (format: `G-XXXXXXXXXX`)
4. Add the GA4 snippet to `<head>` of every HTML page:
```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

## Step 6: Verify Everything Works
- [ ] Domain loads all pages (index, guides, calculator, pricing)
- [ ] All guide pages load without errors
- [ ] CSS styles render correctly (dark theme, element colors)
- [ ] Language toggle works (EN/中文)
- [ ] Calculator works (select character → shows build)
- [ ] GSC shows sitemap as "Success"
- [ ] GSC shows pages being indexed
- [ ] GA4 realtime shows visitor data
- [ ] HTTPS works (SSL auto-provisioned by Cloudflare)

## Cost Summary
| Item | Cost |
|------|------|
| Domain | ~$10/year |
| Cloudflare Pages | $0 (free tier) |
| Google Analytics | $0 |
| Google Search Console | $0 |
| **Total monthly** | **~$0.83 (domain amortized)** |
