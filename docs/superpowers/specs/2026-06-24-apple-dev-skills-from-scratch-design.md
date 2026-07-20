# apple-dev-skills — from-scratch redesign (design spec)

Date: 2026-06-24
Status: Implemented — historical archive, superseded by the shipped repo (see
[`README.md`](../../../README.md) Catalog for current counts/versions; this doc
intentionally keeps its as-written numbers, e.g. 10 collaboration skills / 30 total)
Supersedes the doc/structure decisions in `2026-06-24-apple-dev-skills-shared-plugin-design.md`
for the repo layout, doc set, and zh-Hant handling. Skill *content* is unchanged.

## Context

`wei18/apple-dev-skills` shipped at v0.5.0 as a single Claude Code plugin (30 first-party
skills) plus a marketplace that aggregates three external plugins by reference. This
redesign rethinks the repo from its core value rather than patching it:

- The catalog actually contains **two different kinds** of skill — Apple/Swift
  engineering, and generic AI-agent collaboration/process/memory. Agents need both,
  but they are distinct concerns and should be installable separately.
- The meta/process docs (`ROADMAP.md`, `CURATION.md`, the v0.4→v0.5 course-correction
  narrative) are development archaeology with no value to a consumer of the artifact.
- `README.zh-Hant.md` is a hand-maintained full mirror — a standing drift risk.

