// Genshin Build Calculator — Enhanced Data Layer
// (i18n: t() function provided by lang-switcher.js)

// Character data (internal)
const DATA = {
  raiden: {
    name:'Raiden Shogun',element:'electro',role:'Sub DPS / Battery',atk:337,ascStat:'Energy Recharge',ascVal:32,
    weapons:['engulfing','catch','homa','favlance'],
    arti:'Emblem of Severed Fate',artiAlt:'Thundering Fury / Noblesse',
    main:{sands:'ER% / ATK%',goblet:'Electro DMG / ATK%',circlet:'CRIT Rate / CRIT DMG'},
    subs:['Energy Recharge','CRIT Rate','CRIT DMG','ATK%'],
    teams:[
      {n:'Raiden National',m:'Xiangling + Xingqiu + Bennett',d:'High ST + AoE, consistent rotations'},
      {n:'Raiden Hypercarry',m:'Sara(C6) + Kazuha + Bennett',d:'Maximum burst DMG, needs C6 Sara'},
      {n:'Raiden Hyperbloom',m:'Nahida + Yelan/Xingqiu + Healer',d:'EM build, strongest reaction team'}
    ]
  },
  hutao: {
    name:'Hu Tao',element:'pyro',role:'Main DPS',atk:106,ascStat:'CRIT DMG',ascVal:38.4,
    weapons:['homa','dragonsbane','blackcliff'],
    arti:'Crimson Witch of Flames',artiAlt:"Shimenawa's Reminiscence",
    main:{sands:'HP% / EM',goblet:'Pyro DMG',circlet:'CRIT Rate / CRIT DMG'},
    subs:['CRIT Rate','CRIT DMG','HP%','Elemental Mastery'],
    teams:[
      {n:'Double Hydro',m:'Yelan + Xingqiu + Zhongli',d:'Comfortable, consistent high ST damage'},
      {n:'Vape Melt',m:'Yelan + Kazuha + Bennett',d:'Higher ceiling, less shielding'},
      {n:'Burgeon',m:'Nahida + Yelan + Flex',d:'AoE focused, Dendro reaction team'}
    ]
  },
  yelan: {
    name:'Yelan',element:'hydro',role:'Sub DPS / Support',atk:244,ascStat:'CRIT Rate',ascVal:19.2,
    weapons:['aqua','favbow','sacbow'],
    arti:'Emblem of Severed Fate',artiAlt:'Noblesse Oblige / Heart of Depth',
    main:{sands:'HP% / ER%',goblet:'Hydro DMG',circlet:'CRIT Rate / CRIT DMG'},
    subs:['CRIT Rate','CRIT DMG','HP%','Energy Recharge'],
    teams:[
      {n:'Double Hydro Hu Tao',m:'Hu Tao + Xingqiu + Zhongli',d:'Best Hu Tao support, high off-field DPS'},
      {n:'Hyperbloom Driver',m:'Nahida + Kuki + Flex',d:'Strong reaction core, Yelan drives blooms'},
      {n:'Mono Hydro',m:'Kokomi + Kazuha + Xingqiu',d:'Full hydro team, high ER refund'}
    ]
  },
  nahida: {
    name:'Nahida',element:'dendro',role:'Sub DPS / Support',atk:299,ascStat:'Elemental Mastery',ascVal:115,
    weapons:['thousand','sacfrag'],
    arti:'Deepwood Memories',artiAlt:'Gilded Dreams',
    main:{sands:'EM / ATK%',goblet:'EM / Dendro DMG',circlet:'EM / CRIT Rate'},
    subs:['Elemental Mastery','CRIT Rate','CRIT DMG','ATK%'],
    teams:[
      {n:'Hyperbloom',m:'Yelan/Xingqiu + Kuki/Raiden + Flex',d:'Top meta team, high floor damage'},
      {n:'Aggravate/Spread',m:'Yae/Fischl + Kazuha + Flex',d:'Quicken-based, scales with EM & CRIT'},
      {n:'Nilou Bloom',m:'Nilou + Kokomi + Flex Hydro/Dendro',d:'Pure bloom, massive AoE damage'}
    ]
  },
  kazuha: {
    name:'Kaedehara Kazuha',element:'anemo',role:'Support / CC',atk:297,ascStat:'Elemental Mastery',ascVal:115,
    weapons:['freedom','favsword','mistsplitter'],
    arti:'Viridescent Venerer',artiAlt:'None — 4pc VV is mandatory',
    main:{sands:'EM',goblet:'EM',circlet:'EM'},
    subs:['Elemental Mastery','Energy Recharge','ATK%','CRIT Rate'],
    teams:[
      {n:'International',m:'Childe + Xiangling + Bennett',d:'Classic vaporize team, Kazuha double swirl'},
      {n:'Freeze Support',m:'Ayaka + Kokomi + Shenhe',d:'Group + VV shred + elemental DMG buff'},
      {n:'Aggravate',m:'Yae/Fischl + Nahida + Flex',d:'Anemo driver, swirl electro for aggravate'}
    ]
  },
  zhongli: {
    name:'Zhongli',element:'geo',role:'Shield / Support',atk:251,ascStat:'Geo DMG',ascVal:28.8,
    weapons:['homa','favlance','blackcliff'],
    arti:'Tenacity of the Millelith',artiAlt:'Archaic Petra / Noblesse',
    main:{sands:'HP%',goblet:'HP% / Geo DMG',circlet:'HP% / CRIT Rate'},
    subs:['HP%','Energy Recharge','CRIT Rate','CRIT DMG'],
    teams:[
      {n:'Geo Resonance',m:'Itto/Albedo + Gorou + Flex',d:'Mono geo, strongest shield + resonance'},
      {n:'Universal Shield',m:'Hu Tao/Yoimiya + Xingqiu + Yelan',d:'Fits any team, 100% uptime shield'},
      {n:'Burst Support',m:'Ningguang + Bennett + Xiangling',d:'Quick swap, high burst DMG Zhongli'}
    ]
  },
furina: {
    name:'Furina',element:'hydro',role:'Sub DPS / Buffer',atk:244,ascStat:'CRIT Rate',ascVal:19.2,
    weapons:['splendor','fleuve','festering','favsword'],
    arti:'Golden Troupe',artiAlt:'Tenacity of the Millelith (support)',
    main:{sands:'HP%',goblet:'HP% / Hydro DMG',circlet:'CRIT Rate / CRIT DMG'},
    subs:['Energy Recharge (160-180%)','CRIT Rate / CRIT DMG','HP%','Flat HP'],
    teams:[
      {n:'Neuvillette Hypercarry',m:'Furina + Neuvillette + Kazuha + Baizhu',d:'HP drain synergy, massive DMG amp'},
      {n:'Hu Tao Double Hydro',m:'Furina + Yelan + Hu Tao + Jean',d:'HP-drain keeps Hu Tao <50%, team-wide heal'},
      {n:'Xiao FFXX',m:'Furina + Xiao + Faruzan + Xianyun',d:'Fanfare stacks + Anemo plunge buff'}
    ]
  },
  arlecchino: {
    name:'Arlecchino',element:'pyro',role:'Main DPS',atk:342,ascStat:'CRIT DMG',ascVal:38.4,
    weapons:['crimson','homa','pjws','whitetassel'],
    arti:'Fragment of Harmonic Whimsy',artiAlt:'Gladiator\'s Finale',
    main:{sands:'ATK%',goblet:'Pyro DMG',circlet:'CRIT Rate / CRIT DMG'},
    subs:['CRIT Rate / CRIT DMG','ATK%','Elemental Mastery','Energy Recharge'],
    teams:[
      {n:'Vape Arlecchino',m:'Arle + Yelan + Kazuha + Bennett',d:'Highest ceiling, consistent Vaporize'},
      {n:'Mono Pyro',m:'Arle + Xiangling + Kazuha + Bennett',d:'Raw Pyro DMG, no reaction reliance'},
      {n:'Overload (Chevreuse)',m:'Arle + Fischl + Chevreuse + Bennett',d:'Overload comp, high AoE clear'}
    ]
  },
  neuvillette: {
    name:'Neuvillette',element:'hydro',role:'Main DPS',atk:204,ascStat:'CRIT DMG',ascVal:38.4,
    weapons:['tome','protoamber','sacjade'],
    arti:'Marechaussee Hunter',artiAlt:'Heart of Depth (budget)',
    main:{sands:'HP%',goblet:'Hydro DMG / HP%',circlet:'CRIT DMG / HP%'},
    subs:['CRIT Rate / CRIT DMG (64:250+)','HP%','Energy Recharge (120-140%)','Flat HP'],
    teams:[
      {n:'Hypercarry',m:'Neu + Furina + Kazuha + Baizhu',d:'Premium team, Furina Hydro resonance'},
      {n:'Taser',m:'Neu + Fischl + Kazuha + Zhongli',d:'Electro-charged, shield essential at C0'},
      {n:'Hyperbloom Driver',m:'Neu + Nahida + Raiden + Flex',d:'HP-scaling hyperbloom driver'}
    ]
  },
  bennett: {
    name:'Bennett',element:'pyro',role:'Support / Healer',atk:191,ascStat:'Energy Recharge',ascVal:26.7,
    weapons:['aquila','mistsplitter','sapwood','skyward'],
    arti:'Noblesse Oblige',artiAlt:'Instructor (budget EM buff)',
    main:{sands:'ER% / HP%',goblet:'HP%',circlet:'Healing Bonus / HP%'},
    subs:['Energy Recharge (200%+)','HP%','Flat HP','CRIT (for Favonius)'],
    teams:[
      {n:'National',m:'XL + XQ + Raiden/Childe + Bennett',d:'Core of almost every meta team'},
      {n:'Melt Ganyu',m:'Ganyu + Xiangling + Zhongli + Bennett',d:'ATK buff + Pyro application'},
      {n:'Hypercarry Support',m:'Any ATK DPS + Bennett + Kazuha + Flex',d:'Universal ATK buffer, fits everywhere'}
    ]
  },
  xiangling: {
    name:'Xiangling',element:'pyro',role:'Sub DPS',atk:225,ascStat:'Elemental Mastery',ascVal:96,
    weapons:['catch','homa','dragonsbane','favlance'],
    arti:'Emblem of Severed Fate',artiAlt:'Crimson Witch (Vape focus)',
    main:{sands:'ER% / ATK% / EM',goblet:'Pyro DMG',circlet:'CRIT Rate / CRIT DMG'},
    subs:['Energy Recharge (180-220%)','CRIT Rate / CRIT DMG','ATK% / EM','Flat ATK'],
    teams:[
      {n:'National',m:'XL + Bennett + XQ + Raiden/Childe',d:'Snapshot Bennett buff, top-tier off-field'},
      {n:'Melt Ganyu',m:'Ganyu + XL + Bennett + Zhongli',d:'Pyro enabler for Ganyu charged shots'},
      {n:'Overload',m:'XL + Chevreuse + Fischl + Bennett',d:'Overload meta, Chevreuse shred'}
    ]
  },
  ayaka: {
    name:'Kamisato Ayaka',element:'cryo',role:'Main DPS',atk:342,ascStat:'CRIT DMG',ascVal:38.4,
    weapons:['mistsplitter','amenoma','finale','blackcliffsword'],
    arti:'Blizzard Strayer',artiAlt:'None — 4pc BS is mandatory',
    main:{sands:'ATK%',goblet:'Cryo DMG',circlet:'CRIT DMG'},
    subs:['CRIT DMG (240%+ target)','ATK% (2000+ target)','Energy Recharge (130-140%)','CRIT Rate (30-45% max)'],
    teams:[
      {n:'Premium Freeze',m:'Ayaka + Kokomi + Kazuha + Shenhe',d:'Best Ayaka team, full Cryo shred'},
      {n:'Budget Freeze',m:'Ayaka + Mona + Sucrose + Diona',d:'F2P-friendly, Mona Omen buff'},
      {n:'Mono Cryo',m:'Ayaka + Shenhe + Kazuha + Layla',d:'For unfreezable boss enemies'}
    ]
  },
  albedo: {
    name:'Albedo',element:'geo',role:'Sub DPS',atk:251,ascStat:'Geo DMG',ascVal:28.8,
    weapons:['cinnabar','harbinger','jadecutter','festering'],
    arti:'Husk of Opulent Dreams',artiAlt:'Golden Troupe',
    main:{sands:'DEF%',goblet:'Geo DMG',circlet:'CRIT Rate / CRIT DMG'},
    subs:['DEF%','CRIT Rate / CRIT DMG','Energy Recharge','ATK%'],
    teams:[
      {n:'Mono Geo',m:'Itto + Albedo + Gorou + Zhongli',d:'Geo resonance, full DEF scaling'},
      {n:'Double Geo Flex',m:'Albedo + Zhongli + any DPS duo',d:'Geo resonance + shield shred'},
      {n:'Navia Support',m:'Navia + Albedo + Bennett + XL',d:'Crystallize shard generator'}
    ]
  },
  ganyu: {
    name:'Ganyu',element:'cryo',role:'Main DPS',atk:335,ascStat:'CRIT DMG',ascVal:38.4,
    weapons:['amos','aqua','hunters','protcres'],
    arti:'Wanderer\'s Troupe',artiAlt:'Blizzard Strayer (Freeze)',
    main:{sands:'ATK% / EM',goblet:'Cryo DMG',circlet:'CRIT DMG / CRIT Rate'},
    subs:['CRIT DMG / CRIT Rate','ATK%','Elemental Mastery (Melt)','Energy Recharge'],
    teams:[
      {n:'Melt Ganyu',m:'Ganyu + XL + Bennett + Zhongli',d:'Shielded charge shots, 1.5x Melt'},
      {n:'Morgana Freeze',m:'Ganyu + Kazuha + Mona + Diona',d:'AoE freeze, quadratic scaling burst'},
      {n:'Burn-Melt',m:'Ganyu + Nahida + Bennett + Zhongli',d:'Consistent burning Pyro aura'}
    ]
  },
  xiao: {
    name:'Xiao',element:'anemo',role:'Main DPS',atk:349,ascStat:'CRIT Rate',ascVal:19.2,
    weapons:['pjws','homa','blackcliff','deathmatch'],
    arti:'Vermillion Hereafter',artiAlt:'Marechaussee Hunter (with Furina)',
    main:{sands:'ATK%',goblet:'Anemo DMG',circlet:'CRIT Rate / CRIT DMG'},
    subs:['CRIT Rate / CRIT DMG (75:180+)','ATK%','Energy Recharge (120-130%)','Flat ATK'],
    teams:[
      {n:'FFXX Premium',m:'Xiao + Faruzan + Furina + Xianyun',d:'Best team — Fanfare + Anemo buff'},
      {n:'Classic Hypercarry',m:'Xiao + Faruzan + Bennett + Zhongli',d:'Shield + ATK buff, reliable'},
      {n:'Double Geo',m:'Xiao + Albedo + Zhongli + Jean/Bennett',d:'Geo resonance alternative'}
    ]
  }
};

