// Colour theme (dark ⇄ light).
//
// Dark is the site default and the theme the static markup ships with, so this file
// never has to run for a first-time visitor to see the intended page. What it does:
//
// - wires the toggle buttons (header + mobile off-canvas) and persists the choice in
//   localStorage("vh_theme");
// - keeps each toggle's accessible name describing the *action* ("Switch to light
//   theme" / "Switch to dark theme");
// - swaps <meta name="theme-color"> so the mobile browser chrome matches;
// - swaps decorative images that ship a light-theme counterpart via data-vh-light-src
//   (the dark original stays in `src`, so no-JS and dark visitors fetch only that one);
// - dispatches `vhThemeChange` so theme-aware canvases (the home globe) can recolour.
//
// The theme is applied to <html data-theme> BEFORE first paint by the inline bootstrap
// at the top of _includes/header.html — not here — so a stored light preference never
// flashes dark. Preview either theme with ?vh_theme=light|dark (does not overwrite the
// stored choice), mirroring ?vh_lang=fa and the China bar's ?geo=CN.
(function () {
  "use strict";

  var STORAGE_KEY = "vh_theme";
  var DARK = "dark";
  var LIGHT = "light";
  // Mobile browser chrome: the header's own backdrop colour in each theme.
  var THEME_COLOR = { dark: "#122272", light: "#f2f0fb" };

  var root = document.documentElement;

  function current() {
    return root.getAttribute("data-theme") === LIGHT ? LIGHT : DARK;
  }

  function setStored(theme) {
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      /* private mode — the preference just won't outlive the page */
    }
  }

  // Decorative art that has a light-theme counterpart carries it in data-vh-light-src.
  // Swapping `src` (rather than shipping both and hiding one) keeps the extra file off
  // the critical path for the default theme.
  function applyImages(theme) {
    var imgs = document.querySelectorAll("img[data-vh-light-src]");
    for (var i = 0; i < imgs.length; i++) {
      var img = imgs[i];
      if (!img.dataset.vhDarkSrc) img.dataset.vhDarkSrc = img.getAttribute("src");
      var next = theme === LIGHT ? img.dataset.vhLightSrc : img.dataset.vhDarkSrc;
      if (next && img.getAttribute("src") !== next) img.setAttribute("src", next);
    }
  }

  function applyMeta(theme) {
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", THEME_COLOR[theme]);
  }

  function applyToggles(theme) {
    // The button offers the *other* theme, so it is labelled with that action.
    var toggles = document.querySelectorAll("[data-vh-theme-toggle]");
    for (var i = 0; i < toggles.length; i++) {
      var btn = toggles[i];
      var label = theme === LIGHT ? btn.dataset.vhLabelDark : btn.dataset.vhLabelLight;
      if (!label) continue;
      btn.setAttribute("aria-label", label);
      btn.setAttribute("title", label);
    }
  }

  function apply(theme, persist) {
    root.setAttribute("data-theme", theme);
    applyImages(theme);
    applyMeta(theme);
    applyToggles(theme);
    if (persist) setStored(theme);
    document.dispatchEvent(new CustomEvent("vhThemeChange", { detail: { theme: theme } }));
  }

  // Delegated so it also covers the off-canvas copy, which Bootstrap may move/reflow.
  document.addEventListener("click", function (ev) {
    var btn = ev.target && ev.target.closest ? ev.target.closest("[data-vh-theme-toggle]") : null;
    if (!btn) return;
    ev.preventDefault();
    apply(current() === LIGHT ? DARK : LIGHT, true);
  });

  // Sync the rest of the page with whatever the pre-paint bootstrap decided. Not
  // persisted: a ?vh_theme= preview must not overwrite the visitor's stored choice.
  function init() {
    apply(current(), false);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
