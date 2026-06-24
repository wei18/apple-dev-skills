# apple-dev-skills

> Reusable [Claude Code](https://code.claude.com) skills for **AI-agent-driven Swift / Apple-platform development**.
> A Swift engineer-agent's professional skill library — composable, self-describing, and shareable across projects via git submodule.

This repo is a **Claude Code skills-directory plugin**: a curated set of
`SKILL.md` files under `skills/`, surfaced to Claude Code under the
`apple-dev-skills:` namespace. The skills were battle-tested building real shipping
Apple-platform apps and then genericized for reuse.

**This README is the single source of truth (SSOT) / agenda for the library.**

---

## Roadmap (agenda)

| Phase | What | Status |
|---|---|---|
| **1 — Extract** | Pull the portable skills out of a real project, genericize, ship as a submodule-consumable plugin | ✅ done |
| **2 — Standalone library** | (a) this README as SSOT/agenda · (b) an **npm install path** alongside the submodule · (c) ability to **submodule *other* specialist skill repos** so the library aggregates best-of-breed instead of reinventing | ⏳ planned |
| **3 — Curate the ecosystem** | Survey high-star GitHub Swift / Apple-platform skill repos; per candidate decide **adopt** / **replace ours** / **skip**, documented | ⏳ planned |

---

## Install

> Claude Code discovers shared skills through the **plugin** system, not by a bare
> folder under `.claude/skills/`. This repo is both a plugin and a marketplace
> (`.claude-plugin/marketplace.json` + `.claude-plugin/plugin.json`), so either
> path below works.

### Option A — global marketplace (simplest)

In Claude Code:

```
/plugin marketplace add wei18/apple-dev-skills
/plugin install apple-dev-skills@apple-dev-skills
```

Skills load globally (every project) as `apple-dev-skills:<skill-name>`.

### Option B — vendored submodule, pinned per repo

Vendor the library into one repo and pin its version, then register it as a
**local-path marketplace at project scope** so it loads from the pinned submodule:

```bash
git submodule add https://github.com/wei18/apple-dev-skills.git .claude/skills/apple-dev-skills
cd .claude/skills/apple-dev-skills && git checkout v0.2.0 && cd -
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

### Option C — npm

⏳ Phase 2. The npm distribution path is not built yet.

---

## Skill index

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
| `claude-skill-plugin-packaging` | How to distribute/install these skills — the depth-1 discovery rule, plugin + marketplace packaging, vendored-submodule + committed project-scope settings recipe, aggregating other skill repos, and the gotchas |

---

## Provenance

Extracted and genericized from [`wei18/Sudoku`](https://github.com/wei18/Sudoku)'s
`.claude/skills/` — a spec-first, AI-Leader/Developer-built portfolio of shipping
Apple-platform games. Skills that name that repo's specific tasks / apps stayed
behind; everything here is project-agnostic.

## License

MIT — see [LICENSE](LICENSE).