const WEAPONS_DATA = {
  engulfing:{n:'Engulfing Lightning',r:5,a:608,st:'Energy Recharge',sv:55.1},
  catch:{n:'The Catch',r:4,a:510,st:'Energy Recharge',sv:45.9},
  homa:{n:'Staff of Homa',r:5,a:608,st:'CRIT DMG',sv:66.2},
  aqua:{n:'Aqua Simulacra',r:5,a:542,st:'CRIT DMG',sv:88.2},
  mistsplitter:{n:'Mistsplitter Reforged',r:5,a:674,st:'CRIT DMG',sv:44.1},
  freedom:{n:'Freedom-Sworn',r:5,a:608,st:'Elemental Mastery',sv:198},
  favlance:{n:'Favonius Lance',r:4,a:565,st:'Energy Recharge',sv:30.6},
  thousand:{n:'A Thousand Floating Dreams',r:5,a:542,st:'Elemental Mastery',sv:265},
  sacbow:{n:'Sacrificial Bow',r:4,a:565,st:'Energy Recharge',sv:30.6},
  blackcliff:{n:'Blackcliff Pole',r:4,a:510,st:'CRIT DMG',sv:55.1},
  favbow:{n:'Favonius Warbow',r:4,a:454,st:'Energy Recharge',sv:61.3},
  sacfrag:{n:'Sacrificial Fragments',r:4,a:454,st:'Elemental Mastery',sv:221},
  favsword:{n:'Favonius Sword',r:4,a:454,st:'Energy Recharge',sv:61.3},
  dragonsbane:{n:"Dragon's Bane",r:4,a:454,st:'Elemental Mastery',sv:221},
  splendor:{n:'Splendor of Tranquil Waters',r:5,a:542,st:'CRIT DMG',sv:88.2},
  fleuve:{n:'Fleuve Cendre Ferryman',r:4,a:510,st:'Energy Recharge',sv:45.9},
  festering:{n:'Festering Desire',r:4,a:510,st:'Energy Recharge',sv:45.9},
  crimson:{n:"Crimson Moon's Semblance",r:5,a:674,st:'CRIT Rate',sv:22.1},
  pjws:{n:'Primordial Jade Winged-Spear',r:5,a:674,st:'CRIT Rate',sv:22.1},
  whitetassel:{n:'White Tassel',r:3,a:401,st:'CRIT Rate',sv:23.4},
  tome:{n:'Tome of the Eternal Flow',r:5,a:542,st:'CRIT DMG',sv:88.2},
  protoamber:{n:'Prototype Amber',r:4,a:510,st:'HP',sv:41.3},
  sacjade:{n:'Sacrificial Jade',r:4,a:510,st:'Elemental Mastery',sv:221},
  aquila:{n:'Aquila Favonia',r:5,a:674,st:'Physical DMG',sv:41.3},
  sapwood:{n:'Sapwood Blade',r:4,a:565,st:'Energy Recharge',sv:30.6},
  skyward:{n:'Skyward Blade',r:5,a:608,st:'Energy Recharge',sv:55.1},
  amenoma:{n:'Amenoma Kageuchi',r:4,a:454,st:'ATK',sv:55.1},
  finale:{n:'Finale of the Deep',r:4,a:565,st:'ATK',sv:27.6},
  blackcliffsword:{n:'Blackcliff Longsword',r:4,a:565,st:'CRIT DMG',sv:36.8},
  cinnabar:{n:'Cinnabar Spindle',r:4,a:454,st:'DEF',sv:69.0},
  harbinger:{n:'Harbinger of Dawn',r:3,a:401,st:'CRIT DMG',sv:46.9},
  jadecutter:{n:'Primordial Jade Cutter',r:5,a:542,st:'CRIT Rate',sv:44.1},
  amos:{n:"Amos' Bow",r:5,a:608,st:'ATK',sv:49.6},
  hunters:{n:"Hunter's Path",r:5,a:542,st:'CRIT Rate',sv:44.1},
  protcres:{n:'Prototype Crescent',r:4,a:510,st:'ATK',sv:41.3},
};

