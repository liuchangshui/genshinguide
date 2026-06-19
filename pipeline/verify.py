"""
verify.py — Validate guide data against source material.

Now only uses hard (deterministic) checks — no LLM API calls.
"""

import config

EXPECTED_GUIDE_KEYS = [
    "tldr_weapon", "tldr_artifact", "tldr_team", "tldr_key_stats",
    "intro", "weapon_bottom_line", "weapons",
    "best_artifact", "artifact_why", "artifact_alt",
    "main_stats", "sub_priority", "teams",
    "talent_priority", "rotation_title", "rotation_code",
    "mistakes", "pro_teaser_code", "seo",
]

VALID_ELEMENTS = {"electro", "pyro", "hydro", "dendro", "anemo", "geo", "cryo"}
WEAPON_ATK_RANGE = (200, 750)
WEAPON_RARITY_RANGE = (3, 5)


def verify_guide(guide_data: dict, character_id: str = "",
                 expected_element: str = "electro") -> dict:
    """
    Run deterministic schema and range validation on guide data.
    Returns {"errors": [...], "warnings": [...], "passed": bool}
    """
    errors = []
    warnings = []

    print(f"  [VERIFY] {character_id} — running hard checks...")

    # Schema: required keys
    for key in EXPECTED_GUIDE_KEYS:
        if key not in guide_data:
            errors.append(f"Missing required key: {key}")

    # Weapons validation
    weapons = guide_data.get("weapons", [])
    if not weapons:
        errors.append("No weapons in guide")
    for w in weapons:
        atk = w.get("atk", 0)
        rarity = w.get("rarity", 0)
        name = w.get("name", "unknown")
        if not (WEAPON_ATK_RANGE[0] <= atk <= WEAPON_ATK_RANGE[1]):
            errors.append(f"Weapon '{name}' suspicious ATK: {atk}")
        if not (WEAPON_RARITY_RANGE[0] <= rarity <= WEAPON_RARITY_RANGE[1]):
            errors.append(f"Weapon '{name}' invalid rarity: {rarity}")

    # Teams validation
    teams = guide_data.get("teams", [])
    if len(teams) < 2:
        errors.append(f"Too few teams: {len(teams)} (need >= 2)")
    for team in teams:
        members = team.get("members", "")
        member_count = len([m for m in members.split("+") if m.strip()])
        if member_count < 2:
            errors.append(f"Team '{team.get('name', 'unknown')}' too few members")

    # Element validation
    if expected_element not in VALID_ELEMENTS:
        errors.append(f"Invalid element: {expected_element}")

    # Talent priority
    talents = guide_data.get("talent_priority", [])
    if len(talents) != 3:
        warnings.append(f"Expected 3 talent priorities, got {len(talents)}")

    # SEO
    seo = guide_data.get("seo", {})
    if not seo:
        errors.append("Missing SEO section")
    else:
        title = seo.get("title", "")
        desc = seo.get("description", "")
        if len(title) < 20:
            warnings.append(f"SEO title too short: {len(title)} chars")
        if len(desc) < 80:
            warnings.append(f"SEO description too short: {len(desc)} chars")

    passed = len(errors) == 0

    if errors:
        for e in errors:
            print(f"    ❌ {e}")
    for w in warnings:
        print(f"    ⚠️  {w}")
    print(f"  [VERIFY] {'PASSED' if passed else 'FAILED'}")

    return {"errors": errors, "warnings": warnings, "passed": passed}
