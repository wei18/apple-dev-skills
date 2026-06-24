# Roadmap & alignment

The forward agenda for this library, plus a check of what shipped against the
original spec/plan (`wei18/Sudoku` `docs/superpowers/specs|plans/2026-06-24-apple-dev-skills-*`).

## Status

| Phase | Goal | Status | Shipped |
|---|---|---|---|
| **1 — Extract** | Move portable skills out of a real project, genericize, consume back | ✅ v0.1.0 | 26 skills genericized + 3-way CR; submodule + committed project-scope marketplace |
| **2 — Standalone library** | SSOT README · npm install · aggregate other repos | ✅ v0.2.0–0.3.0 | README SSOT (+zh-Hant); `npx skills add` path; aggregation mechanism skill |
| **3 — Curate ecosystem** | Survey high-star Swift repos → adopt/replace/skip | ✅ v0.3.0 | [CURATION.md](CURATION.md); adopted 3 gap skills; recommended externals |

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

## Next (P4+ — candidates, not committed)

From the [CURATION.md](CURATION.md) gap-map — future **first-party** skills (write, don't bundle):

- **SwiftData / Core Data** persistence patterns.
- **App Intents / Siri** + **WidgetKit / Live Activities**.
- **Performance engineering** — Instruments workflow, MetricKit-as-telemetry, hang/launch/binary-size.
- **iOS 26 / Liquid Glass** migration patterns (or keep deferring to the recommended external SwiftUI skills).

Operational:
- Periodic ecosystem re-survey (P3 is ongoing, not one-shot).
- Keep consuming repos' submodule pins current as the library tags new releases.
- Consider listing in a public marketplace (e.g. `claude-plugins-community`) for discoverability once stable.
