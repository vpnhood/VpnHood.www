/*
 * China promo bar.
 * On the original Joomla site the #chinaBar module was emitted server-side only
 * for visitors geolocated in China. This static site has no server, so we detect
 * the visitor's country in the browser and reveal the (always-rendered, hidden)
 * bar when they are in CN.
 *
 * Geo source (in order):
 *   1. ?geo=CN query param          -> manual preview/testing
 *   2. localStorage 'vh_geo'        -> sticky manual override
 *   3. Cloudflare /cdn-cgi/trace    -> production (the site is served via Cloudflare)
 * Dismissal is remembered in localStorage so the bar stays closed for that browser.
 */
(function () {
  var CLOSED_KEY = 'vh_china_bar_closed';

  function init() {
    var wrap = document.getElementById('mod-custom128');
    if (!wrap) return;

    // Wire up the close button (persist dismissal).
    var closeBtn = document.getElementById('closeChinaBar');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        wrap.style.display = 'none';
        try { localStorage.setItem(CLOSED_KEY, '1'); } catch (e) {}
        // Let Helix recompute the sticky-header placeholder height.
        window.dispatchEvent(new Event('resize'));
      });
    }

    // Respect a previous dismissal.
    try { if (localStorage.getItem(CLOSED_KEY) === '1') return; } catch (e) {}

    function show() {
      wrap.style.display = '';
      window.dispatchEvent(new Event('resize'));
    }

    // 1 & 2: manual override for preview/testing.
    var override = null;
    try {
      override = new URLSearchParams(window.location.search).get('geo') ||
                 localStorage.getItem('vh_geo');
    } catch (e) {}
    if (override) {
      if (String(override).toUpperCase() === 'CN') show();
      return;
    }

    // 3: production geolocation via Cloudflare edge (same-origin, no CORS).
    fetch('/cdn-cgi/trace', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.text() : ''; })
      .then(function (text) {
        var m = /(?:^|\n)loc=([A-Z]{2})/.exec(text || '');
        if (m && m[1] === 'CN') show();
      })
      .catch(function () { /* not behind Cloudflare / offline: leave the bar hidden */ });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
