---
name: mise-tool-management
description: Use mise (mise.jdx.dev) to manage binary CLI / build tools (swiftlint, swiftformat, xcbeautify, gitleaks, lefthook, etc.) on both dev machines and CI, sharing a single `.mise.toml` for version parity. Invoke when starting a new project, choosing a tool version manager (vs asdf / Homebrew / manual), writing `.mise.toml`, or when asked "how do I manage swiftlint / xcbeautify versions".
---

# mise Tool Management

## When to invoke

- Starting a new project and picking a version manager for binary CLI / build tools.
- Writing the first `.mise.toml`.
- Adding new binary tools (swiftlint, swiftformat, xcbeautify, gitleaks, lefthook, jq, yq, ...).
- Setting up CI (e.g. Xcode Cloud `ci_scripts/`) that needs to call tools.
- User asks "asdf vs mise", "why isn't Homebrew enough", "what about CI / local version drift".

## Default decisions

- **Adopt `mise`** ([mise.jdx.dev](https://mise.jdx.dev/)) to manage binary CLI / build tools.
- **Dev machine and CI share the same `.mise.toml`**, committed to git.
- Plugin backend priority: core plugin → `aqua:` → `ubi:` → `asdf:`.
- CI (Xcode Cloud `ci_post_clone.sh`) first line: `mise install`; subsequent tool invocations always go through `mise exec <tool> -- <args>`.

## Rationale

- A single file (`.mise.toml`) is the single source of truth; version drift is eliminated at the root.
- mise manages multiple languages / tools at once, no need for a separate version manager per tool.
- Stronger than Homebrew: pin to minor / patch versions, not "latest is the version".
- Faster than asdf: written in Rust, with small shell-hook overhead.

## Example `.mise.toml`

```toml
[tools]
swift = "system"
swiftlint = "0.54"
xcbeautify = "1"
"aqua:gitleaks/gitleaks" = "8"
"aqua:evilmartians/lefthook" = "1"
# Xcode version can also be managed via a mise plugin if you need to lock it
```

## Deviation considerations

- **Team already uses asdf heavily**: keep it for now, but new repos go to mise; mise can read `.tool-versions` as a transition.
- **Tool not in mise registry / aqua / ubi**: install via Homebrew / SwiftPM build manually and note the exception in the README.
- **CI runner already has the target version preinstalled**: still run `mise install` to enforce parity; the extra overhead is small.
- **macOS-only tools on a mixed-OS CI fleet** (Xcode-project generators, macOS
  artifact bundlers — e.g. `tuist`, `LicensePlist`): guard them with an `os`
  field, `"aqua:tuist/tuist" = { version = "4", os = ["macos"] }`. A Linux CI job
  (L10n / lint / markdown gates run fine on Ubuntu) runs `mise install` which
  installs **every** tool; an unguarded macOS-only tool fails at setup
  (`unsupported env: linux/amd64`) **before any gate runs**, blocking *all* PRs.
  This can appear suddenly with no change of yours — an upstream registry can flip
  a tool to darwin-only mid-day, so earlier PRs pass and later identical ones fail
  at "install pinned tools". When CI dies at the mise-install step, read for
  `unsupported env: linux/amd64` and add the `os` guard.

## Verification checklist

- `.mise.toml` lives at the repo root, committed to git.
- After local `mise install`, `mise exec <tool> -- --version` matches CI log.
- CI scripts go through `mise exec`, never calling `/usr/local/bin/<tool>` or other preinstalled paths.
- New-contributor setup guide (`docs/setup.md`) starts with "install mise → `mise install`".

## Related skills

- `xcode-cloud-single-track-ci`: `ci_scripts/` activates tools through mise.
- `apple-public-repo-security`: gitleaks + lefthook installed through mise.