This is a **clean-slate design** (the user's "丙": treat history as a non-constraint).
No physical memory stores or meeting logs are deleted; the Sudoku-spec project memory
is out of scope and untouched.

## Goals (user-authored)

0. These are skills **built and collected from the author's own experience**.
1. **Installation**, three paths:
   1. Claude marketplace (add + install / public listing).
   2. Consumable as **repo-level skills** by other repos (vendored submodule + committed
      project-scope marketplace settings).
   3. `npx skills`.
2. **README.md is the single source of truth (SSOT).**
3. Beyond the author's own skills, **aggregate other useful, non-duplicate, high-star
   skills by reference** at this repo's marketplace level.
4. Whenever `README.md` changes, a **mise / lefthook pre-commit** step (re)builds
   `README.zh-Hant.md`.

## Non-goals / out of scope

- No `ROADMAP.md`, no `CURATION.md`, no course-correction narrative. The one durable
  principle ("aggregate, don't appropriate") survives as one or two sentences in README.
- **Do not rename** the repo/marketplace (`apple-dev-skills` stays) — renaming breaks
  install URLs and the Sudoku submodule pin.
- Do not delete or alter any memory store / meeting log (clean-slate is a design
  principle only).
- No change to the *content* of any individual `SKILL.md`; this is a re-layout +
  tooling + doc redesign.

## 1. Architecture — one marketplace, two first-party plugins, by-ref externals

```
wei18/apple-dev-skills/                  # marketplace repo (root)
├── .claude-plugin/
│   └── marketplace.json                 # lists both first-party plugins + 3 externals
├── apple-dev-skills/                    # first-party plugin 1 — Apple/Swift (20)
│   ├── .claude-plugin/plugin.json
│   └── skills/<skill>/SKILL.md
├── collaboration-skills/                # first-party plugin 2 — agent process/memory (10)
│   ├── .claude-plugin/plugin.json
│   └── skills/<skill>/SKILL.md
├── README.md                            # SSOT (goal 2)
├── README.zh-Hant.md                    # generated at pre-commit (goal 4)
├── .mise.toml                           # repo-root tooling + tasks
├── lefthook.yml                         # repo-root pre-commit hooks
├── scripts/
│   ├── check-consistency.py             # SSOT gate (extended for two plugins)
│   └── gen-readme-zh.sh                 # zh-Hant generator (C-hybrid)
├── .github/
│   ├── workflows/consistency.yml
│   └── ISSUE_TEMPLATE/aggregate-a-plugin.yml
├── CONTRIBUTING.md
├── LICENSE                              # standalone; README carries no License section
└── .gitignore
```

`marketplace.json` `plugins[]`:

| name | source |
|---|---|
| `apple-dev-skills` | `./apple-dev-skills` (relative subdir) |
| `collaboration-skills` | `./collaboration-skills` (relative subdir) |
| `apple-skills` | `{source: github, repo: vabole/apple-skills}` |
| `swiftui-expert` | `{source: github, repo: AvdLee/SwiftUI-Agent-Skill}` |
| `swiftui-pro` | `{source: git-subdir, url: …/twostraws/SwiftUI-Agent-Skill, path: swiftui-pro}` |
| `caveman` | `{source: github, repo: JuliusBrussee/caveman}` (general agent-behavior, MIT) |
| `ponytail` | `{source: github, repo: DietrichGebert/ponytail}` (general agent-behavior, MIT) |

Install ids: `apple-dev-skills@apple-dev-skills`, `collaboration-skills@apple-dev-skills`,
`<external>@apple-dev-skills`. The `apple-dev-skills@apple-dev-skills` id is unchanged,
so existing consumers keep resolving (see Migration for the skill-count caveat).

## 2. Skill classification (30 → 20 / 10)

**`apple-dev-skills` (20 — Apple/Swift specific):**
swift6-concurrency, apple-platform-targets, swiftpm-modularization, swift-testing-baseline,
xcode-cloud-single-track-ci, mise-tool-management, oslog-logger-defaults,
apple-three-piece-analytics, telemetry-facade-pattern, ai-translated-localization,
ios-accessibility-engineering, swift-dependency-injection, ios-performance-engineering,
apple-public-repo-security, build-time-secret-injection, monetization-sdk-integration,
app-store-review-rejections, swiftui-interaction-footguns, app-icon-rasterize,
ios-design-mockup.

**`collaboration-skills` (10 — generic agent process/memory):**
spec-phase-orchestration, subagent-review-cycles, leader-developer-handoff-contract,
agent-impl-notes-log, subagent-conflict-detection, methodology-pattern-extractor,
session-to-meeting-log, pr-diff-verification, backlog-routing-by-topic,
claude-skill-plugin-packaging.

Decisions: `mise-tool-management` stays in apple-dev (content is entirely Apple toolchain);
`claude-skill-plugin-packaging` goes to collaboration (Claude Code meta-process, neither
Apple nor a single app concern).

## 3. README as SSOT (goal 2)

Lean structure — value + usage only:

```
# apple-dev-skills   — one-liner + goal 0 (distilled & collected from the author's experience)
§ Install      A. marketplace   B. repo-level (submodule + committed settings)   C. npx skills
§ Catalog      apple-dev-skills (20) · collaboration-skills (10) · aggregated external (5, by-ref · credited)
               └ includes the "non-duplicate, aggregate-don't-appropriate" principle in 1–2 sentences
§ Provenance   author's experience + wei18/Sudoku
```

Removed vs current: the Roadmap table, the dedicated "Aggregated external skills"
section (folded into Catalog), and the License section (`LICENSE` file stands alone).
The aggregated externals are presented as just another group in the unified Catalog —
conceptually "mounted under the catalog" — while the mechanism remains by-reference
(goal 3), never vendored or copied.

## 4. zh-Hant generation — C (hybrid), goal 4

Flow: `README.md` staged → lefthook `pre-commit` → `mise run readme-zh` → regenerates
`README.zh-Hant.md` → `git add` into the same commit. English README is the source;
zh-Hant is a derived artifact (an application of the `ai-translated-localization` skill).

`scripts/gen-readme-zh.sh` (hybrid):

```sh
if command -v claude >/dev/null; then
    claude -p "Translate README.md to Traditional Chinese. Preserve structure, code
               fences, links, and skill identifiers (kebab-case names) verbatim; translate
               only prose and one-liners. Output only the translated markdown." \
        < README.md > README.zh-Hant.md
    printf '\n<!-- src-sha: %s -->\n' "$(git hash-object README.md)" >> README.zh-Hant.md
    git add README.zh-Hant.md
else
    embedded=$(grep -oE 'src-sha: [0-9a-f]+' README.zh-Hant.md | awk '{print $2}')
    [ "$embedded" = "$(git hash-object README.md)" ] || {
        echo "README.zh-Hant.md is stale; run 'mise run readme-zh' where claude is available" >&2
        exit 1
    }
fi
```

The embedded `<!-- src-sha: … -->` (the git blob hash of `README.md`) lets both the hook
and the consistency gate detect "zh-Hant fell behind README". `git hash-object` is
deterministic across machines, so the freshness check is reliable offline / in CI.

## 5. Tooling

**`.mise.toml`** (repo root):
- `[tools]` — `lefthook` (via aqua). `claude` is expected on PATH but not mise-managed.
- `[tasks.check]` — `python3 scripts/check-consistency.py`.
- `[tasks.readme-zh]` — `scripts/gen-readme-zh.sh`.

**`lefthook.yml`** (repo root) `pre-commit`:
- `check` → `mise run check` (goal 2 SSOT enforcement).
- `readme-zh` (`glob: README.md`) → `mise run readme-zh` (goal 4).
- Scope is exactly these two; the repo holds no secrets, so no gitleaks.

**mise is the single entry point.** Every script is invoked as a mise task — contributors,
lefthook, and CI all call `mise run <task>`, never `python3 …`/`sh …` directly. This keeps
one tool-versioned, discoverable surface (`mise tasks` lists them) and means the hook and
CI cannot drift from what a contributor runs locally.

**`CONTRIBUTING.md` documents the task surface** (no separate `docs/setup.md` — the repo
stays lean):
- First clone: `mise install && lefthook install`.
- `mise run check` — the SSOT consistency gate (run before every PR).
- `mise run readme-zh` — regenerate `README.zh-Hant.md` from `README.md` (needs `claude`
  on PATH; auto-fires in pre-commit when `README.md` changes).

## 6. Consistency gate (`scripts/check-consistency.py`, extended)

Checks, failing CI/pre-commit on any mismatch (as-built; grown past the checks
originally scoped here — see `scripts/check-consistency.py`'s own docstring for
the current source of truth):

1. Both `apple-dev-skills/skills/<dir>/` and `collaboration-skills/skills/<dir>/` have a
   `SKILL.md` whose frontmatter `name:` == `<dir>`.
2. The README Catalog contains every first-party skill across both plugins **plus**
   the five aggregated external plugin names — missing-direction only; extra kebab-case
   tokens in Catalog prose are tolerated by design.
3. Hardcoded counts (README group headers `(22)`/`(12)`/`(5)`, the Install one-liner
   comments, each `plugin.json` description's "N first-party") == actual.
4. `README.zh-Hant.md` exists and its embedded `src-sha` matches `git hash-object
   README.md` (freshness).
5. Both `plugin.json` and `marketplace.json` parse as JSON; the two subdir plugin sources
   resolve to existing directories; marketplace.json lists exactly the 7 plugins (2 local
   + 5 externals).
6. The `git checkout v<semver>` pin in both READMEs' Install section ==
   marketplace.json `metadata.version`.
7. Each `SKILL.md` frontmatter `description` <= `DESC_MAX` chars.
8. Each plugin's `.claude-plugin/plugin.json` `"version"` == the corresponding
   `marketplace.json` `plugins[]` entry `"version"` (the pair `bump-version.py` maintains).

`.github/workflows/consistency.yml` runs `mise run check` on push/PR.

## 7. Migration (current → target)

1. `git mv` the 20 Apple/Swift skill dirs from `skills/` to `apple-dev-skills/skills/`.
2. `git mv` the 10 collaboration skill dirs from `skills/` to `collaboration-skills/skills/`;
   remove the now-empty root `skills/`.
3. Move the root `.claude-plugin/plugin.json` into `apple-dev-skills/.claude-plugin/`;
   author a new `collaboration-skills/.claude-plugin/plugin.json`.
4. Rewrite root `.claude-plugin/marketplace.json`: change the first-party plugin source
   from `./` to `./apple-dev-skills`, add the `collaboration-skills` entry, keep the three
   externals as-is.
5. Delete `ROADMAP.md` and `CURATION.md`; rewrite `README.md` to the §3 structure; update
   `CONTRIBUTING.md` to drop `CURATION.md` links (criteria already live there) **and document
   the mise task surface** (`mise run check` / `mise run readme-zh`, plus the
   `mise install && lefthook install` setup); update the issue template's `CURATION.md` link.
6. Add `.mise.toml`, `lefthook.yml`, `scripts/gen-readme-zh.sh`; extend
   `scripts/check-consistency.py` for two trees + the catalog/zh-Hant checks.
7. Generate the first `README.zh-Hant.md` via `mise run readme-zh`.

**Backward-compat caveat → coordinated Sudoku PR (deliverable).** `apple-dev-skills@apple-dev-skills`
now exposes 20 skills, not 30. `wei18/Sudoku` relies on the 10 collaboration skills, so the
work includes a **paired PR in the Sudoku repo** that:
- bumps the `.claude/skills/apple-dev-skills` submodule pin to the restructured tag, and
- adds `"collaboration-skills@apple-dev-skills": true` to `.claude/settings.json`
  `enabledPlugins` (alongside the existing `apple-dev-skills@apple-dev-skills`).

Sequencing: this Sudoku PR lands **after** the apple-dev-skills restructure is committed and
tagged (it points at a tag that does not yet exist). The implementation plan treats it as the
final phase. Also note the consequence in the README install section so other consumers know
to enable both plugins.

## 8. Success criteria

- `mise run check` passes on the restructured repo; the gate fails on injected drift
  (missing skill, stale zh-Hant, wrong count).
- Both first-party plugins install and load their skills:
  `claude plugin install apple-dev-skills@apple-dev-skills` (20) and
  `collaboration-skills@apple-dev-skills` (10); the five externals install — `apple-skills` /
  `swiftui-expert` / `swiftui-pro` verified end-to-end this session, `caveman` / `ponytail`
  structurally verified (MIT, root `.claude-plugin/plugin.json`).
- Editing `README.md` and committing regenerates `README.zh-Hant.md` with a matching
  `src-sha` (or, with no `claude`, the commit is blocked with the regen instruction).
- `ROADMAP.md` / `CURATION.md` are gone; README carries no License or Roadmap section.

## 9. Open items

- None blocking. The `claude -p` translation prompt may need one tuning pass on the first
  real run to lock register/length for the zh-Hant one-liners (per `ai-translated-localization`).
