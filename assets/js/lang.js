// Language preference & auto-switch.
//
// - Clicking any language-selector link (data-vh-lang) stores the choice in
//   localStorage("vh_lang"); the links themselves already point to the right URL.
// - On English pages only, visitors whose stored (or, on first visit, browser)
//   language has a translation are sent to it. The target URL is taken from the
//   page's own <link rel="alternate" hreflang> tags — emitted only when the
//   translation really exists — so this can never redirect into a 404.
// - Translated pages never auto-redirect (Googlebot crawls with en-US; a
//   redirect away from /fa/... would effectively de-index it).
//
// Preview locally with ?vh_lang=fa (same idea as the China bar's ?geo=CN).
(function () {
  "use strict";

  var STORAGE_KEY = "vh_lang";

  function getStored() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function setStored(lang) {
    try {
      localStorage.setItem(STORAGE_KEY, lang);
    } catch (e) {
      /* private mode — preference just won't persist */
    }
  }

  // Persist explicit selector choices (delegated: selector exists in header + offcanvas).
  document.addEventListener("click", function (ev) {
    var link = ev.target && ev.target.closest ? ev.target.closest("[data-vh-lang]") : null;
    if (link) setStored(link.getAttribute("data-vh-lang"));
  });

  var pageLang = (document.documentElement.getAttribute("lang") || "en").toLowerCase();
  if (pageLang !== "en") return; // only ever switch away from the default language

  var override = new URLSearchParams(location.search).get("vh_lang");
  var preferred =
    override ||
    getStored() ||
    (navigator.language || "").toLowerCase().split("-")[0];
  if (!preferred || preferred === "en") return;

  var alternate = document.querySelector(
    'link[rel="alternate"][hreflang="' + preferred + '"]'
  );
  if (!alternate || !alternate.href) return;

  setStored(preferred); // remember, so the switch happens at most once per visitor
  location.replace(alternate.href);
})();
