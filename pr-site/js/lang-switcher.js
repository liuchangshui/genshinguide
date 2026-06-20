// GenshinGuide Language Switcher + minimal i18n
(function(){
  var currentLang = document.documentElement.lang.startsWith('zh') ? 'zh' : 'en';
  var zh = currentLang === 'zh';

  function switchTo(lang) {
    localStorage.setItem('lang', lang);
    var path = location.pathname.replace(/\/$/, '');
    if (path.startsWith('/en')) path = path.replace(/^\/en/, '/zh');
    else if (path.startsWith('/zh')) path = path.replace(/^\/zh/, '/en');
    else path = (lang === 'zh' ? '/zh' : '/en') + path;
    if (path === '/en' || path === '/zh') path += '/';
    location.href = path;
  }

  document.querySelectorAll('.lang-toggle').forEach(function(btn){
    btn.addEventListener('click', function(){
      var lang = btn.dataset.lang;
      if (lang && lang !== currentLang) switchTo(lang);
    });
  });

  // Minimal t() polyfill — replaces 162KB i18n.js
  var DICT = {
    'calcJS.sands_label':         [ 'Sands', '\u65f6\u4e4b\u6c99' ],
    'calcJS.goblet_label':        [ 'Goblet', '\u7a7a\u4e4b\u676f' ],
    'calcJS.circlet_label':       [ 'Circlet', '\u7406\u4e4b\u51a0' ],
    'calcJS.build_summary':       [ 'Build Summary', 'Build\u603b\u7ed3' ],
    'calcJS.build_grade':         [ 'Build Grade', 'Build\u8bc4\u7ea7' ],
    'calcJS.optimal_meta':        [ 'Optimal \u2014 Meta choice', '\u6700\u4f18 \u2014 \u7248\u672c\u7b54\u6848' ],
    'calcJS.strong_viable':       [ 'Strong \u2014 Viable in all content', '\u5f3a\u529b \u2014 \u5168\u5185\u5bb9\u53ef\u7528' ],
    'calcJS.functional_budget':   [ 'Functional \u2014 Budget build', '\u53ef\u7528 \u2014 \u5e73\u6c11\u914d\u88c5' ],
    'calcJS.best_arti':           [ 'Best Artifact Set', '\u6700\u4f73\u5723\u9057\u7269' ],
    'calcJS.total_atk':           [ 'Total ATK', '\u603b\u653b\u51fb\u529b' ],
    'calcJS.char_atk':            [ 'char', '\u89d2\u8272' ],
    'calcJS.weapon_atk':          [ 'wpn', '\u6b66\u5668' ],
    'calcJS.wpn_substat':         [ 'Weapon Sub-stat', '\u6b66\u5668\u526f\u8bcd\u6761' ],
    'calcJS.main_priority':       [ 'Main Stats Priority', '\u4e3b\u8bcd\u6761\u4f18\u5148\u7ea7' ],
    'calcJS.sub_priority':        [ 'Sub-stat Priority', '\u526f\u8bcd\u6761\u4f18\u5148\u7ea7' ],
    'calcJS.best_teams':          [ 'Best Teams', '\u6700\u4f73\u914d\u961f' ],
    'home.calc_wpn_placeholder':  [ '\u2014 Select Weapon \u2014', '\u2014 \u9009\u62e9\u6b66\u5668 \u2014' ],
    'home.calc_hint':             [ '\u261b Select a character to see build recommendations', '\u261b \u9009\u62e9\u89d2\u8272\u67e5\u770bBuild\u63a8\u8350' ],
    'home.calc_placeholder':      [ '\u2014 Select Character \u2014', '\u2014 \u9009\u62e9\u89d2\u8272 \u2014' ],
    'guide.pro_lock_desc':        [ 'Unlock full damage simulation and build optimization.', '\u89e3\u9501\u5b8c\u6574\u4f24\u5bb3\u6a21\u62df\u4e0eBuild\u4f18\u5316\u3002' ],
    'guide.pro_lock_btn':         [ 'Unlock Pro \u2014 $5/month', '\u5f00\u901aPro \u2014 $5/\u6708' ],
    'pricing.checkout_soon':      [ 'Pro checkout coming soon \u2014 thank you for your interest!', 'Pro\u652f\u4ed8\u5373\u5c06\u4e0a\u7ebf\uff0c\u611f\u8c22\u5173\u6ce8\uff01' ],
  };
  window.t = function(key){
    var entry = DICT[key];
    return entry ? entry[zh ? 1 : 0] : key;
  };
})();
