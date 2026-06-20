#!/usr/bin/env python3
"""
Generate calc-i18n.js from i18n.json — comprehensive character/weapon/
artifact/team translations for the calculator page.

Called by build.py during each build.
"""
import json, os, re, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUTPUT_DIR = os.path.join(ROOT, 'pr-site')


def generate(i18n):
    """Main generation function. Returns number of entries."""
    calc = {}

    def add(en, zh):
        calc[en] = [en, zh]

    # ── 1. Character names ────────────────────────────────────────────
    char_ids = ['raiden','hutao','yelan','nahida','kazuha','zhongli','furina','arlecchino',
                'neuvillette','bennett','xiangling','ayaka','albedo','ganyu','xiao']
    char_zh = {}
    for cid in char_ids:
        if cid in i18n and 'name' in i18n[cid]:
            en, zh = i18n[cid]['name']['en'], i18n[cid]['name']['zh']
            add(en, zh)
            char_zh[en] = zh

    # ── 2. Weapon names + variants ────────────────────────────────────
    for val in i18n.get('wpn', {}).values():
        en, zh = val['en'], val['zh']
        add(en, zh)
        if en.endswith(' R5'):
            add(en[:-3], zh.replace('R5', ''))
        if 'R5' in en:
            base = en.replace(' R5', '').replace('R5', '')
            if base != en:
                add(base, zh.replace('R5', '').strip())

    # ── 3. Artifact names + variants ───────────────────────────────────
    for val in i18n.get('arti_names', {}).values():
        en, zh = val['en'], val['zh']
        add(en, zh)
        for prefix in ['4pc ', '4-Piece ']:
            if en.startswith(prefix):
                add(en[len(prefix):], zh.replace('4件套', ''))

    # Additional artifact names (without 4pc prefix)
    arti_alts = {
        "Thundering Fury / Noblesse": "如雷的盛怒 / 昔日宗室之仪",
        "Shimenawa's Reminiscence": "追忆之注连",
        "Noblesse Oblige / Heart of Depth": "昔日宗室之仪 / 沉沦之心",
        "Gilded Dreams": "饰金之梦",
        "None — 4pc VV is mandatory": "无 — 翠绿之影4件套为必选",
        "Archaic Petra / Noblesse": "悠古的磐岩 / 昔日宗室之仪",
        "Tenacity of the Millelith (support)": "千岩牢固（辅助向）",
        "Gladiator's Finale": "角斗士的终幕礼",
        "Heart of Depth (budget)": "沉沦之心（过渡）",
        "Instructor (budget EM buff)": "教官（过渡精通拐）",
        "Crimson Witch (Vape focus)": "炽烈的炎之魔女（蒸发向）",
        "None — 4pc BS is mandatory": "无 — 冰风迷途的勇士4件套为必选",
        "Blizzard Strayer (Freeze)": "冰风迷途的勇士（永冻）",
        "Marechaussee Hunter (with Furina)": "逐影猎人（配芙宁娜）",
        "Golden Troupe": "黄金剧团", "Deepwood Memories": "深林的记忆",
        "Emblem of Severed Fate": "绝缘之旗印",
        "Crimson Witch of Flames": "炽烈的炎之魔女",
        "Blizzard Strayer": "冰风迷途的勇士",
        "Wanderer's Troupe": "流浪大地的乐团",
        "Fragment of Harmonic Whimsy": "谐律异想断章",
        "Husk of Opulent Dreams": "华馆梦醒形骸记",
        "Marechaussee Hunter": "逐影猎人",
        "Tenacity of the Millelith": "千岩牢固",
        "Viridescent Venerer": "翠绿之影",
        "Vermillion Hereafter": "辰砂往生录",
        "Noblesse Oblige": "昔日宗室之仪", "Heart of Depth": "沉沦之心",
    }
    for en, zh in arti_alts.items():
        if en not in calc:
            add(en, zh)

    # ── 4. Character roles ─────────────────────────────────────────────
    for en, zh in {
        'Sub DPS / Battery': '副C / 充能辅助', 'Main DPS': '主C',
        'Sub DPS / Support': '副C / 辅助', 'Sub DPS / Buffer': '副C / 增伤辅助',
        'Support / CC': '辅助 / 聚怪', 'Shield / Support': '护盾 / 辅助',
        'Support / Healer': '辅助 / 治疗', 'Sub DPS': '副C',
    }.items():
        add(en, zh)

    # ── 5. Team names from i18n character sections ─────────────────────
    for cid in char_ids:
        if cid not in i18n:
            continue
        for i in range(1, 6):
            for suffix in ['_name', '_desc']:
                key = f'team{i}{suffix}'
                if key in i18n[cid]:
                    add(i18n[cid][key]['en'], i18n[cid][key]['zh'])

    # ── 6. Team member strings — auto-translate ────────────────────────
    abbrev_map = {'XL': '香菱', 'XQ': '行秋', 'Arle': '阿蕾奇诺', 'Neu': '那维莱特',
                  'Raiden': '雷电将军', 'Yae': '八重神子', 'Kazuha': '枫原万叶'}
    team_strings = [
        "Xiangling + Xingqiu + Bennett", "Sara(C6) + Kazuha + Bennett",
        "Nahida + Yelan/Xingqiu + Healer", "Yelan + Xingqiu + Zhongli",
        "Yelan + Kazuha + Bennett", "Nahida + Yelan + Flex",
        "Hu Tao + Xingqiu + Zhongli", "Nahida + Kuki + Flex",
        "Kokomi + Kazuha + Xingqiu", "Yelan/Xingqiu + Kuki/Raiden + Flex",
        "Yae/Fischl + Kazuha + Flex", "Nilou + Kokomi + Flex Hydro/Dendro",
        "Childe + Xiangling + Bennett", "Ayaka + Kokomi + Shenhe",
        "Yae/Fischl + Nahida + Flex", "Itto/Albedo + Gorou + Flex",
        "Hu Tao/Yoimiya + Xingqiu + Yelan", "Ningguang + Bennett + Xiangling",
        "Furina + Yelan + Hu Tao + Jean", "Furina + Xiao + Faruzan + Xianyun",
        "Furina + Neuvillette + Kazuha + Baizhu",
        "Arle + Yelan + Kazuha + Bennett", "Arle + Xiangling + Kazuha + Bennett",
        "Arle + Fischl + Chevreuse + Bennett", "Neu + Furina + Kazuha + Baizhu",
        "Neu + Fischl + Kazuha + Zhongli", "Neu + Nahida + Raiden + Flex",
        "XL + XQ + Raiden/Childe + Bennett", "Ganyu + Xiangling + Zhongli + Bennett",
        "Any ATK DPS + Bennett + Kazuha + Flex", "XL + Bennett + XQ + Raiden/Childe",
        "Ganyu + XL + Bennett + Zhongli", "XL + Chevreuse + Fischl + Bennett",
        "Ayaka + Kokomi + Kazuha + Shenhe", "Ayaka + Mona + Sucrose + Diona",
        "Ayaka + Shenhe + Kazuha + Layla", "Itto + Albedo + Gorou + Zhongli",
        "Albedo + Zhongli + any DPS duo", "Navia + Albedo + Bennett + XL",
        "Ganyu + Kazuha + Mona + Diona", "Ganyu + Nahida + Bennett + Zhongli",
        "Xiao + Faruzan + Furina + Xianyun", "Xiao + Faruzan + Bennett + Zhongli",
        "Xiao + Albedo + Zhongli + Jean/Bennett",
        "Yelan + Nahida + Kuki/Raiden + Flex",
        "Raiden + Xiangling + Bennett", "Hu Tao + Furina + Yelan + Jean/Healer",
        "Neuvillette + Furina + Kazuha + Baizhu",
        "Neuvillette + Furina + Kazuha + Xilonen",
        "Noelle(C6) + Furina + Gorou + Flex",
        "Neuvillette + Fischl + Sucrose + Zhongli",
        "Neuvillette + Fischl + Kazuha + Beidou",
    ]
    for s in team_strings:
        if s in calc:
            continue
        parts = re.split(r'\s*\+\s*', s)
        zh_parts = []
        for p in parts:
            p = p.strip()
            if p in abbrev_map:
                zh_parts.append(abbrev_map[p])
            elif p in char_zh:
                zh_parts.append(char_zh[p])
            elif p in calc:
                zh_parts.append(calc[p][1])
            else:
                found = False
                for en_name, zh_name in char_zh.items():
                    if en_name in p or p in en_name:
                        zh_parts.append(p.replace(en_name, zh_name))
                        found = True
                        break
                if not found:
                    zh_parts.append(p)
        add(s, ' + '.join(zh_parts))

    # ── 7. Team descriptions ──────────────────────────────────────────
    desc_map = {
        "High ST + AoE, consistent rotations": "高额对单+对群，循环稳定",
        "Maximum burst DMG, needs C6 Sara": "极限爆发伤害，需要满命九条",
        "EM build, strongest reaction team": "精通流，最强反应队",
        "Comfortable, consistent high ST damage": "舒适稳定，高额对单伤害",
        "Higher ceiling, less shielding": "上限更高，护盾较少",
        "AoE focused, Dendro reaction team": "对群特化，草反应队",
        "Best Hu Tao support, high off-field DPS": "胡桃最佳辅助，高额后台伤害",
        "Strong reaction core, Yelan drives blooms": "强力反应核心，夜兰驱动绽放",
        "Full hydro team, high ER refund": "纯水队，高额充能返还",
        "Top meta team, high floor damage": "版本答案队伍，基础伤害高",
        "Quicken-based, scales with EM & CRIT": "激化反应，精通与双爆双修",
        "Pure bloom, massive AoE damage": "纯绽放，巨额对群伤害",
        "Classic vaporize team, Kazuha double swirl": "经典蒸发队，万叶双扩散",
        "Group + VV shred + elemental DMG buff": "聚怪+风套减抗+元素增伤",
        "Anemo driver, swirl electro for aggravate": "风系驾驶员，扩散雷元素触发激化",
        "Mono geo, strongest shield + resonance": "纯岩队，最强护盾+双岩共鸣",
        "Fits any team, 100% uptime shield": "百搭任意队伍，护盾100%覆盖率",
        "Quick swap, high burst DMG Zhongli": "速切爆发，钟离大招伤害流",
        "HP drain synergy, massive DMG amp": "血量消耗协同，巨额伤害放大",
        "HP-drain keeps Hu Tao <50%, team-wide heal": "血量消耗维持胡桃半血以下，全队治疗",
        "Fanfare stacks + Anemo plunge buff": "气氛值叠加+风系下落增伤",
        "Highest ceiling, consistent Vaporize": "伤害上限最高，稳定蒸发",
        "Raw Pyro DMG, no reaction reliance": "纯火输出，不依赖反应",
        "Overload comp, high AoE clear": "超载队，对群清怪强力",
        "Premium team, Furina Hydro resonance": "顶配队伍，芙宁娜水共鸣",
        "Electro-charged, shield essential at C0": "感电反应，零命必须带盾",
        "HP-scaling hyperbloom driver": "生命值驱动的超绽放驾驶员",
        "Core of almost every meta team": "几乎所有版本队伍的核心",
        "ATK buff + Pyro application": "攻击增益+挂火",
        "Universal ATK buffer, fits everywhere": "万能攻击拐，百搭任何队伍",
        "Snapshot Bennett buff, top-tier off-field": "锁定班尼特增益，顶级后台输出",
        "Pyro enabler for Ganyu charged shots": "甘雨蓄力射击的火元素启动器",
        "Overload meta, Chevreuse shred": "超载版本答案，夏沃蕾减抗",
        "Best Ayaka team, full Cryo shred": "神里绫华最强队伍，全冰减抗",
        "F2P-friendly, Mona Omen buff": "零氪友好，莫娜星异增伤",
        "For unfreezable boss enemies": "针对无法冻结的Boss敌人",
        "Geo resonance, full DEF scaling": "双岩共鸣，纯防御力加成",
        "Geo resonance + shield shred": "双岩共鸣+护盾减抗",
        "Crystallize shard generator": "结晶碎片生成器",
        "Shielded charge shots, 1.5x Melt": "护盾保护蓄力，1.5倍融化",
        "AoE freeze, quadratic scaling burst": "对群永冻，大招平方衰减",
        "Consistent burning Pyro aura": "稳定燃烧火附着",
        "Best team — Fanfare + Anemo buff": "最强配队——气氛值+风元素增益",
        "Shield + ATK buff, reliable": "护盾+攻击增益，稳定可靠",
        "Geo resonance alternative": "双岩共鸣替代方案",
    }
    for en, zh in desc_map.items():
        if en not in calc:
            add(en, zh)

    # ── 8. Additional weapon names ────────────────────────────────────
    for en, zh in {
        "Favonius Lance": "西风长枪", "Favonius Warbow": "西风猎弓",
        "Favonius Sword": "西风剑", "Sacrificial Bow": "祭礼弓",
        "Sacrificial Fragments": "祭礼残章", "Blackcliff Pole": "黑岩刺枪",
        "Dragon's Bane": "匣里灭辰", "The Catch": "「渔获」",
        "Mistsplitter Reforged": "雾切之回光", "Freedom-Sworn": "苍古自由之誓",
        "A Thousand Floating Dreams": "千夜浮梦", "Aquila Favonia": "风鹰剑",
        "Skyward Blade": "天空之刃", "Sapwood Blade": "原木刀",
        "Primordial Jade Cutter": "磐岩结绿",
        "Primordial Jade Winged-Spear": "和璞鸢",
        "Cinnabar Spindle": "辰砂之纺锤", "Harbinger of Dawn": "黎明神剑",
        "Blackcliff Longsword": "黑岩长剑", "White Tassel": "白缨枪",
        "Deathmatch": "决斗之枪", "Festering Desire": "腐殖之剑",
        "Finale of the Deep": "海渊终曲", "Amenoma Kageuchi": "天目影打刀",
        "Fleuve Cendre Ferryman": "灰河渡手", "Prototype Amber": "试作金珀",
        "Sacrificial Jade": "祭礼玉", "Prototype Crescent": "试作澹月",
        "Hamayumi": "破魔之弓", "The Stringless": "绝弦",
        "The Widsith": "流浪乐章", "Xiphos' Moonlight": "西福斯的月光",
        "Iron Sting": "铁蜂刺", "Magic Guide": "魔导绪论",
        "Hunter's Path": "猎人之径",
        "Splendor of Tranquil Waters": "静水流涌之辉",
        "Staff of Homa": "护摩之杖",
    }.items():
        if en not in calc:
            add(en, zh)

    # ── 9. Related guide descriptions ──────────────────────────────────
    for en, zh in {
        "Best F2P. +32% burst DMG, +12% CR. Free.": "零氪最优。+32%大招伤害，+12%暴击率。免费。",
        "Essential shield for Melt Ganyu": "融甘必备护盾",
        "Cryo DMG buff + Freeze support": "冰伤增伤+永冻辅助",
        "Burn-Melt enabler": "燃融启动器",
        "Best Xiao buffer via Fanfare stacks": "通过气氛值提供最强增益",
        "Shield for interruption-free plunges": "护盾保护下落不被打断",
        "Off-field DPS in Double Geo teams": "双岩队后台输出",
        "Hyperbloom trigger": "超绽放触发器",
        "Shield for universal support": "护盾万能辅助",
        "Geo resonance + off-field DPS": "双岩共鸣+后台输出",
        "Double Hydro Vaporize": "双水蒸发",
        "Rational — Electro-charged": "雷国——感电",
        "Best Xiao buffer via Fanfare": "通过气氛值提供最强增益",
        "Shield keeps Hu Tao at low HP safely": "护盾安全保护胡桃低血量",
        "National core — snapshot her burst": "国家队核心——锁定大招面板",
        "Rational team — overload + battery": "雷国队——超载+充能",
        "Double Hydro Vaporize core": "双水蒸发核心",
        "ATK buff + Pyro resonance": "攻击增益+双火共鸣",
        "HP-drain synergy for Vaporize": "血量消耗+蒸发协同",
        "Universal DMG buff": "万能增伤",
        "Hydro application + DMG buff": "挂水+增伤",
        "Cryo swirl + freeze support": "冰风扩散+永冻辅助",
        "Pyro swirl + DMG buff": "火风扩散+增伤",
        "Hydro swirl + DMG amp": "水风扩散+增伤",
        "Off-field Hydro for Hyperbloom": "后台挂水超绽放",
        "Off-field Hydro for Vaporize": "后台挂水蒸发",
        "Shield for glass-cannon DPS": "护盾保护脆皮主C",
        "Snapshot ATK buff": "锁定攻击增益",
        "Double Hydro — flexible slot": "双水——灵活位",
        # Team names used in calculator
        "Raiden National": "雷神国家队", "Raiden Hypercarry": "雷神纯伤队",
        "Raiden Hyperbloom": "雷神超绽放", "Double Hydro": "双水队",
        "Vape Melt": "蒸发融化", "Burgeon": "烈绽放",
        "Double Hydro Hu Tao": "胡桃双水", "Hyperbloom Driver": "超绽放驾驶员",
        "Mono Hydro": "纯水队", "Hyperbloom": "超绽放",
        "Aggravate/Spread": "激化/蔓激化", "Nilou Bloom": "妮露绽放",
        "International": "万达国际", "Freeze Support": "永冻辅助",
        "Aggravate": "激化队", "Geo Resonance": "双岩共鸣",
        "Universal Shield": "万能护盾", "Burst Support": "爆发辅助",
        "Melt Ganyu": "融甘", "Morgana Freeze": "莫甘娜永冻",
        "Burn-Melt": "燃融", "FFXX Premium": "FFXX顶配队",
        "Classic Hypercarry": "经典三保一", "Double Geo": "双岩队",
        "Vape Arlecchino": "蒸发阿蕾奇诺", "Mono Pyro": "纯火队",
        "Overload (Chevreuse)": "超载（夏沃蕾）",
        "Neuvillette Hypercarry": "那维莱特主C队", "Taser": "感电队",
        "Hu Tao Double Hydro": "胡桃双水", "Xiao FFXX": "魈FFXX队",
        "National": "国家队", "Hypercarry": "纯伤队",
        "Hypercarry Support": "主C辅助", "Overload": "超载队",
        "Premium Freeze": "顶配永冻", "Budget Freeze": "平民永冻",
        "Mono Cryo": "纯冰队", "Mono Geo": "纯岩队",
        "Double Geo Flex": "双岩灵活位", "Navia Support": "娜维娅辅助",
        "Premium Plunge (FFXX)": "顶配下落（FFXX）",
    }.items():
        if en not in calc:
            add(en, zh)

    # ── 10. Stat/substat translations ──────────────────────────────────
    for en, zh in {
        "Energy Recharge": "元素充能效率", "CRIT Rate": "暴击率", "CRIT DMG": "暴击伤害",
        "ATK": "攻击力", "ATK%": "攻击力%", "HP": "生命值", "HP%": "生命值%",
        "DEF": "防御力", "DEF%": "防御力%", "Elemental Mastery": "元素精通",
        "Physical DMG": "物理伤害加成", "Electro DMG": "雷元素伤害加成",
        "Pyro DMG": "火元素伤害加成", "Hydro DMG": "水元素伤害加成",
        "Cryo DMG": "冰元素伤害加成", "Anemo DMG": "风元素伤害加成",
        "Geo DMG": "岩元素伤害加成", "Dendro DMG": "草元素伤害加成",
        "Healing Bonus": "治疗加成", "Flat HP": "固定生命值", "Flat ATK": "固定攻击力",
        "ATK% / EM": "攻击力% / 元素精通", "ATK% / ER%": "攻击力% / 充能效率%",
        "HP% / ER%": "生命值% / 充能效率%", "HP% / Hydro DMG": "生命值% / 水伤%",
        "Hydro DMG / HP%": "水伤% / 生命值%", "HP% / Geo DMG": "生命值% / 岩伤%",
        "HP% / CRIT Rate": "生命值% / 暴击率%", "ER% / ATK%": "充能效率% / 攻击力%",
        "ER% / ATK% / EM": "充能效率% / 攻击力% / 元素精通",
        "ER% / HP%": "充能效率% / 生命值%", "EM / ATK%": "元素精通 / 攻击力%",
        "EM / Dendro DMG": "元素精通 / 草伤%", "EM / CRIT Rate": "元素精通 / 暴击率%",
        "EM": "元素精通", "Electro DMG / ATK%": "雷伤% / 攻击力%",
        "Pyro DMG / ATK%": "火伤% / 攻击力%", "Cryo DMG%": "冰伤%",
        "Anemo DMG%": "风伤%", "CRIT Rate / CRIT DMG": "暴击率 / 暴击伤害",
        "CRIT DMG / CRIT Rate": "暴击伤害 / 暴击率",
        "CRIT DMG / HP%": "暴击伤害 / 生命值%",
        "Healing Bonus / HP%": "治疗加成 / 生命值%",
    }.items():
        if en not in calc:
            add(en, zh)


    # ── Element/weapon UI labels ────────────────────────────────────
    for en, zh in {
        "Electro": "雷", "Pyro": "火", "Hydro": "水", "Cryo": "冰",
        "Anemo": "风", "Geo": "岩", "Dendro": "草",
        "Polearm": "长柄武器", "Sword": "单手剑", "Bow": "弓",
        "Catalyst": "法器", "Claymore": "双手剑",
    }.items():
        if en not in calc:
            add(en, zh)

    # ── Guide card descriptions for homepage rotation ──────────────
    for cid in ['raiden','hutao','yelan','nahida','kazuha','zhongli','furina','arlecchino',
                'neuvillette','bennett','xiangling','ayaka','albedo','ganyu','xiao',
                'kokomi','tartaglia','alhaitham','yae-miko','xingqiu','kuki-shinobu',
                'fischl','beidou','sucrose','yaoyao','faruzan']:
        key = f'guides.{cid}_desc'
        if 'guides' in i18n and key.replace('guides.','') in i18n.get('guides',{}):
            val = i18n['guides'][key.replace('guides.','')]
            if val['en'] not in calc:
                add(val['en'], val['zh'])


    # ── Write JS file ──────────────────────────────────────────────────
    entries = []
    for en, pair in sorted(calc.items()):
        en_safe = en.replace('\\', '\\\\').replace("'", "\\'")
        zh_safe = pair[1].replace('\\', '\\\\').replace("'", "\\'")
        entries.append(f"  '{en_safe}': ['{en_safe}', '{zh_safe}']")

    out_path = os.path.join(OUTPUT_DIR, 'js', 'calc-i18n.js')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("// Auto-generated — do not edit\nvar CALC_I18N = {\n")
        f.write(",\n".join(entries))
        f.write("\n};\n")

    return len(entries)


if __name__ == '__main__':
    i18n_path = os.path.join(os.path.dirname(__file__), 'data', 'i18n.json')
    with open(i18n_path) as f:
        i18n = json.load(f)
    n = generate(i18n)
    print(f"Generated calc-i18n.js: {n} entries")
