# Roadmap & alignment

The forward agenda for this library, plus a check of what shipped against the
original spec/plan (`wei18/Sudoku` `docs/superpowers/specs|plans/2026-06-24-apple-dev-skills-*`).

## Status

| Phase | Goal | Status | Shipped |
|---|---|---|---|
| **1 — Extract** | Move portable skills out of a real project, genericize, consume back | ✅ v0.1.0 | 26 skills genericized + 3-way CR; submodule + committed project-scope marketplace |
| **2 — Standalone library** | SSOT README · `npx` install · a marketplace that can aggregate other repos | ✅ v0.2.0–0.3.0 | README SSOT (+zh-Hant); `npx skills add` path; `claude-skill-plugin-packaging` |
| **3 — Curate & aggregate** | Survey high-star Swift repos → aggregate by reference / first-party only for gaps | ✅ v0.5.0 | [CURATION.md](CURATION.md); aggregated 3 external plugins (credited); 3 first-party gap skills; **removed earlier reimplementations** |

## Course correction (v0.4.0 → v0.5.0)

v0.4.0 wrote first-party skills (`swiftui-state-and-composition`, `swiftdata-persistence`,
`app-intents-and-shortcuts`, `widgetkit-and-live-activities`) that **duplicated**
aggregatable community plugins — re-implementing others' work without credit.
**v0.5.0 corrected this**: those four were removed and replaced by *aggregating* the
originals by reference (`apple-skills` / `swiftui-expert` / `swiftui-pro`, credited to
vabole / AvdLee / twostraws). Only the three genuine-gap skills with no aggregatable
plugin (accessibility, dependency injection, performance) remain first-party.

## Alignment: spec/plan → implementation

| Spec/plan item | Planned | Shipped | Note |
|---|---|---|---|
| P1 extract mechanism | `git filter-repo` | **fresh-copy** | User chose clean history for a new public repo; source history stays in Sudoku. |
| P1 consumption | submodule | submodule **+ plugin marketplace** | Bare submodule isn't discovered (depth-1); marketplace is the real mechanism. Spec §3 updated. |
| P2(b) npm | a custom npm package | **existing `vercel-labs/skills` CLI** | No custom build; our `SKILL.md` layout is already compatible. |
| P2(c)/P3 aggregate others | submodule/import external repos | **aggregate by reference in `marketplace.json`** | The correct, attribution-preserving mechanism — externals install from their authors' repos. (Initial pass wrongly reimplemented; corrected in v0.5.0.) |

Feasibility items from spec §3 — both **resolved**: npm mechanism (`skills` CLI);
nested aggregation (marketplace multi-source `plugins[]`).

## Next (candidates, not committed)

- First-party only where no compatibly-licensed external plugin exists: networking /
  `URLSession` + structured concurrency; watchOS / visionOS / App Clips.
- Aggregate more high-quality MIT Swift skill plugins as the ecosystem grows (issue-driven).
- Periodic ecosystem re-survey (curation is ongoing, not one-shot).

Operational:
- Keep consuming repos' submodule pins current as the library tags releases.
- Consider listing in a public marketplace (e.g. `claude-plugins-community`) once stable.
