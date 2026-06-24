# apple-dev-skills

> A **curated catalog of Swift / Apple-platform skills for AI coding agents** ([Claude Code](https://code.claude.com)).
> It ships **original first-party skills** for one project's hard-won patterns and for
> public-standard topics, **plus aggregated best-of-breed external skill plugins
> referenced from their original repos and credited to their authors** — not copied.
>
> 繁體中文版：[`README.zh-Hant.md`](README.zh-Hant.md)

The repo is two things at once:

- A **Claude Code plugin** (`apple-dev-skills`) — 30 first-party `SKILL.md` files under
  `skills/`, namespaced `apple-dev-skills:<skill>`. These were distilled from a real
  shipping project's own experience and from public Apple / WCAG / Swift documentation.
- A **marketplace catalog** that also lists best-of-breed **external** skill plugins.
  Those install from **their authors' repos** (full attribution); nothing here is a
  copy or re-implementation of someone else's skill.

**This README is the single source of truth (SSOT) for the library.**

---

## Roadmap (agenda)

| Phase | What | Status |
|---|---|---|
| **1 — Extract** | Pull one project's portable skills out, genericize, ship as a submodule-consumable plugin | ✅ done |
| **2 — Standalone library** | README as SSOT · an `npx skills add` install path · a marketplace catalog that can aggregate other repos (mechanism in [`claude-skill-plugin-packaging`](skills/claude-skill-plugin-packaging/SKILL.md)) | ✅ done |
| **3 — Curate & aggregate** | Surveyed high-star Swift/Apple skill repos and **aggregated** the best-of-breed MIT plugins **by reference** (credited to their authors — see below), rather than re-implementing them. First-party skills were written **only** for genuine gaps with no aggregatable plugin (accessibility, dependency injection, performance). Decisions: [CURATION.md](CURATION.md) | ✅ done |

Detailed status, spec→impl alignment, and future phases: **[ROADMAP.md](ROADMAP.md)**.

---

## Install

> Claude Code discovers shared skills through the **plugin** system, not by a bare
> folder under `.claude/skills/`. This repo is both a plugin and a marketplace.

### Option A — marketplace (simplest)

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills
```

Our skills load as `apple-dev-skills:<skill-name>`. The same marketplace also offers
the [aggregated external plugins](#aggregated-external-skills) — install any of them
from their authors' repos, e.g. `/plugin install swiftui-expert@apple-dev-skills`.

### Option B — vendored submodule, pinned per repo

Vendor the first-party plugin into one repo and pin its version, then register it as a
**local-path marketplace at project scope** so it loads from the pinned submodule:

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v0.5.0 && cd -
```

Then commit this to the repo's `.claude/settings.json` (collaborators are prompted
to trust the workspace, after which it auto-registers):

```json
{
  "extraKnownMarketplaces": {
    "apple-dev-skills": {
      "source": { "source": "directory", "path": "./.claude/skills/apple-dev-skills" }
    }
  },
  "enabledPlugins": { "apple-dev-skills@apple-dev-skills": true }
}
```

A bare `git submodule add` **alone will not surface the skills** — the marketplace
registration above is what makes Claude Code load them.

### Option C — `npx skills` (flat skills, no plugin)

Copy chosen first-party `SKILL.md` files into your agent's skills directory with the
open [`skills`](https://github.com/vercel-labs/skills) CLI, **flat and un-namespaced**:

```bash
npx skills add wei18/apple-dev-skills --list                       # browse the full index
npx skills add wei18/apple-dev-skills --skill swift6-concurrency   # one skill
npx skills add wei18/apple-dev-skills --all -a claude-code         # everything
```

---

## First-party skill index (30)

### Platform defaults (10)

| Skill | One-liner |
|---|---|
| `swift6-concurrency` | Swift 6 language mode + complete concurrency checking; Sendable by default; `@preconcurrency` escape hatch |
| `apple-platform-targets` | Default iOS 18 / macOS 15, Xcode 16+; bump to 26 only for Liquid Glass / latest-OS-only APIs |
| `swiftpm-modularization` | Single Package, multiple targets, thin App, DI composition root, restricted framework imports, one-to-one test targets |
| `swift-testing-baseline` | swift-testing (no XCTest) + pointfreeco snapshot; protocol fakes; snapshots in git; strict-content/tolerant-board gate; CI Xcode locked |
| `xcode-cloud-single-track-ci` | Single-track Xcode Cloud; 4 workflows (PR / Main / Release / Periodic); PR CI with pre-merge |
| `mise-tool-management` | mise manages binary CLI tools; dev + CI share `.mise.toml`; macOS-only-tool `os` guard for mixed-OS CI |
| `oslog-logger-defaults` | `os.Logger` (no third-party); subsystem = bundle ID, category = module; `.private` default |
| `apple-three-piece-analytics` | ASC Analytics + MetricKit + Game Center; no third-party tracking; `PrivacyInfo.xcprivacy` mandatory |
| `telemetry-facade-pattern` | A single `Telemetry` target, fan-out facade; OSLog / NoOp / MetricKit / GameCenter sinks; sink-wiring traps |
| `ai-translated-localization` | Default 7 locales; AI translation flow; `Localizable.xcstrings`; per-key completeness + shared-key gate blind spots |

### Process & collaboration (7)

| Skill | One-liner |
|---|---|
| `spec-phase-orchestration` | The pre-implementation doc pipeline (README + design / foundations / plan / methodology + meetings); section-by-section approval |
| `subagent-review-cycles` | Leader / Developer / Code-Reviewer triad; round-1 cosmetic inline; limit(N) rounds |
| `leader-developer-handoff-contract` | 5 required elements when dispatching a sub-agent: scope / inputs / skills / return format / verification |
| `agent-impl-notes-log` | Running `meetings/{date}_{topic}.impl-notes.md` during a sub-agent task — decisions, deviations, open questions |
| `subagent-conflict-detection` | Before dispatch, check the new sub-agent's target files don't overlap an in-flight sub-agent's worktree |
| `methodology-pattern-extractor` | Extract patterns recurring ≥ 3 times from meeting logs; append to `methodology.md` |
| `session-to-meeting-log` | Consolidate a Claude Code session into `meetings/{date}_{topic}.md`; summary, not verbatim |

### Ops & review (10)

| Skill | One-liner |
|---|---|
| `pr-diff-verification` | Before push / PR, verify `git show --stat HEAD` matches what the commit message claims |
| `backlog-routing-by-topic` | Route stray ideas by topic to the matching spec file's §Backlog |
| `apple-public-repo-security` | Three lines of defence for public iOS / macOS repos (lefthook + gitleaks / CI post-clone / secret scanning) + rotate-first leak SOP |
| `build-time-secret-injection` | xcconfig + Info.plist `$()` + `Bundle.main` for ship-in-binary-but-out-of-PR-diff IDs |
| `monetization-sdk-integration` | Add / upgrade / audit a third-party monetization SDK; isolate `import GoogleMobileAds` to one bridge file |
| `app-store-review-rejections` | Diagnose App Review rejections and harden submissions against the guideline classes a free app with ads + IAP + CloudKit + Game Center hits |
| `swiftui-interaction-footguns` | Checklist of known SwiftUI interaction bugs that slip past pure-code review (tap-target, safe-area, sizeClass, `.task` re-fire) |
| `app-icon-rasterize` | Rasterize a 1024 SVG app icon to the asset-catalog PNG via `qlmanage` — no Homebrew / cloud dependency |
| `ios-design-mockup` | Single-file HTML iOS design mockup from a spec — iPhone frames + SVG nav arrows + design-token panel |
| `claude-skill-plugin-packaging` | How to distribute/install skills — the depth-1 discovery rule, plugin + marketplace packaging, vendored-submodule + committed project-scope settings recipe, aggregating other skill repos by reference, and the gotchas |

### App engineering (3)

These cover topics no compatibly-licensed external Claude Code plugin packages; the
content is original, distilled from public Apple HIG / WCAG / Swift documentation.

| Skill | One-liner |
|---|---|
| `ios-accessibility-engineering` | Concrete VoiceOver / Dynamic Type / touch-target / Reduce Motion implementation + audit for SwiftUI & UIKit, with WCAG 2.2 mapping for App Review |
| `swift-dependency-injection` | Testable seams via protocol injection + a single composition root, SwiftUI environment vs constructor injection, `@TaskLocal` overrides, Swift 6 `Sendable` dependency rules |
| `ios-performance-engineering` | Measure & fix performance — Instruments (Time Profiler / Hangs / SwiftUI), `xctrace` in CI, hang/hitch budgets, launch time, memory & leaks, binary size, MetricKit field telemetry |

---

## Aggregated external skills

These are **not authored here**. They are excellent community skill plugins that this
marketplace lists **by reference** — they install from their authors' own repos, which
keeps full credit with the authors and means you always get their latest. Add this
marketplace (Option A) and install any of them as `<plugin>@apple-dev-skills`.

| Plugin | Author | License | Covers |
|---|---|---|---|
| [`apple-skills`](https://github.com/vabole/apple-skills) | vabole | MIT | Broad Apple frameworks — SwiftUI, Swift Testing, Concurrency, SwiftData, App Intents, WidgetKit, StoreKit, HealthKit, MapKit, TipKit … |
| [`swiftui-expert`](https://github.com/AvdLee/SwiftUI-Agent-Skill) | Antoine van der Lee (AvdLee) | MIT | SwiftUI patterns, Swift Charts, macOS multi-window, Liquid Glass, an Instruments-trace toolchain |
| [`swiftui-pro`](https://github.com/twostraws/SwiftUI-Agent-Skill) | Paul Hudson (twostraws) | MIT | SwiftUI pitfalls LLMs make, deprecated-API watchlist, accessibility, iOS 26 / Liquid Glass |

If you maintain a high-quality, compatibly-licensed Swift/Apple skill plugin and want
it aggregated here, open an issue.

---

## Provenance & credit

The first-party skills were extracted and genericized from
[`wei18/Sudoku`](https://github.com/wei18/Sudoku)'s `.claude/skills/` — a spec-first,
AI-Leader/Developer-built portfolio of shipping Apple-platform games — plus original
write-ups of public Apple / WCAG / Swift standards. The aggregated external plugins
above remain the work and property of their respective authors and are surfaced by
reference only.

## License

MIT (first-party content) — see [LICENSE](LICENSE). Aggregated external plugins are
licensed by their own authors (all MIT at time of listing).
