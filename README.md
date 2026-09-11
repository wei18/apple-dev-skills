# apple-dev-skills

> Skills for vibe coding iOS & Apple-ecosystem apps with Claude Code — and for driving
> the agent that builds them.
>
> Languages: [English](README.md) · [繁體中文](README.zh-Hant.md) · [简体中文](README.zh-Hans.md) · [日本語](README.ja.md)

apple-dev-skills is one **marketplace** for independent developers and small teams
taking an idea to a shipped App Store release. Its first-party skills come in two halves:
**Apple/Swift** skills for what you are building, and **harness engineering** skills for
how you direct Claude Code itself — planning, reviewing, and shipping the work. Every
skill is an opinionated default backed by a shipped-it war story and held to a consistency
gate. Alongside them sit best-of-breed **external** skill plugins, **aggregated by
reference** — not written here, linked and credited to their authors, never copied.

## Quickstart

> Skills trigger automatically from what you ask for — install, then just describe the task.

Inside a Claude Code session, run:

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills          # 26 Apple/Swift skills
/plugin install collaboration-skills@apple-dev-skills      # 12 agent-collaboration skills
```

If the install summary says `Run /reload-plugins to activate.`, run it — older clients always need it.

Install either or both. Externals install the same way, e.g. `/plugin install swiftui-expert@apple-dev-skills`.

Then just describe the task:

- *"I'm starting a new iOS app"* → `apple-platform-targets` answers the deployment target and
  hands off to the package shape, language mode, and test baseline in order.
- *"App Review bounced this on guideline 5.1.2"* → `app-store-review-rejections` maps the
  guideline to the fix.

To force one, use its slash command: `/apple-dev-skills:swift6-concurrency`. `/skills` lists
what is installed and which plugin each skill came from.

> Newly installed skills are first to lose their descriptions if Claude Code's skill-listing
> context budget overflows. Run `/doctor` to check the listing's cost; tune
> `skillListingBudgetFraction` / `skillOverrides` in settings if it's too tight.

## Catalog

- **Spec** the flow → `spec-phase-orchestration`
- **Bootstrap** the project → `apple-platform-targets`
- **Build** the UI → `swiftui-navigation-architecture`
- **Test** it → `swift-testing-baseline`
- **Ship** it → `asc-api-automation`
- **Operate** it → `apple-three-piece-analytics`

Full index in the tables below.

### apple-dev-skills (26) — Apple/Swift

| Skill | One-liner |
|---|---|
| `swift6-concurrency` | Swift 6 language mode + complete concurrency checking; `MainActor` by default, Sendable only where code crosses into `nonisolated`/actor context |
| `apple-platform-targets` | Default iOS 26 / macOS 26, Xcode 26.x; drop to 18 / 15 only when an older user base requires it |
| `swiftpm-modularization` | Single Package, multi-target, thin App, DI composition root, one-to-one tests |
| `swift-testing-baseline` | swift-testing + pointfreeco snapshot; protocol fakes; strict/tolerant snapshot gate |
| `xcode-cloud-single-track-ci` | Single-track Xcode Cloud; PR / Main / Release / Periodic; pre-merge PR CI |
| `local-archive-export-upload` | Local `xcodebuild archive` → export → `altool` upload to TestFlight when Xcode Cloud can't run |
| `mise-tool-management` | Pin CLI tool versions (swiftlint, xcbeautify…) with mise, so local dev and CI use the exact same ones |
| `oslog-logger-defaults` | Default logging setup: Apple's own `os.Logger`, no third-party library, log values private unless you opt in |
| `apple-three-piece-analytics` | App Store Connect (ASC) Analytics + MetricKit + Game Center; no third-party tracking; PrivacyInfo mandatory |
| `telemetry-facade-pattern` | One `observe(event)` call fanned out to OSLog / tracking / Game Center sinks, with MetricKit payloads fed in as events — swap sinks without touching call sites |
| `ai-translated-localization` | Default 7 locales; AI translation flow; `Localizable.xcstrings`; completeness gates |
| `ios-accessibility-engineering` | VoiceOver / Dynamic Type / touch-target / Reduce Motion for SwiftUI & UIKit; WCAG 2.2 |
| `swift-dependency-injection` | Make services swappable for tests — protocol injection + a composition root (environment vs constructor, `@TaskLocal`, Sendable) |
| `ios-performance-engineering` | Instruments / xctrace / hang-hitch budgets / launch / memory / binary size / MetricKit |
| `apple-public-repo-security` | Three lines of defence for public iOS/macOS repos + rotate-first leak SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main` for ship-in-binary-but-out-of-diff IDs |
| `storekit2-iap-defaults` | StoreKit 2 non-consumable IAP defaults; bridge-protocol test seam, entitlements, restore |
| `monetization-sdk-integration` | Add/upgrade/audit a monetization SDK; isolate `import` to one bridge file |
| `app-store-review-rejections` | Diagnose & pre-empt App Review rejection classes for free + ads + IAP + CloudKit + Game Center (GC) |
| `asc-api-automation` | ES256 JWT from the `.p8` + curl against the ASC REST API — TestFlight, metadata, submission, reports; no fastlane |
| `swiftui-interaction-footguns` | Known SwiftUI interaction bugs that slip past pure-code review |
| `swiftui-navigation-architecture` | Typed-route navigation for SwiftUI — one `@Observable` router, `NavigationStack`, deep links, macOS fallbacks handled |
| `ios-design-mockup` | Single-file HTML iOS design mockup from a spec — iPhone frames + tokens |
| `interactive-simulator-ux-audit` | Drive a booted Simulator with `idb` (tap/describe/screenshot) to catch nav/modal/safe-area bugs snapshots can't |
| `host-driven-xcuitest-e2e` | Launch-the-app XCUITest E2E via Tuist — dedicated scheme wiring + macOS window-frame click driving |
| `cloudkit-schema-source-of-truth` | Committed `.ckdb` + `cktool` export/validate/deploy to Development; Production is a user-owned Console-only gate |

