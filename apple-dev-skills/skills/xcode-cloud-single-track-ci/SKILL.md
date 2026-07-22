---
name: xcode-cloud-single-track-ci
description: Default CI strategy for solo / small-team Apple-platform projects — Xcode Cloud single-track only (defer GitHub Actions until real pain appears), 4 workflow types (PR / Main / Release / Periodic), pre-merge main on PR CI, Xcode version locked to local. Invoke when setting up CI on a new project, deciding GitHub Actions vs Xcode Cloud, writing ci_scripts/, or when asked "how should CI be set up, do I need dual-track".
---

# Xcode Cloud Single-Track CI

## When to invoke

- Starting a new Apple-platform project and setting up CI.
- Deciding between GitHub Actions and Xcode Cloud.
- Writing `ci_scripts/ci_post_clone.sh` / `ci_pre_xcodebuild.sh` / `ci_post_xcodebuild.sh`.
- Bumping the Xcode version and handling snapshot baselines.
- User asks "how to split PR / Main / Release workflow", "auto-upload to TestFlight or not".

## Default decisions

### Single-track on Xcode Cloud

- **GitHub Actions is not enabled yet** — wait for real pain (PR metadata rules, external lint jobs, Selective Testing, etc.) to appear.
- The repo is hosted on GitHub, but CI runs on Xcode Cloud.

### 4 workflows

| Workflow | Trigger | Action |
|---|---|---|
| **PR CI** | PR open / push (**enable "Merge with base branch before building"**) | Build + Test (unit / integration with fakes / snapshot) |
| **Main CI** | Merge to `main` | Build + Archive + upload to internal TestFlight; **do not re-run tests** (already verified by PR CI in pre-merged state) |
| **Release** | git tag `v*` | Build + upload to App Store Connect (manual submission for review) |
| **Periodic / Manual** | Scheduled + manual trigger | Project-specific batch jobs (puzzle generation, metadata updates, etc.) |

> **Scheduling granularity caveat**: Xcode Cloud's "On a Schedule" start condition supports **hourly / daily / weekly** granularity only — arbitrary cron expressions are not supported. For monthly-or-longer cadence, schedule weekly and add a script-side date guard inside `ci_post_clone.sh` that early-exits when the date doesn't match the desired condition.

### Environment lock

- Xcode version is locked to match `.mise.toml` on the local machine.
- When bumping Xcode, open a dedicated PR to refresh snapshot baselines.
- Any tool inside `ci_scripts/` is activated via `mise` first, to avoid drift from Xcode Cloud's preinstalled versions.
- Test environment disables iCloud / Game Center sign-in; all tests go through protocol fakes.

### Build number & version automation

- Two build settings, two jobs: `MARKETING_VERSION` (→ `CFBundleShortVersionString`, the SemVer-style version users see) is bumped deliberately per release; `CURRENT_PROJECT_VERSION` (→ `CFBundleVersion`, the build number) increments on every build, including PR builds.
- **Xcode Cloud manages the build number for you** — it assigns a sequential integer per build starting at `1`, independent of whatever `CURRENT_PROJECT_VERSION` says in the repo, and exposes it to `ci_scripts/` as `CI_BUILD_NUMBER`. For a new app this is enough: e.g. `1.2.2 (1)` is a valid, unique version+build pair even after a prior manually-numbered `1.2.1 (42)`.
- **Exception — existing Mac apps**: macOS requires the build number to strictly increase *across* versions too, not just be unique within one, so restarting Xcode Cloud's counter at `1` can collide with a prior higher build number. Fix once, on the ASC side: app → **Xcode Cloud** tab → **Settings** → **Build Number** tab → **Edit** → set the next build number above your last shipped one. This is an App Store Connect setting, not a `ci_scripts/` variable.
- If something in the repo needs `CURRENT_PROJECT_VERSION` itself to reflect Xcode Cloud's build number (e.g. crash-symbolication tooling that reads it from the binary), write it early in `ci_post_clone.sh`: `agvtool new-version -all "$CI_BUILD_NUMBER"` — requires `VERSIONING_SYSTEM = apple-generic` (agvtool enabled) on the target.
- Release tooling that mints `versionString` for the ASC API (→ `asc-api-automation`) should read this project's `MARKETING_VERSION` rather than track a second version counter — one SemVer source of truth.

### Three Xcode Cloud hooks

Apple provides:
- `ci_post_clone.sh` — runs right after clone, before any build resources are spent (**secret scan, `mise install` go here, cheapest stage**)
- `ci_pre_xcodebuild.sh` — before build
- `ci_post_xcodebuild.sh` — after build

## Rationale

- For solo / small teams, CI usage is light and Xcode Cloud's free quota is enough; dual-track adds ops cost with no matching value.
- PR CI with pre-merge fundamentally resolves the common "fails only after merge to main" race.
- Main CI skips re-running tests: PR already ran them in pre-merged state, so rerunning is waste; it archives and ships to TestFlight instead.
- Periodic workflow is built into Xcode Cloud (no separate cron service required).

## Deviation considerations

### When to add GitHub Actions

- PR metadata rules (conventional commits, PR title lint, auto-label / required reviewer)
- SwiftLint / SwiftFormat or other binary tools running on PR
- `docs/` link checks, `meetings/` index auto-updates
- Wiring up Selective Testing
- Using `nektos/act` to reproduce non-build jobs locally

Starting point: when one of the above real pain points appears, **add a single workflow first**, don't go dual-track in one shot.

### Known race condition

When two PRs each pass pre-merge and merge back to back, **their combined result was never tested**.
- Solo projects rarely hit this.
- Multi-person teams who care: enable GitHub's "Require branches to be up to date before merging", or add minimal smoke tests to Main CI.

## Verification checklist

- The Xcode version in the Xcode Cloud workflow matches `.mise.toml`.
- PR CI has "Merge with base branch before building" enabled.
- First line of `ci_post_clone.sh` is `mise install`.
- Periodic workflow trigger time is explicit (UTC recommended).
- Existing Mac apps: Xcode Cloud's next build number (App Store Connect → Xcode Cloud → Settings → Build Number) is set above the last shipped build number.

## Related skills

- `mise-tool-management`: `ci_scripts/` tools installed via mise.
- `swift-testing-baseline`: CI skips real-network integration tests.
- `apple-public-repo-security`: PR CI adds a gitleaks step as the second line of defence.
- `apple-platform-targets`: Xcode version lock.
- `asc-api-automation`: release-side `versionString` and changelog automation, once the build exists in ASC — reuses this project's `MARKETING_VERSION` / `CI_BUILD_NUMBER`.
