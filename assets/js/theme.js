// Colour theme: the visitor picks a *mode* (Auto, Dark or Light), and the page shows a
// *theme* (dark or light).
//
// Dark and Light apply to every page. Auto is the default: a showcase page stays dark and
// any other page follows the system setting (<html data-vh-auto-theme>, from the list in
// _config.yml). The static markup ships dark, so a page still reads without JavaScript.
// What this file does:
//
// - wires the theme menu (header + mobile off-canvas), marks the active mode, and keeps
//   the choice in localStorage("vh_theme"); Auto is the absence of a stored value;
// - follows a live change of the system setting while in Auto;
// - swaps <meta name="theme-color"> so the mobile browser chrome matches;
// - swaps decorative images that ship a light-theme counterpart via data-vh-light-src
//   (the dark original stays in `src`, so no-JS and dark visitors fetch only that one);
// - dispatches `vhThemeChange` so theme-aware canvases (the home globe) can recolour.
//
// The theme is applied to <html data-theme> BEFORE first paint by the inline bootstrap
// at the top of _includes/header.html — not here — so a light page never flashes dark.
// Preview a mode with ?vh_theme=auto|light|dark (does not overwrite the stored choice),
// mirroring ?vh_lang=fa and the China bar's ?geo=CN.
(function () {
  "use strict";

  var STORAGE_KEY = "vh_theme";
  var AUTO = "auto";
  var DARK = "dark";
  var LIGHT = "light";
  // Mobile browser chrome: the header's own backdrop colour in each theme.
  var THEME_COLOR = { dark: "#122272", light: "#f2f0fb" };

  var root = document.documentElement;
  var systemLight = window.matchMedia ? window.matchMedia("(prefers-color-scheme: light)") : null;

  // The bootstrap has already worked out the mode, a ?vh_theme= preview included.
  var mode = root.getAttribute("data-vh-theme-mode") || AUTO;

  function resolve() {
    if (mode !== AUTO) return mode;
    var followsSystem = root.getAttribute("data-vh-auto-theme") === "system";
    return followsSystem && systemLight && systemLight.matches ? LIGHT : DARK;
  }

  function store() {
    try {
      if (mode === AUTO) localStorage.removeItem(STORAGE_KEY);
      else localStorage.setItem(STORAGE_KEY, mode);
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

  function applyMenus() {
    var items = document.querySelectorAll("[data-vh-theme-set]");
    for (var i = 0; i < items.length; i++) {
      var active = items[i].getAttribute("data-vh-theme-set") === mode;
      items[i].classList.toggle("active", active);
      if (active) items[i].setAttribute("aria-current", "true");
      else items[i].removeAttribute("aria-current");
    }
  }

  function apply() {
    var theme = resolve();
    root.setAttribute("data-vh-theme-mode", mode);
    root.setAttribute("data-theme", theme);
    applyImages(theme);
    applyMeta(theme);
    applyMenus();
    document.dispatchEvent(new CustomEvent("vhThemeChange", { detail: { theme: theme } }));
  }

  // Delegated so it also covers the off-canvas copy, which Bootstrap may move/reflow.
  document.addEventListener("click", function (ev) {
    var item = ev.target && ev.target.closest ? ev.target.closest("[data-vh-theme-set]") : null;
    if (!item) return;
    mode = item.getAttribute("data-vh-theme-set");
    apply();
    store();
  });

  if (systemLight && systemLight.addEventListener) {
    systemLight.addEventListener("change", function () {
      if (mode === AUTO) apply();
    });
  }

  // Sync the rest of the page with what the pre-paint bootstrap decided. Not stored: a
  // ?vh_theme= preview must not overwrite the visitor's choice.
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", apply);
  } else {
    apply();
  }
})();
