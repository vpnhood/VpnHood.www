/*
 * China promo bar.
 *
 * On the original site the #chinaBar module was emitted server-side only
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
 * Geo source: window.vhCountry, the lookup header.html shares with the analytics
 * consent (in order: ?geo=CN query param, localStorage 'vh_geo', the session's
 * cached answer, then Cloudflare /cdn-cgi/trace read from the apex vpnhood.com).
 *
 * Closing the bar only removes it for the current page view; it reappears on the
 * next load if the visitor is still in CN (no persisted dismissal).
 */
(function () {
  // dir="ltr": the bar is Chinese (LTR) content and must render identically on
  // RTL pages (e.g. a CN visitor reading the Persian tree) — without this, an
  // RTL <html dir> would mirror the bar's layout and arrow.
  var BAR_HTML =
    '<div id="vhChinaBar" dir="ltr">' +
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

  function setBarHeight(bar) {
    // Reserve the bar's height so the (fixed) header and page content sit below it.
    document.documentElement.style.setProperty('--china-bar-h', bar.offsetHeight + 'px');
  }

  function inject() {
    if (document.getElementById('vhChinaBar')) return;
    var tmp = document.createElement('div');
    tmp.innerHTML = BAR_HTML;
    var bar = tmp.firstChild;

    // Inject OUTSIDE #sp-header (into <body>) so the header keeps its natural
    // height and Helix's sticky measurements stay correct.
    document.body.insertBefore(bar, document.body.firstChild);
    document.body.classList.add('has-china-bar');
    setBarHeight(bar);

    // Keep the reserved space correct if the bar wraps/reflows on resize.
    var onResize = function () {
      if (document.getElementById('vhChinaBar')) setBarHeight(bar);
    };
    window.addEventListener('resize', onResize);

    var closeBtn = document.getElementById('closeChinaBar');
    if (closeBtn) {
      closeBtn.addEventListener('click', function () {
        if (bar.parentNode) bar.parentNode.removeChild(bar); // gone for this view only
        document.body.classList.remove('has-china-bar');
        document.documentElement.style.removeProperty('--china-bar-h');
        window.removeEventListener('resize', onResize);
      });
    }
  }

  function detect() {
    // Not reachable / offline resolves to null: no bar. Why the lookup reads the apex
    // vpnhood.com and not same-origin or cloudflare.com: .docs/china-bar-geo.md.
    window.vhCountry.then(function (country) {
      if (country === 'CN') inject();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', detect);
  } else {
    detect();
  }
})();
