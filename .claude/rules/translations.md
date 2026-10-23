---
paths:
  - "_data/i18n/**"
  - "vh_translator/**"
  - "_plugins/i18n-*.rb"
  - "tools/check-placeholders.py"
  - "assets/js/lang.js"
  - "_includes/lang-selector.html"
---

# Translations — [.docs/translations.md](.docs/translations.md)

Strings are translated by `vhtranslator` (`vh_translator/vhtranslator.json`, 12 languages, incremental via the committed watches); pages are cloned per language at build time by `_plugins/i18n-pages.rb` (opt out with `translate: false`). Fixes to a translation go in `vh_translator/prompt.txt` or `prompts/<lang>.prompt.txt`, never in the generated folder. **Never put an LRM in English source** — use `dir="ltr"` on the element. **Never encode spacing inside a string** (a `<span class="mx-3">` between two words, a padding `&nbsp;`) — words are separated by real spaces and the gap belongs in CSS, or the browser joins Arabic/Persian glyphs straight across the inline boundary; decorative `letter-spacing`/`word-spacing` is always `calc(<value> * var(--vh-tracking))`, which folds to 0 for the connected scripts (`fa`, `ar`, `hi`). A new key renders blank in other languages until CI translates it, so an include that reads data falls back per key (`{{ t.x | default: t_en.x }}`), as `faq.html`, `compare-table.html` and the chrome do. Keep `vh_translator/prompt.txt` short — it is sent with every batch in every language — and prefer a data file or a key name to a new rule. Preview with `?vh_lang=fa`.
