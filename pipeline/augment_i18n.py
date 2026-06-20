#!/usr/bin/env python3
"""
One-time script: add weapon/artifact name translations to i18n.json,
add wpn_key to each weapon in guide JSONs, add character name keys.

Run once, then rebuild with build.py.
"""
import json, os, re

ROOT = '/Users/liucs/CodeingZH/Cc_Projects/genshinguide-deliverables'

# ── Weapon name → i18n key + Chinese translation ──────────────────────
WEAPON_MAP = {
    # 5-star weapons
    "A Thousand Floating Dreams": ("wpn_thousand_floating_dreams", "千夜浮梦"),
    "Amos' Bow": ("wpn_amos_bow", "阿莫斯之弓"),
    "Aqua Simulacra": ("wpn_aqua_simulacra", "若水"),
    "Aquila Favonia": ("wpn_aquila_favonia", "风鹰剑"),
    "Crimson Moon's Semblance": ("wpn_crimson_moons_semblance", "赤月之形"),
    "Engulfing Lightning": ("wpn_engulfing_lightning", "薙草之稻光"),
    "Freedom-Sworn": ("wpn_freedom_sworn", "苍古自由之誓"),
    "Hunter's Path": ("wpn_hunters_path", "猎人之径"),
    "Mistsplitter Reforged": ("wpn_mistsplitter_reforged", "雾切之回光"),
    "Primordial Jade Cutter": ("wpn_primordial_jade_cutter", "磐岩结绿"),
    "Primordial Jade Winged-Spear": ("wpn_primordial_jade_winged_spear", "和璞鸢"),
    "Skyward Blade": ("wpn_skyward_blade", "天空之刃"),
    "Splendor of Tranquil Waters": ("wpn_splendor_of_tranquil_waters", "静水流涌之辉"),
    "Staff of Homa": ("wpn_staff_of_homa", "护摩之杖"),
    "Tome of the Eternal Flow": ("wpn_tome_of_the_eternal_flow", "万世流涌大典"),
    # 4-star weapons
    "Amenoma Kageuchi R5": ("wpn_amenoma_kageuchi", "天目影打刀R5"),
    "Black Tassel": ("wpn_black_tassel", "黑缨枪"),
    "Blackcliff Longsword": ("wpn_blackcliff_longsword", "黑岩长剑"),
    "Blackcliff Pole R5": ("wpn_blackcliff_pole", "黑岩刺枪R5"),
    "Cinnabar Spindle R5": ("wpn_cinnabar_spindle", "辰砂之纺锤R5"),
    "Deathmatch": ("wpn_deathmatch", "决斗之枪"),
    "Deathmatch R5": ("wpn_deathmatch_r5", "决斗之枪R5"),
    "Dragon's Bane R5": ("wpn_dragons_bane", "匣里灭辰R5"),
    "Favonius Lance": ("wpn_favonius_lance", "西风长枪"),
    "Favonius Sword": ("wpn_favonius_sword", "西风剑"),
    "Favonius Warbow": ("wpn_favonius_warbow", "西风猎弓"),
    "Festering Desire": ("wpn_festering_desire", "腐殖之剑"),
    "Finale of the Deep": ("wpn_finale_of_the_deep", "海渊终曲"),
    "Fleuve Cendre Ferryman R5": ("wpn_fleuve_cendre_ferryman", "灰河渡手R5"),
    "Hamayumi R5": ("wpn_hamayumi", "破魔之弓R5"),
    "Harbinger of Dawn R5": ("wpn_harbinger_of_dawn", "黎明神剑R5"),
    "Iron Sting R5": ("wpn_iron_sting", "铁蜂刺R5"),
    "Magic Guide R5": ("wpn_magic_guide", "魔导绪论R5"),
    "Prototype Amber R5": ("wpn_prototype_amber", "试作金珀R5"),
    "Prototype Crescent R5": ("wpn_prototype_crescent", "试作澹月R5"),
    "Sacrificial Bow": ("wpn_sacrificial_bow", "祭礼弓"),
    "Sacrificial Fragments": ("wpn_sacrificial_fragments", "祭礼残章"),
    "Sacrificial Jade R5": ("wpn_sacrificial_jade", "祭礼玉R5"),
    "Sapwood Blade R5": ("wpn_sapwood_blade", "原木刀R5"),
    "The Catch R5": ("wpn_the_catch", "「渔获」R5"),
    "The Stringless": ("wpn_the_stringless", "绝弦"),
    "The Widsith": ("wpn_the_widsith", "流浪乐章"),
    "White Tassel": ("wpn_white_tassel", "白缨枪"),
    "White Tassel R5": ("wpn_white_tassel_r5", "白缨枪R5"),
    "Xiphos' Moonlight": ("wpn_xiphos_moonlight", "西福斯的月光"),
}