// ===== Compatibility layer for inline scripts =====

const CHARACTERS = {};
Object.entries(DATA).forEach(([id, c]) => {
  CHARACTERS[id] = { name: c.name, baseATK: c.atk, element: c.element };
});

const CHARACTER_WEAPONS = {};
Object.entries(DATA).forEach(([id, c]) => {
  CHARACTER_WEAPONS[id] = [...c.weapons];
});

const WEAPONS = {};
Object.entries(WEAPONS_DATA).forEach(([id, w]) => {
  WEAPONS[id] = { name: w.n, atk: w.a, rarity: w.r, substat: w.st + ' +' + w.sv + '%' };
});

const ARTIFACT_SETS = {};
Object.entries(DATA).forEach(([id, c]) => {
  ARTIFACT_SETS[id] = { best: c.arti };
});

const MAIN_STATS = {};
Object.entries(DATA).forEach(([id, c]) => {
  MAIN_STATS[id] = { ...c.main };
});

const SUB_STATS = {};
Object.entries(DATA).forEach(([id, c]) => {
  SUB_STATS[id] = [...c.subs];
});

const TEAMS = {};
Object.entries(DATA).forEach(([id, c]) => {
  TEAMS[id] = c.teams.map(t => ({ name: t.n, members: t.m, desc: t.d }));
});

