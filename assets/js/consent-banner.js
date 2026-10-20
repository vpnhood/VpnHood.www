// Analytics consent: the banner (_includes/consent-banner.html) and the footer's "Cookie
// settings". Only visitors in window.vhConsentRegions (header.html) see them, or anyone who
// already chose; the choice lives in localStorage vh_consent. Accept loads Tag Manager
// (window.vhLoadGtm, production builds only). Declining after an Accept deletes Google
// Analytics' cookies and reloads, so nothing already running keeps collecting.
(function () {
  var KEY = 'vh_consent';

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function store(choice) {
    try { localStorage.setItem(KEY, choice); } catch (e) {}
  }

  // Google Analytics sets _ga* on the widest domain it can, so try every parent domain.
  function deleteGaCookies() {
    var parts = location.hostname.split('.');
    document.cookie.split(';').forEach(function (cookie) {
      var name = cookie.split('=')[0].trim();
      if (name.indexOf('_ga') !== 0) return;
      document.cookie = name + '=; Max-Age=0; path=/';
      for (var i = 0; i < parts.length - 1; i++)
        document.cookie = name + '=; Max-Age=0; path=/; domain=.' + parts.slice(i).join('.');
    });
  }

  function init() {
    var banner = document.getElementById('vhConsent');
    if (!banner) return;
    var settings = document.querySelectorAll('.vh-consent-settings');

    banner.addEventListener('click', function (e) {
      var button = e.target.closest('[data-vh-consent]');
      if (!button) return;
      var choice = button.getAttribute('data-vh-consent');
      var before = stored();
      store(choice);
      banner.hidden = true;
      if (choice === 'granted') {
        if (window.vhLoadGtm) window.vhLoadGtm(true);
      } else if (before === 'granted') {
        deleteGaCookies();
        location.reload();
      }
    });

    document.addEventListener('click', function (e) {
      if (e.target.closest('#vhConsentSettings')) banner.hidden = false;
    });

    window.vhCountry.then(function (country) {
      var inRegion = !!country && window.vhConsentRegions.indexOf(country) >= 0;
      if (inRegion || stored())
        settings.forEach(function (el) { el.hidden = false; });
      if (inRegion && !stored()) banner.hidden = false;
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