### collaboration-skills (12) — harness engineering: dispatch, review, ship

| Skill | One-liner |
|---|---|
| `spec-phase-orchestration` | Pre-implementation doc pipeline; section-by-section approval |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer triad; round-1 cosmetic inline; limit(N) |
| `leader-developer-handoff-contract` | 6 required elements when dispatching a sub-agent |
| `agent-impl-notes-log` | Running impl-notes during a sub-agent task — decisions, deviations, open questions |
| `subagent-conflict-detection` | Check a new sub-agent's targets don't overlap an in-flight worktree |
| `methodology-pattern-extractor` | Extract patterns recurring ≥3 times from meeting logs |
| `session-to-meeting-log` | Consolidate a Claude Code session into a meeting log; summary, not verbatim |
| `pr-diff-verification` | Before push/PR, verify `git show --stat --summary HEAD` matches the commit's claims |
| `backlog-routing-by-topic` | Route stray ideas by topic to the matching spec file's §Backlog |
| `claude-skill-plugin-packaging` | Distribute/install Claude Code skills — depth-1 rule, plugin + marketplace, aggregation |
| `skill-authoring-patterns` | Apple/Swift catalog layer over `superpowers:writing-skills` — router descriptions, bookend sections, two-tier references, evidence-based CR |
| `github-contribution-workflow` | gh-CLI contribution loop — PRs, issues, GitHub file ops, secrets, contribution-flow repo settings; conventions + CLEAN-before-merge |

### Aggregated external (7) — by reference, credited

Listed here but **not authored here**: each installs from its author's own repo (you get
their latest) and is credited in full. **Aggregate, don't appropriate** — only MIT-compatible,
non-duplicate plugins are listed, and only for genuine gaps. That check happens once, at
listing time, not on every upstream commit, so an external's scope and licence can drift
afterwards (`caveman` already has). Externals are broad **reference** — "here's the API,
here's how to build X." First-party skills are narrower: one opinionated default per topic
(iOS 26 as the floor, one Package, swift-testing + snapshot, OSLog only, known runtime bugs
to avoid). Where a topic overlaps, the two aren't duplicates — they answer at a different
level of detail.

