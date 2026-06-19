// GenshinGuide Language Switcher (~1KB)
(function(){
  var currentLang = document.documentElement.lang.startsWith('zh') ? 'zh' : 'en';

  function switchTo(lang) {
    localStorage.setItem('lang', lang);
    var path = location.pathname;
    if (lang === 'zh') {
      path = path.replace('/en/', '/zh/');
      if (path === location.pathname) path = '/zh/' + path.replace(/^\//, '');
    } else {
      path = path.replace('/zh/', '/en/');
      if (path === location.pathname) path = '/en/' + path.replace(/^\//, '');
    }
    location.href = path;
  }

  document.addEventListener('DOMContentLoaded', function(){
    var btns = document.querySelectorAll('.lang-toggle');
    btns.forEach(function(btn){
      btn.addEventListener('click', function(){
        var lang = btn.dataset.lang;
        if (lang) switchTo(lang);
      });
      // Highlight active
      if (btn.dataset.lang === currentLang) btn.classList.add('active');
    });
  });
})();
