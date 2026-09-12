# L10n Gate Scope And Blind Spots

### L10n gate scope — and its two blind spots

If the repo has a per-key completeness gate (recommended, see Step 5), it checks **per-key
locale completeness**: every key present in a catalog has all declared locales, no `<TRANSLATE>`.
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
2. **Multi-app repos sharing UI modules only:** a key referenced from shared UI code
   but absent from an app's catalog. Per-key completeness alone will NOT catch this
   — the gate only validates keys that already exist in a catalog, so a key
   referenced from a shared UI module that the app's own catalog never declares
   renders raw at runtime while the gate stays green. **Build a shared-code
   dotted-key gate:** every dotted-namespace key (e.g. `leave.game.close`,
   `att.primer.title`) referenced from a shared UI module (SharedUI / SettingsUI /
   any shared UI module) must exist in **every** app catalog or CI fails. Scope it
   to *dotted* keys to avoid app-conditional English-phrase false positives —
   English-phrase shared keys are a separate, harder case (no dotted namespace to
   anchor on; track them with a dedicated audit rather than this gate).