| Plugin | Author | Covers |
|---|---|---|
| [`apple-skills`](https://github.com/Prisma-Labs-Dev/apple-skills) | Prisma Labs (vabole), MIT | Broad Apple frameworks — SwiftUI, SwiftData, App Intents, WidgetKit, StoreKit, HealthKit …, and a SwiftUI performance audit guide (code-first, view-update causes) that complements `ios-performance-engineering`'s Instruments/MetricKit measurement |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (MIT) | SwiftUI patterns, Swift Charts, Liquid Glass, Instruments toolchain |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (MIT) | SwiftUI pitfalls, deprecated-API watchlist, iOS 26 / Liquid Glass |
| [`caveman`](https://github.com/JuliusBrussee/caveman) | JuliusBrussee (MIT) | Ultra-compressed communication mode — cuts ~75% of tokens (general agent behavior) |
| [`ponytail`](https://github.com/DietrichGebert/ponytail) | DietrichGebert (MIT) | "Lazy senior dev" mode — forces the simplest, shortest solution (general agent behavior) |
| [`i-have-adhd`](https://github.com/ayghri/i-have-adhd) | Ayoub G. (MIT) | Always-on ADHD-friendly output mode — numbered steps, state restated each turn (general agent behavior) |
| [`xcode-build-skill`](https://github.com/pzep1/xcode-build-skill) | pz (MIT) | `xcodebuild`/`xcrun simctl` CLI cheatsheet — schemes → simulators → build → install → launch → screenshot |

`caveman`'s license: skills MIT; repo also ships a BSL-1.1 engine. `caveman` has since grown
into a 20-skill suite; 4 of them (`caveman-discover`, `caveman-manage`,
`caveman-evidence-review`, `caveman-setup`) document the author's hosted Caveman Cloud commercial
service (general agent behavior).

`i-have-adhd` vs `caveman` (token compression) and `ponytail` (solution simplicity), this shapes
structure.

`xcode-build-skill` is CLI-driven, distinct from `interactive-simulator-ux-audit` (idb-driven
interactive UX audit) and `host-driven-xcuitest-e2e` (Tuist-scheme XCUITest E2E) — the three
don't overlap.

`apple-skills` moved from the `vabole` personal account to the `Prisma-Labs-Dev` organization;
this table lists the org's repo.

## Other ways to install

### B — pinned for a team

Pin the marketplace to a released tag directly in `.claude/settings.json` — no submodule needed:

```json
{
  "extraKnownMarketplaces": {
    "apple-dev-skills": {
      "source": { "source": "github", "repo": "wei18/apple-dev-skills", "ref": "v1.7.1" }
    }
  },
  "enabledPlugins": {
    "apple-dev-skills@apple-dev-skills": true,
    "collaboration-skills@apple-dev-skills": true
  }
}
```

Commit it — collaborators get the marketplace automatically once they trust the project
folder, no separate prompt. If Claude Code still reports a plugin as not installed, run the
`/plugin install` command it shows once.

### C — `npx skills` (flat, no plugin)

```bash
npx skills add wei18/apple-dev-skills --list
npx skills add wei18/apple-dev-skills --skill swift6-concurrency
```

> **Path C does not include the aggregated externals.** `npx skills` reads this repo's
> `marketplace.json` / `plugin.json`, but it only follows locally-declared skill paths. It
> does not fetch the externals' remote `github` / `git-subdir` sources. So the commands above
> install only the 38 first-party skills — the 7 externals are silently skipped. To
> flat-install the whole catalog (externals included, pulled from their authors' repos):

```bash
scripts/install-flat.sh -g          # user-level; drop -g for project-level
scripts/install-flat.sh --dry-run   # preview the `npx skills add` commands
```

## Contributing

Three ways to help: **aggregate** an external plugin, **add** a first-party skill, or
**report** a field note — see [CONTRIBUTING.md](CONTRIBUTING.md).

## Provenance

First-party skills were distilled and genericized from [`wei18/Sudoku`](https://github.com/wei18/Sudoku)'s
`.claude/skills/` — a spec-first, AI-Leader/Developer-built portfolio of shipping Apple-platform
games — plus original write-ups of public Apple / WCAG / Swift standards. Aggregated externals
remain their authors' work, surfaced by reference only. The design specs and plans that produced
this repo's two-plugin shape lived under `docs/superpowers/` — retired in favour of git history;
run `git log -- docs/` to find them. MIT — see [LICENSE](LICENSE).
