# Roadmap & alignment

The forward agenda for this library, plus a check of what shipped against the
original spec/plan (`wei18/Sudoku` `docs/superpowers/specs|plans/2026-06-24-apple-dev-skills-*`).

## Status

| Phase | Goal | Status | Shipped |
|---|---|---|---|
| **1 — Extract** | Move portable skills out of a real project, genericize, consume back | ✅ v0.1.0 | 26 skills genericized + 3-way CR; submodule + committed project-scope marketplace |
| **2 — Standalone library** | SSOT README · npm install · aggregate other repos | ✅ v0.2.0–0.3.0 | README SSOT (+zh-Hant); `npx skills add` path; aggregation mechanism skill |
| **3 — Curate ecosystem** | Survey high-star Swift repos → adopt/replace/skip | ✅ v0.3.0 | [CURATION.md](CURATION.md); adopted 3 gap skills; recommended externals |
| **4 — Fill gap-map** | First-party skills for surveyed gaps | ✅ v0.4.0 | swiftdata-persistence · app-intents-and-shortcuts · widgetkit-and-live-activities · ios-performance-engineering |

## Alignment: spec/plan → implementation

High alignment. Three **intentional, user-approved deviations** (no unintentional drift):

| Spec/plan item | Planned | Shipped | Note |
|---|---|---|---|
| P1 extract mechanism | `git filter-repo` (history-preserving) | **fresh-copy** | User chose clean history for a new public repo; source history stays in Sudoku. |
| P1 consumption | submodule | submodule **+ plugin marketplace** (committed `.claude/settings.json`) | Verified: bare submodule isn't discovered (depth-1); marketplace is the real mechanism. Spec §3 updated to match. |
| P2(b) npm | a custom npm package | **existing `vercel-labs/skills` CLI** | No custom build needed; our `SKILL.md` layout is already compatible. |
| P2(c) aggregate others | submodule/aggregate external repos | **mechanism documented, not exercised** | No non-redundant, license-clean external CC-plugin qualified → recommend (README) instead of bundle. |
| P3 "adopt" | submodule/import their plugin | **adopt by writing first-party skills** (a11y, DI, SwiftUI) | External SwiftUI plugins overlapped ours; gap content (a11y/DI) wasn't a CC plugin → adapted original skills. |

Feasibility items flagged in spec §3 — both **resolved**: npm mechanism (`skills` CLI); nested aggregation (marketplace multi-source `plugins[]`, documented in `claude-skill-plugin-packaging`).

## Phase 4 — fill the gap-map (✅ v0.4.0)

First-party skills written for the gaps the survey found (not bundled):
`swiftdata-persistence` · `app-intents-and-shortcuts` · `widgetkit-and-live-activities` ·
`ios-performance-engineering`. **iOS 26 / Liquid Glass** intentionally deferred to the
recommended external SwiftUI skills (redundant with our SwiftUI coverage).

## Next (P5+ — candidates, not committed)

- Networking / `URLSession` + structured concurrency patterns; Swift on the server boundary.
- watchOS / visionOS / App Clips targets (per the broader-platform survey findings).
- A periodic ecosystem re-survey (P3 is ongoing).

Operational:
- Periodic ecosystem re-survey (P3 is ongoing, not one-shot).
- Keep consuming repos' submodule pins current as the library tags new releases.
- Consider listing in a public marketplace (e.g. `claude-plugins-community`) for discoverability once stable.
