# apple-dev-skills

> A **curated catalog of skills for AI coding agents** ([Claude Code](https://code.claude.com)) —
> built and collected from one developer's own shipping experience. First-party **Apple/Swift**
> and **AI-agent-collaboration** skills, plus best-of-breed **external** skill plugins aggregated
> **by reference** (credited to their authors, never copied).
>
> Languages: [English](README.md) · [繁體中文](README.zh-Hant.md)

This repo is one **marketplace** hosting two first-party plugins and several aggregated externals.

## Install

> Claude Code discovers shared skills through the **plugin** system. This repo is both a
> marketplace and the home of two first-party plugins.

### A — marketplace (simplest)

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 25 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 12 agent-collaboration skills
```

Install either or both. Externals install the same way, e.g. `/plugin install swiftui-expert@apple-dev-skills`.

### B — repo-level (vendored submodule, pinned)

Vendor + pin into one repo, then register a project-scope local-path marketplace so the
plugins load from the pinned submodule (collaborators are prompted to trust the workspace):

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v1.4.0 && cd -
```

`.claude/settings.json` (committed):

```json
{
  "extraKnownMarketplaces": {
    "apple-dev-skills": { "source": { "source": "directory", "path": "./.claude/skills/apple-dev-skills" } }
  },
  "enabledPlugins": {
    "apple-dev-skills@apple-dev-skills": true,
    "collaboration-skills@apple-dev-skills": true
  }
}
```

A bare submodule alone is **not** discovered — the marketplace registration is what loads the skills.

### C — `npx skills` (flat, no plugin)

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

## Catalog

### apple-dev-skills (25) — Apple/Swift

| Skill | One-liner |
|---|---|
| `swift6-concurrency` | Swift 6 language mode + complete concurrency checking; Sendable by default |
| `apple-platform-targets` | Default iOS 18 / macOS 15, Xcode 16+; bump to 26 only for latest-OS-only APIs |
| `swiftpm-modularization` | Single Package, multi-target, thin App, DI composition root, one-to-one tests |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot; protocol fakes; strict/tolerant snapshot gate |
| `xcode-cloud-single-track-ci` | Single-track Xcode Cloud; PR / Main / Release / Periodic; pre-merge PR CI |
| `mise-tool-management` | mise manages binary CLI tools; dev + CI share `.mise.toml`; macOS-only `os` guard |
| `oslog-logger-defaults` | `os.Logger` (no third-party); subsystem = bundle ID; `.private` default |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center; no third-party tracking; PrivacyInfo mandatory |
| `telemetry-facade-pattern` | One `Telemetry` target, fan-out facade; OSLog / NoOp / MetricKit / GameCenter sinks |
| `ai-translated-localization` | Default 7 locales; AI translation flow; `Localizable.xcstrings`; completeness gates |
| `ios-accessibility-engineering` | VoiceOver / Dynamic Type / touch-target / Reduce Motion for SwiftUI & UIKit; WCAG 2.2 |
| `swift-dependency-injection` | Protocol injection + composition root; environment vs constructor; `@TaskLocal`; Sendable |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch budgets / launch / memory / binary size / MetricKit |
| `apple-public-repo-security` | Three lines of defence for public iOS/macOS repos + rotate-first leak SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main` for ship-in-binary-but-out-of-diff IDs |
| `monetization-sdk-integration` | Add/upgrade/audit a monetization SDK; isolate `import` to one bridge file |
| `app-store-review-rejections` | Diagnose & pre-empt App Review rejection classes for free + ads + IAP + CloudKit + GC |
| `asc-api-automation` | ES256 JWT from the `.p8` + curl against the ASC REST API — TestFlight, metadata, submission, reports; no fastlane |
| `swiftui-interaction-footguns` | Known SwiftUI interaction bugs that slip past pure-code review |
| `swiftui-navigation-architecture` | Typed `Route` enum + `@Observable` router; value-based `NavigationStack`; per-transition presentation semantics with macOS fallbacks; deep links; per-tab paths |
| `app-icon-rasterize` | Rasterize a 1024 SVG icon to asset-catalog PNG via `qlmanage` — no Homebrew |
| `ios-design-mockup` | Single-file HTML iOS design mockup from a spec — iPhone frames + tokens |
| `interactive-simulator-ux-audit` | Drive a booted Simulator with `idb` (tap/describe/screenshot) to catch nav/modal/safe-area bugs snapshots can't |
| `host-driven-xcuitest-e2e` | Launch-the-app XCUITest E2E via Tuist — dedicated scheme wiring + macOS window-frame click driving |
| `cloudkit-schema-source-of-truth` | Committed `.ckdb` + `cktool` export/validate/deploy to Development; Production is a user-owned Console-only gate |

### collaboration-skills (12) — AI-agent process

| Skill | One-liner |
|---|---|
| `spec-phase-orchestration` | Pre-implementation doc pipeline; section-by-section approval |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer triad; round-1 cosmetic inline; limit(N) |
| `leader-developer-handoff-contract` | 5 required elements when dispatching a sub-agent |
| `agent-impl-notes-log` | Running impl-notes during a sub-agent task — decisions, deviations, open questions |
| `subagent-conflict-detection` | Check a new sub-agent's targets don't overlap an in-flight worktree |
| `methodology-pattern-extractor` | Extract patterns recurring ≥3 times from meeting logs |
| `session-to-meeting-log` | Consolidate a Claude Code session into a meeting log; summary, not verbatim |
| `pr-diff-verification` | Before push/PR, verify `git show --stat HEAD` matches the commit's claims |
| `backlog-routing-by-topic` | Route stray ideas by topic to the matching spec file's §Backlog |
| `claude-skill-plugin-packaging` | Distribute/install Claude Code skills — depth-1 rule, plugin + marketplace, aggregation |
| `skill-authoring-patterns` | Apple/Swift catalog layer over `superpowers:writing-skills` — router descriptions, bookend sections, two-tier references, evidence-based CR |
| `github-contribution-workflow` | gh-CLI contribution loop — PRs, issues, GitHub file ops, secrets, contribution-flow repo settings; conventions + CLEAN-before-merge |

### Aggregated external (5) — by reference, credited

Listed here but **not authored here**; they install from their authors' own repos (you get
their latest), credited in full. **Aggregate, don't appropriate**: only MIT-compatible,
non-duplicate plugins are listed — first-party skills are written only for genuine gaps.
The externals are broad **reference** ("here's the API / here's how to build X"); the
first-party skills sit a layer below as **opinionated defaults and shipped-it war stories**
(use iOS 18, one Package, swift-testing + snapshot, OSLog no-third-party, runtime bugs that
slipped past review). Where a topic overlaps, they differ by altitude, not duplication.

| Plugin | Author | Covers |
|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole (MIT) | Broad Apple frameworks — SwiftUI, SwiftData, App Intents, WidgetKit, StoreKit, HealthKit … |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI patterns, Swift Charts, Liquid Glass, Instruments toolchain |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI pitfalls, deprecated-API watchlist, iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | Ultra-compressed communication mode — cuts ~75% of tokens (general agent behavior) |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | "Lazy senior dev" mode — forces the simplest, shortest solution (general agent behavior) |

## Provenance

First-party skills were distilled and genericized from [`wei18/Sudoku`](https://github.com/wei18/Sudoku)'s
`.claude/skills/` — a spec-first, AI-Leader/Developer-built portfolio of shipping Apple-platform
games — plus original write-ups of public Apple / WCAG / Swift standards. Aggregated externals
remain their authors' work, surfaced by reference only. MIT — see [LICENSE](LICENSE).
