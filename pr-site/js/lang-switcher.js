// GenshinGuide Language Switcher
(function(){
  var currentLang = document.documentElement.lang.startsWith('zh') ? 'zh' : 'en';

  function switchTo(lang) {
    localStorage.setItem('lang', lang);
    var path = location.pathname.replace(/\/$/, '');
    if (path.startsWith('/en')) path = path.replace(/^\/en/, '/zh');
    else if (path.startsWith('/zh')) path = path.replace(/^\/zh/, '/en');
    else path = (lang === 'zh' ? '/zh' : '/en') + path;
    if (path === '/en' || path === '/zh') path += '/';
    location.href = path;
  }

  document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('.lang-toggle').forEach(function(btn){
      btn.addEventListener('click', function(){
        var lang = btn.dataset.lang;
        if (lang && lang !== currentLang) switchTo(lang);
      });
    });
  });
})();
