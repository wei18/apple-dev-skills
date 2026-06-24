---
name: ai-translated-localization
description: Default localization scope AND execution playbook for Apple-platform Apps — 7 locales (en, zh-Hant, zh-Hans, ja, ko, es, th) translated via AI agent flow using `Localizable.xcstrings`. Source = en, primary = zh-Hant. Minimum set zh-Hant + en. Invoke when (1) deciding L10n scope / catalog format / translation flow at project setup, OR (2) actually executing a translation pass to add or refresh strings.
---

# AI-Translated Localization

## When to invoke

**Scope decisions:**
- Starting a new App and deciding which locales to support.
- Choosing a string catalog format (`.strings` vs `.xcstrings`).
- Planning the translation flow (manual / agency / AI agent).
- User asks "are 7 locales too many", "how do translations enter git", "how to handle multi-locale App Store metadata".

**Execution:**
- Adding new user-facing strings (UI keys, GC titles, ASC metadata, achievement descriptions) and need to fill out their non-source locales.
- Refreshing strings whose source language changed (`extractionState: stale` entries in xcstrings).
- Auditing whether a release's xcstrings is complete (every key has every locale, no `<TRANSLATE>` placeholders shipping).

## Default decisions

### Default 7 locales

| Locale | Code | Notes |
|---|---|---|
| English | `en` | Catalog `sourceLanguage`; translation source for the fan-out |
| Traditional Chinese | `zh-Hant` | Primary language — author-written alongside `en`, never AI-translated |
| Japanese | `ja` | Largest adjacent market outside the Chinese sphere |
| Simplified Chinese | `zh-Hans` | Converted from `zh-Hant` + Mainland phrasing review |
| Spanish | `es` | World's second largest native-speaker base |
| Thai | `th` | Southeast Asia representative |
| Korean | `ko` | High-penetration Asian market |

- Locale codes are the **script-based BCP-47 forms** (`zh-Hant` / `zh-Hans`), not region
  forms (`zh-TW` / `zh-CN`) — matches the committed catalogs and your repo's L10n completeness gate.
- **Minimum set**: zh-Hant + en (every project includes at least these two).
- Per-project locale lists can be adjusted, but **English and zh-Hant are always included**.

### Translation flow

