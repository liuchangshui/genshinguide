// Genshin Build Calculator — Enhanced Data Layer

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
  dragonsbane:{n:"Dragon's Bane",r:4,a:454,st:'Elemental Mastery',sv:221}
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
  wpnSel.innerHTML = c.weapons.map(k=>`<option value="${k}">${WEAPONS_DATA[k].n} (${WEAPONS_DATA[k].r}★)</option>`).join('');
  if(wpn && c.weapons.includes(wpn)) wpnSel.value = wpn;

  const selWpn = WEAPONS_DATA[wpnSel.value] || WEAPONS_DATA[c.weapons[0]];
  const totalATK = c.atk + selWpn.a;
  const grade = scoreBuild(c, selWpn);

  const labelSands = t('calcJS.sands_label');
  const labelGoblet = t('calcJS.goblet_label');
  const labelCirclet = t('calcJS.circlet_label');

  document.getElementById('calc-result').innerHTML = `
    <h4>${t('calcJS.build_summary')} — ${c.name}</h4>
    <div class="calc-stat"><div class="label">${t('calcJS.build_grade')}</div>
      <div class="value"><span class="grade grade-${grade}">${grade.toUpperCase()}</span> ${grade=='s'?t('calcJS.optimal_meta'):grade=='a'?t('calcJS.strong_viable'):t('calcJS.functional_budget')}</div>
    </div>
    <div class="calc-stat"><div class="label">${t('calcJS.best_arti')}</div>
      <div class="value" style="color:var(--accent);">🎯 ${c.arti}</div>
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
      ${c.teams.map(t=>`
        <div style="margin-bottom:10px;padding:10px;background:var(--bg-card);border-radius:6px;">
          <div style="font-weight:700;color:var(--accent);font-size:0.9rem;">${t.n}</div>
          <div style="font-size:0.8rem;color:var(--text-secondary);">${t.m}</div>
          <div style="font-size:0.78rem;color:var(--text-muted);margin-top:4px;">${t.d}</div>
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
  charSel.innerHTML = '<option value="">— Select Character —</option>' +
    Object.entries(DATA).map(([k,v])=>`<option value="${k}">${v.name}</option>`).join('');
  charSel.addEventListener('change', ()=>updateCalc());
  document.getElementById('weapon-select').addEventListener('change', ()=>updateCalc());
  if(window.location.hash==='#raiden'){
    charSel.value = 'raiden';
    updateCalc();
  }
});
