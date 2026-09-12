# Locale Gotchas

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
