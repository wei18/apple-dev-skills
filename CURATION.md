# Curation log (Phase 3)

**Principle: aggregate, don't appropriate.** When a good external skill exists, list
it **by reference** in our marketplace (it installs from the author's repo, fully
credited) — never copy or re-implement it as a first-party skill. Write first-party
skills **only** for topics that no compatibly-licensed external Claude Code *plugin*
covers. License must be MIT-compatible to aggregate.

## Decisions

| Repo | ★ | License | CC plugin? | Decision | Reason |
|---|--:|---|---|---|---|
| [vabole/apple-skills](https://github.com/vabole/apple-skills) | ~270 | MIT | ✅ | **Aggregate** (`apple-skills@apple-dev-skills`) | Broad Apple-framework coverage (SwiftData, App Intents, WidgetKit, StoreKit, HealthKit, …). Reference, don't reimplement. |
| [AvdLee/SwiftUI-Agent-Skill](https://github.com/AvdLee/SwiftUI-Agent-Skill) | ~3.1k | MIT | ✅ | **Aggregate** (`swiftui-expert@apple-dev-skills`) | SwiftUI patterns + Instruments toolchain, high authority. |
| [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) | ~4.2k | MIT | ✅ | **Aggregate** (`swiftui-pro@apple-dev-skills`) | SwiftUI pitfalls / iOS 26, by Paul Hudson. |
| dadederk/iOS-Accessibility-Agent-Skill | ~160 | MIT | ❌ (no manifest) | **Gap → first-party** `ios-accessibility-engineering` | Not a CC plugin, so not aggregatable by marketplace. Wrote an original skill from public Apple HIG / WCAG (no repo copied); links the source as a reference. |
| pointfreeco/swift-dependencies, Factory | ~2.2k | MIT | ❌ (a library) | **Gap → first-party** `swift-dependency-injection` | A Swift library, not a skill plugin. Original write-up; mentions the libraries as options. |
| (performance / Instruments / MetricKit) | — | — | ❌ | **Gap → first-party** `ios-performance-engineering` | No aggregatable plugin; original from public Apple docs. |
| dpearson2699/swift-ios-skills | ~790 | PolyForm Perimeter | ✅ | **Skip** | Non-compete license — incompatible with aggregation in a public MIT catalog. |
| ochococo/Design-Patterns-In-Swift | ~15k | GPL-3.0 | ❌ | **Skip** | Copyleft. |
| futurice/ios-good-practices | ~11k | CC-BY-4.0 | ❌ | **Skip** | Attribution-share + stale. |
| awesome-* lists, vendor-SDK skills, official marketplaces | — | — | — | **Skip** | Link directories / vendor-specific / no Swift-first content. |

## Course correction (2026-06-24)

An earlier pass wrote first-party skills that **duplicated** aggregatable external
plugins — that re-implements others' work without credit. Corrected: those four were
removed and replaced by the aggregated plugins above:

- ~~`swiftui-state-and-composition`~~ → covered by `swiftui-expert` / `swiftui-pro`
- ~~`swiftdata-persistence`~~ · ~~`app-intents-and-shortcuts`~~ · ~~`widgetkit-and-live-activities`~~ → covered by `apple-skills`

Only the three genuine-gap skills (accessibility, dependency injection, performance)
remain first-party, because no compatibly-licensed external plugin packages them.

_Survey method: two parallel research agents; star / license / manifest verified via `gh api`; Leader-reconciled._