- **Handled by an AI agent**, recorded as a step in `plan.md`: "author `en` + `zh-Hant` by hand, fan out the other 5 locales from `en`, write into `Localizable.xcstrings`" (see Execution playbook Step 1).
- Covers:
  - In-app strings
  - Game Center leaderboard / achievement names (for games)
  - App Store metadata (title / description / keywords / what's new)
  - Description text inside the Privacy Manifest
- Every time strings are added / modified, run another round of the AI translation flow; the diff lands in a PR.

### Catalog format

- Use Xcode's **`Localizable.xcstrings`** (String Catalog, introduced in Xcode 15+).
- Stop using legacy `.strings` / `.stringsdict` (unless an external tool forces it).
- xcstrings is JSON-structured: PR-friendly diffs and easy for AI to manipulate.

## Rationale

- 7 locales cover most of the global market while remaining a polish scope a solo developer can sustain.
- AI translation quality for App UI strings (short, clear context) is at commercial level; long marketing copy is still recommended for human review.
- xcstrings JSON structure is naturally friendly to AI / diff / version control.
- `zh-Hant` as primary reflects the author's native-language accuracy; `en` is the
  fan-out source because translator competence is broader from English (see Field notes).

## Deviation considerations

- **Focused target market**: shrink to zh-Hant + en + one target-market locale.
- **No budget / no time**: ship zh-Hant + en first; mark others as `extractionState: stale` for later.
- **Regulated / sensitive content** (medical / financial / kids): **mandatory human review** after AI translation; add a review step to `plan.md`.
- **Special scripts / RTL** (Arabic / Hebrew): UI needs additional layout verification, not just translation.

## Execution playbook

Use when actually performing a translation pass. The flow is **source-pair seed → AI fan-out → tricky-case review → completeness check**.

### Step 1 — Seed source pair (en + zh-Hant)

- Source language for translation **must be English** (broader translator competence across all target locales than zh-Hant).
- Authors write English first; zh-Hant is the project's primary native locale and is hand-written in parallel — *not* AI-translated from English. Both are written by the author with intent; the other 5 locales fan out from `en`.
- Each new key lands in xcstrings with **at minimum** `en` + `zh-Hant` populated and `extractionState: manual`.
- Other 5 locales (`ja`, `zh-Hans`, `es`, `th`, `ko`) start either absent or with the placeholder string `<TRANSLATE>` so the fan-out pass can find them with a single grep.

### Step 2 — AI fan-out pass

For each target locale, translate each key from `en` (source-of-truth) into the target locale. The AI doing the translation should:

- **Preserve substitutions**: `%@`, `%lld`, `%1$@`, `\n`, markdown markers (`**`, `_`), and any `${...}` interpolation tokens are copied verbatim.
- **Match plural/variation forms**: if xcstrings declares plural variations for `en`, all forms must exist in the target locale (`zero` / `one` / `two` / `few` / `many` / `other`) per CLDR plural categories for that locale — don't blindly copy English's two forms.
- **Match length budget**: if source is a button label (≤ 12 chars typical), keep target short. Don't let "OK" become a 6-word phrase. UI labels lose to long translations.
- **Match register / tone**: derive from `en`'s tone. Buttons are imperative, descriptions are neutral, error messages are direct. Don't add politeness markers absent in source (see locale gotchas below).
- **Preserve product nouns**: app name, brand terms, mode names that share visual identity across locales (e.g., "Practice" → 練習 in both zh-Hant and ja for visual consistency). Maintain a small **glossary** captured per-project to enforce this.

After translation, set `extractionState: translated` (per Apple xcstrings convention) so Xcode no longer flags the key as needing attention.

### Step 3 — Tricky-case review (locale-specific gotchas)

Lessons captured from real translation passes. Apply these as a second-pass review after the bulk AI fan-out.

**Japanese (`ja`):**
- Prefer **semantic** over literal. "Pencil" (notes / candidate input) → メモ, NOT 鉛筆. The literal kanji confuses Japanese users; the semantic UI term is correct.
- Drop politeness markers (`です` / `ます`) in button labels and short UI strings — Japanese app UIs are typically declarative/imperative, not polite.
- 漢字 vs かな: prefer 漢字 for nouns, ひらがな for particles, カタカナ for loanwords. Don't romanize unless the source is romanized.

**Thai (`th`):**
- **No politeness markers** (`ครับ` / `ค่ะ`) in UI strings unless the app's voice is deliberately conversational. Calm/neutral apps drop them.
- Compound nouns: "leaderboard" → กระดานผู้นำ (no single-word equivalent). Accept the multi-word form.
- Thai has **no word boundaries** — sentence length affects line break behavior. UI strings >24 chars need spot-check rendering.

**Korean (`ko`):**
- Use **informal-formal** style (해요체) for app UI by default — neither too casual (반말) nor overly formal (합쇼체).
- 한자 should be avoided unless disambiguation is needed; pure 한글 is the modern default.
- Postpositions (조사) change based on preceding character's final consonant; AI usually handles this, but spot-check `을/를`, `이/가`, `은/는`.

**Spanish (`es`):**
- Default to **neutral Latin American Spanish** unless the project explicitly targets Spain (`es-ES`). Avoid `vosotros` forms; use `ustedes`.
- Gender agreement: nouns referring to the user (e.g., "completed") need gender-neutral phrasing if the user's gender is unknown.

**Simplified Chinese (`zh-Hans`):**
- Convert from `zh-Hant` (not from `en`) for terminology consistency; the AI still needs to substitute Mainland-preferred terms (软件 vs 軟體, 移动 vs 行動, 视频 vs 影片).
- DON'T just run `tongwen` character conversion — phrase choice differs (e.g., zh-Hant 「設定」 → zh-Hans 「设置」, not 「設定 → 设定」).

**English (`en`):**
- US English by default. UK spellings (`colour`, `centre`, `analyse`) only if explicitly targeted.
- Sentence case for buttons and UI; Title Case only for proper nouns and app section headers.

### Step 4 — Visual / glossary consistency

Beyond per-string correctness, enforce a project-level glossary so the same concept renders identically across locales and screens:

- **Mode names** (e.g., "Daily" / "Practice") — pick one term per locale and use it everywhere (HomeView card, hub header, navigation title, Settings labels).
- **Product nouns** (app name, branded features) — don't translate.
- **Difficulty labels** (Easy / Medium / Hard) — short, consistent.
- **Action verbs** (Submit / Confirm / Cancel) — match iOS native terminology in each locale (Apple has localized Human Interface Guidelines for major locales).

Maintain the glossary as either inline comments in xcstrings, or a sidecar `Localization-Glossary.md` in `docs/` if it grows.

### Step 5 — Completeness check (before PR)

Verification gates before merging a translation pass:

- `<TRANSLATE>` count across xcstrings = 0 (none shipped).
- `extractionState: stale` count = 0 (all stale entries refreshed).
- Per-key locale coverage = 100% (parse xcstrings JSON; every `localizations` dict has every declared locale).
- For plural keys: every locale has every plural form required by CLDR for that locale.
- Substitution token parity per key: `en` has N `%@` → all locales have N `%@` (or locale-specific reordering via `%1$@` / `%2$@`).
- Spot-check 3-5 keys per locale visually in the simulator with `Scheme → Run → Options → App Language`.

### L10n gate scope — and its two blind spots

Your repo's L10n completeness gate (CI-enforced) checks **per-key locale
completeness**: every key present in a catalog has all declared locales, no `<TRANSLATE>`.
Two things it does **NOT** catch — both have shipped English-fallback bugs in real projects:

1. **A required key being *absent* entirely.** The gate validates keys that
   exist; it cannot know a newly-activated capability *needs* a key that no
   catalog has. When an app adopts a shared feature (audio settings, ATT primer,
   reminders), its catalog can ship missing keys → the UI renders raw dotted keys
   or English literals, and the gate stays green. After wiring any shared-UI
   capability into a new app, **diff its catalog's key set against an app that
   already has the feature** (real-world: a new game adopted shared audio-settings
   UI without copying the required catalog keys; another adopted an ATT primer
   and the raw dotted keys appeared at runtime — both passed the gate).
2. **A key referenced from shared UI code but absent from an app's catalog.**
   Per-key completeness alone will NOT catch this — the gate only validates keys
   that already exist in a catalog, so a key referenced from a shared UI module
   that the app's own catalog never declares renders raw at runtime while the gate
   stays green. **Build a shared-code dotted-key gate:** every dotted-namespace key
   (e.g. `leave.game.close`, `att.primer.title`) referenced from a shared UI module
   (SharedUI / SettingsUI / any shared UI module) must exist in **every** app
   catalog or CI fails. Scope it to *dotted* keys to avoid app-conditional
   English-phrase false positives — English-phrase shared keys are a separate,
   harder case (no dotted namespace to anchor on; track them with a dedicated
   audit rather than this gate).

### xcstrings editing footgun

When adding keys to a `Localizable.xcstrings`, **text-splice** the new entries
into the file — do **not** round-trip the whole catalog through a Python/JSON
`load → dump`. The round-trip reformats Xcode's style (`"k" : v` space-before-
colon + Xcode key order) and produces a multi-thousand-line noise diff that
buries the real change. Splicing keeps a clean, reviewable diff (real example:
4400-line noise diff collapsed to 192 lines after switching to splice approach).

