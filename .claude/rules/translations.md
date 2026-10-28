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

**Translate strings yourself before every commit**: every new or changed key of `_data/i18n/en/`, in all 12 languages, into `_data/i18n/<lang>/`, by `vh_translator/prompts/<lang>.prompt.txt` (NAMES, TERMS, KEYWORDS, RULES). `dotnet tool run vhtranslator -- --show-changes` lists the keys; once each is translated, `-- --ignore-changes` rewrites the watches to the current English, so CI's `vhtranslator` (`vh_translator/vhtranslator.json`) has nothing left. It is only the fallback: a key you leave for it must be missing from the target file, since a missing key is always translated but a stale one is not once the watches are current. Write each file as the tool does — English key order, two-space JSON, no trailing newline, non-ASCII as is except U+00A0 — keep every `[placeholder]`, `<code>` span and tag, and in `fa`/`ar` put an LRM after a Latin word's `!`/`?` when an RTL word or the string's end follows (`VpnHood!` + U+200E). A fix that follows a rule (a name, a term, the register) also goes in that language's prompt, so the fallback keeps to it. Pages are cloned per language at build time by `_plugins/i18n-pages.rb` (opt out with `translate: false`). **Never put an LRM in English source** — use `dir="ltr"` on the element. **Never encode spacing inside a string** (a `<span class="mx-3">` between two words, a padding `&nbsp;`) — words are separated by real spaces and the gap belongs in CSS, or the browser joins Arabic/Persian glyphs straight across the inline boundary; decorative `letter-spacing`/`word-spacing` is always `calc(<value> * var(--vh-tracking))`, which folds to 0 for the connected scripts (`fa`, `ar`, `hi`). A key left to CI renders blank in other languages until CI translates it, so an include that reads data falls back per key (`{{ t.x | default: t_en.x }}`), as `faq.html`, `compare-table.html` and the chrome do. Keep `vh_translator/prompt.txt` short — it is sent with every batch in every language — and prefer a data file or a key name to a new rule. Preview with `?vh_lang=fa`.
