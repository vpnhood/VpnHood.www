/*
 * China promo bar.
 *
 * On the original Joomla site the #chinaBar module was emitted server-side only
 * for visitors geolocated in China. This static site has no server, so we detect
 * the country in the browser and INJECT the bar only for CN visitors.
 *
 * SEO: Googlebot DOES execute JS, so "hiding in JS" alone wouldn't help. What
 * keeps this SEO-safe is that the bar is GEO-GATED: it injects only when the
 * Cloudflare edge reports loc=CN. Googlebot crawls/renders from non-CN (US)
 * IPs, so /cdn-cgi/trace returns a non-CN country and the bar is never injected
 * in the rendered DOM Google indexes. The static HTML is also clean (no Chinese
 * copy, no c-hood.com link), and the link carries rel="nofollow" as a backstop.
 * This is legitimate geo-targeting (all CN users see it), not cloaking.
 *
 * Geo source (in order):
 *   1. ?geo=CN query param     -> manual preview/testing
 *   2. localStorage 'vh_geo'   -> sticky manual override
 *   3. Cloudflare /cdn-cgi/trace (loc=CN) -> production (site is served via Cloudflare)
 *
 * Closing the bar only removes it for the current page view; it reappears on the
 * next load if the visitor is still in CN (no persisted dismissal).
 */
(function () {
  var BAR_HTML =
    '<div id="mod-custom128" class="mod-custom custom">' +
      '<div id="chinaBar">' +
        '<div id="barTextWrapper">' +
          '<p class="txt-purple-l-1 me-lg-5">您想要购买高级代码吗？您在中国吗？</p>' +
          '<a id="chinaTopBarLink" href="https://www.c-hood.com/login" target="_blank" rel="nofollow noopener" class="vh-btn vh-btn-light-purple px-3 py-1">' +
            '<span>从这里开始</span>' +
            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 12h16m0 0l-6-6m6 6l-6 6"></path></svg>' +
          '</a>' +
        '</div>' +
        '<button id="closeChinaBar" aria-label="Close">' +
          '<svg xmlns="http://www.w3.org/2000/svg" width="30px" height="30px" viewBox="0 0 24 24"><path fill="#7b7afe" d="M22 12c0 5.523-4.477 10-10 10S2 17.523 2 12S6.477 2 12 2s10 4.477 10 10" opacity="0.3"></path><path fill="#7b7afe" d="M8.97 8.97a.75.75 0 0 1 1.06 0L12 10.94l1.97-1.97a.75.75 0 1 1 1.06 1.06L13.06 12l1.97 1.97a.75.75 0 0 1-1.06 1.06L12 13.06l-1.97 1.97a.75.75 0 0 1-1.06-1.06L10.94 12l-1.97-1.97a.75.75 0 0 1 0-1.06"></path></svg>' +
        '</button>' +
      '</div>' +
    '</div>';

  function inject() {
    var header = document.getElementById('sp-header');
    if (!header || document.getElementById('mod-custom128')) return;
    var tmp = document.createElement('div');
    tmp.innerHTML = BAR_HTML;
    var bar = tmp.firstChild;
    header.insertBefore(bar, header.firstChild);

    var closeBtn = document.getElementById('closeChinaBar');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        bar.parentNode && bar.parentNode.removeChild(bar); // gone for this view only
        window.dispatchEvent(new Event('resize'));          // let Helix recompute header height
      });
    }
    window.dispatchEvent(new Event('resize'));
  }

  function detect() {
    // 1 & 2: manual override for preview/testing.
    var override = null;
    try {
      override = new URLSearchParams(window.location.search).get('geo') ||
                 localStorage.getItem('vh_geo');
    } catch (e) {}
    if (override) {
      if (String(override).toUpperCase() === 'CN') inject();
      return;
    }
    // 3: production geolocation via Cloudflare edge (same-origin, no CORS).
    fetch('/cdn-cgi/trace', { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.text() : ''; })
      .then(function (text) {
        var m = /(?:^|\n)loc=([A-Z]{2})/.exec(text || '');
        if (m && m[1] === 'CN') inject();
      })
      .catch(function () { /* not behind Cloudflare / offline: no bar */ });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', detect);
  } else {
    detect();
  }
})();