// ===== Legacy calculator functions =====
function updateCalc(){
  const char = document.getElementById('char-select').value;
  const wpn = document.getElementById('weapon-select').value;
  if(!char || !DATA[char]) return;
  const c = DATA[char];
  const w = WEAPONS_DATA[wpn] || null;

  const wpnSel = document.getElementById('weapon-select');
  wpnSel.innerHTML = c.weapons.map(k=>`<option value="${k}">${t(WEAPONS_DATA[k].n)} (${WEAPONS_DATA[k].r}★)</option>`).join('');
  if(wpn && c.weapons.includes(wpn)) wpnSel.value = wpn;

  const selWpn = WEAPONS_DATA[wpnSel.value] || WEAPONS_DATA[c.weapons[0]];
  const totalATK = c.atk + selWpn.a;
  const grade = scoreBuild(c, selWpn);

  const labelSands = t('calcJS.sands_label');
  const labelGoblet = t('calcJS.goblet_label');
  const labelCirclet = t('calcJS.circlet_label');

  document.getElementById('calc-result').innerHTML = `
    <h4>${t('calcJS.build_summary')} — ${t(c.name)}</h4>
    <div class="calc-stat"><div class="label">${t('calcJS.build_grade')}</div>
      <div class="value"><span class="grade grade-${grade}">${grade.toUpperCase()}</span> ${grade=='s'?t('calcJS.optimal_meta'):grade=='a'?t('calcJS.strong_viable'):t('calcJS.functional_budget')}</div>
    </div>
    <div class="calc-stat"><div class="label">${t('calcJS.best_arti')}</div>
      <div class="value" style="color:var(--accent);">🎯 ${t(c.arti)}</div>
    </div>
    <div class="calc-stat"><div class="label">${t('calcJS.total_atk')}</div>
      <div class="value">${totalATK} <span style="font-size:0.8rem;color:var(--text-muted);">(${c.atk} ${t('calcJS.char_atk')} + ${selWpn.a} ${t('calcJS.weapon_atk')})</span></div>
    </div>
    <div class="calc-stat"><div class="label">${t('calcJS.wpn_substat')}</div>
      <div class="value">${selWpn.st} +${selWpn.sv}%</div>
    </div>
    <div class="calc-stat"><div class="label">${t('calcJS.main_priority')}</div>
      <div class="value" style="font-size:0.9rem;">${labelSands}: <b style="color:var(--gold);">${c.main.sands}</b> | ${labelGoblet}: <b style="color:var(--gold);">${c.main.goblet}</b> | ${labelCirclet}: <b style="color:var(--gold);">${c.main.circlet}</b></div>
    </div>
    <div class="calc-stat"><div class="label">${t('calcJS.sub_priority')}</div>
      <div class="value" style="font-size:0.85rem;">${c.subs.map((s,i)=>`<span style="color:#e0e0e0;">${i+1}. ${s}</span>`).join(' > ')}</div>
    </div>
    <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border);">
      <div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:10px;">${t('calcJS.best_teams')}</div>
      ${c.teams.map(tm=>`
        <div style="margin-bottom:10px;padding:10px;background:var(--bg-card);border-radius:6px;">
          <div style="font-weight:700;color:var(--accent);font-size:0.9rem;">${t(tm.n)}</div>
          <div style="font-size:0.8rem;color:var(--text-secondary);">${t(tm.m)}</div>
          <div style="font-size:0.78rem;color:var(--text-muted);margin-top:4px;">${t(tm.d)}</div>
        </div>
      `).join('')}
    </div>
    <div class="pro-lock" style="margin-top:16px;">
      <div class="icon">🔒</div>
      <p>${t('guide.pro_lock_desc')}</p>
      <a href="pricing.html" class="btn btn-gold" style="display:inline-flex;">${t('guide.pro_lock_btn')}</a>
    </div>
  `;
}

function scoreBuild(c, w){
  const score = w.r * 10 + c.atk/20;
  return score > 70 ? 's' : score > 50 ? 'a' : 'b';
}

document.addEventListener('DOMContentLoaded',()=>{
  const charSel = document.getElementById('char-select');
  if(!charSel) return;
  charSel.innerHTML = '<option value="">' + t('home.calc_placeholder') + '</option>' +
    Object.entries(DATA).map(([k,v])=>`<option value="${k}">${t(v.name)}</option>`).join('');
  charSel.addEventListener('change', ()=>updateCalc());
  document.getElementById('weapon-select').addEventListener('change', ()=>updateCalc());
  if(window.location.hash==='#raiden'){
    charSel.value = 'raiden';
    updateCalc();
  }
});
