# GenshinGuide — Deployment Guide

## Your Deployment Options

### Option A: You Deploy Yourself (full control, free)
Follow the steps below. Takes ~30 minutes one-time, then zero maintenance.

### Option B: I Deploy for You
Tell me "deploy it" and I'll do everything below. You just need to:
- Give me your GitHub username
- Tell me your chosen domain name

---

## Option A: Self-Deploy Steps

### Prerequisites
- GitHub account (free)
- Cloudflare account (free)
- Domain name (~$10/year, recommended: `buildguide.gg` or `teyvatguides.com`)

### Step 1: Push code to GitHub

```bash
cd /Users/liucs/CodeingZH/Cc_Projects/genshinguide-deliverables

# Initialize git if not done
git init
git add .
git commit -m "Initial: GenshinGuide site + pipeline"

# Create repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/genshinguide.git
git push -u origin main
```

### Step 2: Connect Cloudflare Pages

1. Go to https://dash.cloudflare.com/ → Workers & Pages → Pages
2. "Create a project" → "Connect to Git" → select your repo
3. Configure:
   - **Build command**: (leave empty)
   - **Build output directory**: `pr-site/`
4. Save and Deploy
5. In "Custom domains", add your domain
6. Cloudflare auto-provisions SSL (free)

### Step 3: Google Search Console

1. https://search.google.com/search-console → Add property
2. Verify via DNS TXT record (Cloudflare DNS panel)
3. Submit sitemap: `sitemap.xml`

### Step 4: Google Analytics (optional)

1. Create GA4 property at https://analytics.google.com/
2. Add the tracking snippet to every page's `<head>`
3. Measurement ID format: `G-XXXXXXXXXX`

### Step 5: Set up daily data sync (one-time)

The daily sync workflow (`.github/workflows/daily-sync.yml`) runs automatically.
No secrets needed — it only fetches free public data. Zero configuration required.

---

## After Deployment: Content Updates

### Adding a new character guide
```bash
cd pipeline/
python make.py new {character_id}
# Edit data/guides/{character_id}.json
python make.py render {character_id}
# Review in browser
python make.py publish {character_id}
git push  # or let publish.py push for you
```

### Updating existing guides for a new version
```bash
cd pipeline/
python make.py sync        # pull latest game data
# Check which characters changed, update their JSONs
python make.py update-all  # re-render all
# Review, then:
git add . && git commit -m "version update to X.Y" && git push
```

### Just syncing game data (CI does this daily)
```bash
cd pipeline/
python make.py sync
```

---

## Site Structure After Deployment

```
yourdomain.com/
  index.html              ← Homepage
  guides.html             ← All guides listing
  guide-furina.html       ← Individual guide
  guide-raiden.html       ← Individual guide
  ... (all character guides)
  calculator.html         ← Build calculator
  pricing.html            ← Pricing page
  pipeline.html           ← Pipeline info
  sitemap.xml             ← SEO
  robots.txt              ← SEO
```

Cloudflare Pages auto-deploys on every `git push`. No build step needed — pure static HTML.

---

## Monthly Costs

| Item | Cost |
|------|------|
| Domain | ~$0.83/mo ($10/year) |
| Cloudflare Pages | $0 (unlimited bandwidth) |
| GitHub | $0 (public repo) |
| Content pipeline | $0 (free APIs only) |
| **Total** | **~$0.83/month** |

---

## Emergency: Site Goes Down?

Cloudflare Pages has 99.9% uptime. If the site goes down:
1. Check https://www.cloudflarestatus.com/
2. Check your domain hasn't expired
3. Check the GitHub repo is still accessible
4. `git push` triggers redeploy

All content is static files — no database to crash, no server to maintain.
