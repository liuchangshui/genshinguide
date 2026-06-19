# GenshinGuide — Content Pipeline

No AI APIs. No monthly costs. Data comes from genshin.jmp.blue (free, public).

## Architecture

```
pipeline/
  config.py          — Central configuration (no API keys needed)
  sync_wiki.py       — Fetch game data from genshin.jmp.blue → local cache
  generate.py        — Create guide scaffold JSON + render HTML from template
  verify.py          — Deterministic validation (schema, ranges, required fields)
  publish.py         — Post-review publishing (update indexes + git push)
  templates/
    guide_template.html  — Jinja2 template for guide pages
  data/
    cache/            — Local JSON cache of game data
    guides/           — Guide content JSON files (human-edited)
  requirements.txt   — Python dependencies (requests, jinja2)

../.github/workflows/
  daily-sync.yml     — GitHub Actions: daily auto-sync of game data
```

## How It Works

### 1. Sync game data (automatic, daily)
```bash
python sync_wiki.py
```
Fetches character/weapon/artifact data from genshin.jmp.blue → caches to `data/cache/`. Zero cost, zero API keys.

### 2. Create a new guide
```bash
# Step A: Generate a scaffold JSON with pre-filled game data
python generate.py --character furina --scaffold

# Step B: Edit the JSON file (data/guides/furina.json)
# Fill in weapons, artifacts, teams, rotation, mistakes, etc.
# All weapon/artifact options are listed in the scaffold for reference.

# Step C: Render the HTML
python generate.py --character furina --render

# Step D: Human review the HTML → publish
python publish.py --character furina
```

### 3. Update an existing guide
Edit `data/guides/{character}.json` → run `python generate.py --character {id} --render` → review → publish.

### 4. Daily sync (CI)
Push to GitHub → GitHub Actions runs `sync_wiki.py` daily at 00:07 UTC.
If game data changes, you get a commit notification. Then you decide whether
to regenerate affected guides.

## Adding a New Character Guide (Workflow)

1. `python sync_wiki.py` — ensure data is cached
2. `python generate.py --character {id} --scaffold` — create scaffold
3. Edit `data/guides/{id}.json` — write the actual guide content
   - Use `_available_weapons` and `_available_artifacts` in the scaffold as reference
   - Fill in TL;DR, weapons, artifacts, teams, talents, rotation, mistakes
   - Set accurate weapon ATK and substat values
4. `python generate.py --character {id} --render` — generate HTML
5. Open the HTML in browser, review content quality
6. `python publish.py --character {id}` — update indexes and commit

## Costs

| Item | Cost |
|------|------|
| genshin.jmp.blue API | $0 (free, open) |
| Python scripts | $0 |
| GitHub Actions | $0 (public repo) |
| **Total** | **$0/month** |

## Dependencies

```bash
pip install -r requirements.txt
# requests, jinja2 (that's it)
```
