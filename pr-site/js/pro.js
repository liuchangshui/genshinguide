// GenshinGuide Pro — supporter status + email verification
(function(){
  var WORKER_URL = 'https://pro.bricklayer.tech'; // Placeholder — replace when Worker deployed
  var JWT_KEY = 'pro_jwt';

  // ── Check Pro status on page load ──────────────────────────────────
  try {
    var payload = parseJWT(localStorage.getItem(JWT_KEY));
    if (payload && payload.exp > Date.now()/1000) {
      applyProUI();
    }
  } catch(e) { /* invalid JWT, ignore */ }

  // ── Email verification (pricing page) ──────────────────────────────
  var emailInput = document.getElementById('pro-email-input');
  var verifyBtn  = document.getElementById('pro-verify-btn');
  var statusEl   = document.getElementById('pro-status');

  if (verifyBtn && emailInput && statusEl) {
    verifyBtn.addEventListener('click', function(){
      var email = emailInput.value.trim();
      if (!email || email.indexOf('@') < 0) {
        statusEl.textContent = (typeof t !== 'undefined' ? t('support.invalid_email') : 'Please enter a valid email');
        return;
      }
      verifyBtn.disabled = true;
      verifyBtn.textContent = (typeof t !== 'undefined' ? t('support.checking') : 'Checking...');
      fetch(WORKER_URL + '/verify?email=' + encodeURIComponent(email))
        .then(function(r){ return r.json(); })
        .then(function(data){
          if (data.valid && data.token) {
            localStorage.setItem(JWT_KEY, data.token);
            statusEl.textContent = (typeof t !== 'undefined' ? t('support.restored') : '✅ Restored! Refreshing...');
            setTimeout(function(){ location.reload(); }, 1000);
          } else {
            verifyBtn.disabled = false;
            verifyBtn.textContent = (typeof t !== 'undefined' ? t('support.verify_btn') : 'Restore');
            statusEl.textContent = (typeof t !== 'undefined' ? t('support.not_found') : '❌ No purchase found for this email');
          }
        })
        .catch(function(){
          verifyBtn.disabled = false;
          verifyBtn.textContent = (typeof t !== 'undefined' ? t('support.verify_btn') : 'Restore');
          statusEl.textContent = (typeof t !== 'undefined' ? t('support.error') : 'Network error. Please try again.');
        });
    });
  }

  // ── Apply Pro UI ───────────────────────────────────────────────────
  function applyProUI() {
    var proLinks = document.querySelectorAll('.btn-pro');
    for (var i = 0; i < proLinks.length; i++) {
      proLinks[i].textContent = '❤️ ' + (typeof t !== 'undefined' ? t('support.nav_badge') : 'Supporter');
      proLinks[i].style.background = 'linear-gradient(135deg, #e84a7a, #c0392b)';
    }
    var ads = document.querySelectorAll('.ad-native');
    for (var j = 0; j < ads.length; j++) {
      ads[j].style.display = 'none';
    }
  }

  // ── Parse JWT (no crypto lib needed) ────────────────────────────────
  function parseJWT(token) {
    if (!token) return null;
    try {
      var parts = token.split('.');
      if (parts.length !== 3) return null;
      var payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      return JSON.parse(atob(payload));
    } catch(e) {
      return null;
    }
  }
})();
