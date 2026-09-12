# Xcstrings Format And Tooling Notes

### Tooling notes

- xcstrings is JSON; parse with any JSON library. Schema: `{"version": "1.0", "sourceLanguage": "en", "strings": {<key>: {"localizations": {<locale>: {"stringUnit": {"state": "translated", "value": "..."}}}}}}`. The top-level `"version"` field auto-bumps to `1.1` when Xcode 26's type-safe symbol generation or AI-generated comments touch the catalog — preserve it verbatim when splicing (see the splice footgun above).
- Plural variations use `{"variations": {"plural": {<cldr-form>: {"stringUnit": {...}}}}}` instead of a single `stringUnit`.
- When fanning out via an LLM, send a single key + source + glossary in the prompt; don't batch hundreds at once (latency wins less than accuracy loses).
- For ASC metadata (App Store description, keywords, "what's new"), use the **same flow** but route to the ASC API endpoints rather than xcstrings. The translation principles (length budget, register, gotchas) apply identically.
