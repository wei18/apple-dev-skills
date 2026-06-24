# Curation log (Phase 3)

How candidates from the ecosystem are evaluated for inclusion, and the decisions
to date. Principle: **fill genuine gaps, do not bundle redundancy.** A high-star
external skill that overlaps what this library already covers is *recommended*, not
copied or aggregated. License must be compatible with an MIT library before any
content is adapted.

## Decisions

| Repo | ★ | License | Decision | Reason |
|---|--:|---|---|---|
| twostraws/SwiftUI-Agent-Skill | 4.2k | MIT | **Recommend (not bundled)** | Excellent SwiftUI pitfalls / iOS 26, but overlaps `swiftui-interaction-footguns`. Listed in README. |
| AvdLee/SwiftUI-Agent-Skill | 3.1k | MIT | **Recommend (not bundled)** | SwiftUI patterns + Instruments toolchain; overlaps our SwiftUI coverage. Listed in README. |
| (accessibility) dadederk/iOS-Accessibility-Agent-Skill + cvs-health/ios-swiftui-accessibility-techniques | 159 / 363 | MIT / Apache-2 | **Adopted (adapted)** → `ios-accessibility-engineering` | A real gap (zero a11y coverage). Wrote an original first-party skill distilling the practice; both sources license-compatible. |
| (DI) pointfreeco/swift-dependencies, Factory | 2.2k | MIT | **Adopted (adapted)** → `swift-dependency-injection` | Gap (no DI skill). Original skill referencing the libraries as options. |
| twostraws/Swift-Agent-Skills | 2.1k | MIT | **Gap-map (defer)** | Not a CC plugin (no manifest). Use as a roadmap for future first-party skills (SwiftData / App Intents / WidgetKit / performance). |
| kodecocodes/swift-style-guide | 13.2k | **NOASSERTION** | **Skip** | License unclear → don't adapt. If a naming skill is wanted, distil Apple's API Design Guidelines (the authoritative public source) instead. |
| dpearson2699/swift-ios-skills | 790 | **PolyForm Perimeter** (non-compete) | **Skip** | Non-compete license is incompatible with endorsing/aggregating in a public MIT library. |
| ochococo/Design-Patterns-In-Swift | 15.3k | **GPL-3.0** | **Skip** | Copyleft — incompatible. |
| futurice/ios-good-practices | 11k | **CC-BY-4.0** | **Skip** | Attribution-share license + stale; adapt-risk. |
| awesome-* lists (matteocrippa, onmyway133) | 26k / 5.3k | — | **Skip** | Link directories, not extractable skill content. |
| adapty / vendor-SDK skills | <10 | — | **Skip** | Vendor-specific, overlaps `monetization-sdk-integration`. |
| anthropics/claude-plugins-official + community | 31k / 208 | Apache | **Skip** | No Swift-first plugins as of this survey; monitor. |

## Known gaps to fill next (first-party, from the gap-map)

SwiftData / Core Data persistence · App Intents / Siri · WidgetKit / Live Activities ·
performance engineering (Instruments / MetricKit-as-telemetry / hang & launch) ·
iOS 26 Liquid Glass migration. These are candidates for future first-party skills
rather than external bundling.

_Survey method: two parallel research agents (CC-native plugins + adjacent knowledge
repos), star/license/recency verified via `gh api`, Leader-reconciled._