# ── Artifact set name → i18n key + Chinese ────────────────────────────
ARTIFACT_MAP = {
    "4pc Archaic Petra": ("arti_archaic_petra", "悠古的磐岩4件套"),
    "4pc Blizzard Strayer": ("arti_blizzard_strayer", "冰风迷途的勇士4件套"),
    "4pc Crimson Witch of Flames": ("arti_crimson_witch", "炽烈的炎之魔女4件套"),
    "4pc Deepwood Memories": ("arti_deepwood_memories", "深林的记忆4件套"),
    "4pc Emblem of Severed Fate": ("arti_emblem_of_severed_fate", "绝缘之旗印4件套"),
    "4pc Fragment of Harmonic Whimsy": ("arti_fragment_harmonic_whimsy", "谐律异想断章4件套"),
    "4pc Gilded Dreams": ("arti_gilded_dreams", "饰金之梦4件套"),
    "4pc Golden Troupe": ("arti_golden_troupe", "黄金剧团4件套"),
    "4pc Heart of Depth": ("arti_heart_of_depth", "沉沦之心4件套"),
    "4pc Husk of Opulent Dreams": ("arti_husk_of_opulent_dreams", "华馆梦醒形骸记4件套"),
    "4pc Instructor": ("arti_instructor", "教官4件套"),
    "4pc Marechaussee Hunter": ("arti_marechaussee_hunter", "逐影猎人4件套"),
    "4pc Noblesse Oblige": ("arti_noblesse_oblige", "昔日宗室之仪4件套"),
    "4pc Shimenawa's Reminiscence": ("arti_shimenawa_reminiscence", "追忆之注连4件套"),
    "4pc Tenacity of the Millelith": ("arti_tenacity_of_millelith", "千岩牢固4件套"),
    "4pc Vermillion Hereafter": ("arti_vermillion_hereafter", "辰砂往生录4件套"),
    "4pc Viridescent Venerer": ("arti_viridescent_venerer", "翠绿之影4件套"),
    "4pc Wanderer's Troupe": ("arti_wanderers_troupe", "流浪大地的乐团4件套"),
}

# ── Character name translations ───────────────────────────────────────
CHAR_NAMES = {
    "albedo": "阿贝多", "arlecchino": "阿蕾奇诺", "ayaka": "神里绫华",
    "bennett": "班尼特", "furina": "芙宁娜", "ganyu": "甘雨",
    "hutao": "胡桃", "kazuha": "枫原万叶", "nahida": "纳西妲",
    "neuvillette": "那维莱特", "raiden": "雷电将军", "xiangling": "香菱",
    "xiao": "魈", "yelan": "夜兰", "zhongli": "钟离",
}

# ── 1. Update i18n.json ───────────────────────────────────────────────
i18n_path = os.path.join(ROOT, 'pipeline/data/i18n.json')
with open(i18n_path, 'r') as f:
    i18n = json.load(f)

# Add weapon translations
if 'wpn' not in i18n:
    i18n['wpn'] = {}
for eng_name, (key, zh_name) in WEAPON_MAP.items():
    i18n['wpn'][key] = {"en": eng_name, "zh": zh_name}

# Add artifact translations
if 'arti_names' not in i18n:
    i18n['arti_names'] = {}
for eng_name, (key, zh_name) in ARTIFACT_MAP.items():
    i18n['arti_names'][key] = {"en": eng_name, "zh": zh_name}

# Add character name keys to existing character sections
for char_id, zh_name in CHAR_NAMES.items():
    if char_id in i18n:
        if 'name' not in i18n[char_id]:
            # Get English display name from existing data or capitalize
            en_name = char_id.capitalize()
            if char_id == 'hutao': en_name = 'Hu Tao'
            elif char_id == 'raiden': en_name = 'Raiden Shogun'
            elif char_id == 'kazuha': en_name = 'Kaedehara Kazuha'
            elif char_id == 'ayaka': en_name = 'Kamisato Ayaka'
            i18n[char_id]['name'] = {"en": en_name, "zh": zh_name}
            print(f"  Added {char_id}.name: {en_name} → {zh_name}")

with open(i18n_path, 'w') as f:
    json.dump(i18n, f, indent=2, ensure_ascii=False)
print(f"i18n.json: {len(WEAPON_MAP)} weapons + {len(ARTIFACT_MAP)} artifacts + {len(CHAR_NAMES)} character names")

# ── 2. Add wpn_key to each weapon in guide JSONs ──────────────────────
guide_dir = os.path.join(ROOT, 'pipeline/data/guides')
updated = 0
for fname in os.listdir(guide_dir):
    if not fname.endswith('.json'):
        continue
    path = os.path.join(guide_dir, fname)
    with open(path, 'r') as f:
        guide = json.load(f)
    changed = False
    for w in guide.get('weapons', []):
        name = w.get('name', '')
        if name in WEAPON_MAP:
            key, _ = WEAPON_MAP[name]
            if w.get('wpn_key') != key:
                w['wpn_key'] = key
                changed = True
    if changed:
        with open(path, 'w') as f:
            json.dump(guide, f, indent=2, ensure_ascii=False)
        updated += 1

print(f"Guide JSONs updated: {updated} files with wpn_key fields")
print("\nDone. Run build.py to regenerate.")
