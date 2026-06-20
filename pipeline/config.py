"""
GenshinGuide Content Pipeline — Central Configuration
======================================================
No AI APIs. Data comes from genshin.jmp.blue (free, public).
Content is written manually using game data as reference.
"""

import os

# ---- Data Source (free, no API key needed) ----
DATA_API_BASE = "https://genshin.jmp.blue"
DATA_ENDPOINTS = {
    "characters": "/characters",
    "weapons":    "/weapons",
    "artifacts":  "/artifacts",
}

# ---- Local Paths (relative to pipeline/ directory) ----
CACHE_DIR = "data/cache"
TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "templates/guide_template.html"
OUTPUT_DIR = "../pr-site"
I18N_FILE = "../pr-site/js/i18n.js"
CALCULATOR_FILE = "../pr-site/js/calculator.js"
SITEMAP_FILE = "../pr-site/sitemap.xml"
GUIDES_INDEX = "../pr-site/guides.html"

# ---- Game Version ----
CURRENT_VERSION = "5.6"

# ---- Character Priority (P0 = search-volume order) ----
P0_CHARACTERS = ["furina", "arlecchino", "neuvillette", "raiden", "bennett"]

# ---- Element mapping ----
ELEMENT_MAP = {
    "Electro": "electro",
    "Pyro":   "pyro",
    "Hydro":  "hydro",
    "Dendro": "dendro",
    "Anemo":  "anemo",
    "Geo":    "geo",
    "Cryo":   "cryo",
}

ELEMENT_COLORS = {
    "electro": "#b388ff",
    "pyro":    "#ff5252",
    "hydro":   "#448aff",
    "dendro":  "#69f0ae",
    "anemo":   "#4db6ac",
    "geo":     "#ff9100",
    "cryo":    "#18ffff",
}