### Tooling notes

- xcstrings is JSON; parse with any JSON library. Schema: `{"sourceLanguage": "en", "strings": {<key>: {"localizations": {<locale>: {"stringUnit": {"state": "translated", "value": "..."}}}}}}`.
- Plural variations use `{"variations": {"plural": {<cldr-form>: {"stringUnit": {...}}}}}` instead of a single `stringUnit`.
- When fanning out via an LLM, send a single key + source + glossary in the prompt; don't batch hundreds at once (latency wins less than accuracy loses).
- For ASC metadata (App Store description, keywords, "what's new"), use the **same flow** but route to the ASC API endpoints rather than xcstrings. The translation principles (length budget, register, gotchas) apply identically.

## Verification checklist

- `Localizable.xcstrings` exists and each key has 7 locale entries (2 for the minimum set).
- App Store Connect metadata is complete per locale (including screenshot captions).
- Game Center / achievement display names are complete per locale.
- `PrivacyInfo.xcprivacy` description itself doesn't need to be multi-locale, but the corresponding App Store privacy policy page does.

## Related skills

- `apple-platform-targets`: xcstrings requires Xcode 15+; aligns with the deployment target's toolchain.
- `spec-phase-orchestration`: "translation" should be an explicit step in `plan.md`.

## Field notes

Real translation passes have surfaced these recurring decisions:

- **Source = `en`, primary = `zh-Hant`** — both written by author. The other 5 fan out from `en` because translator competence is broader from English than from Chinese for `th` / `ko` / `es`.
- **Glossary beats per-string correctness** — visual consistency across screens matters more than the perfect translation of any single string.
- **5 locales in one pass is the sweet spot** — fewer wastes the per-pass setup; more risks AI fatigue degradation on the last locales. 1 commit per locale keeps PR review tractable.
