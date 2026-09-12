---
name: mise-tool-management
description: 'Use when pinning binary CLI / build tools (swiftlint, xcbeautify, gitleaks, lefthook) with mise so dev machines and CI share one `.mise.toml` — choosing mise vs asdf / Homebrew / manual, writing `.mise.toml` (`aqua:` / `ubi:` backends, `os = ["macos"]` guards), running `mise trust` / `mise install` / `mise exec` from `ci_post_clone.sh` or a fresh git worktree, or debugging "mise exec ignores .mise.toml in a new worktree", `unsupported env: linux/amd64`. Does NOT cover Xcode Cloud workflow design → xcode-cloud-single-track-ci, nor gitleaks / lefthook policy → apple-public-repo-security.'
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
- **Dev machine and CI share the same `.mise.toml`**, committed to git. Both `.mise.toml` and `mise.toml` (no leading dot) are valid config filenames — mise's own docs primarily spell it `mise.toml` — but this catalog's convention is the dotfile form.
- Plugin backend priority: core plugin → `aqua:` → `github:`/`gitlab:` (release assets) → `asdf:` (legacy). `ubi:` is deprecated — mise's own release-backend docs mark it "Legacy release installer (deprecated)".
- **Xcode Cloud has no mise preinstalled** — its build environment ships only Homebrew, so a `ci_post_clone.sh` that starts with a bare `mise` command fails with "command not found". Xcode Cloud also runs `ci_post_clone.sh` with `ci_scripts/` as the working directory, so the script must `cd "$CI_PRIMARY_REPOSITORY_PATH"` first or `./bin/mise` won't resolve. Commit a bootstrapped `bin/mise` (`mise generate bootstrap -l -w bin/mise`) and call it explicitly: after `cd "$CI_PRIMARY_REPOSITORY_PATH"`, run `./bin/mise trust && ./bin/mise install`; subsequent tool invocations always go through `./bin/mise exec -- <tool> <args>` (see `xcode-cloud-single-track-ci` for the full hook). On a dev machine or any CI runner that already has mise on `PATH`, drop the `./bin/` prefix: `mise exec -- <tool> <args>`.
- **A freshly cloned repo or a freshly created git worktree starts with `.mise.toml` untrusted** — `mise install` / `mise exec` hard-error with `Config files in <dir> are not trusted. Trust them with 'mise trust'` until `mise trust` has run once in that directory. Every new agent worktree and every CI checkout hits this; run `mise trust` before the first `mise install`/`mise exec` in each.

## Rationale

- A single file (`.mise.toml`) is the single source of truth; version drift is eliminated at the root.
- mise manages multiple languages / tools at once, no need for a separate version manager per tool.
- Stronger than Homebrew: pin to minor / patch versions, not "latest is the version".
- Faster than asdf: written in Rust, with small shell-hook overhead.

## Example `.mise.toml`

```toml
[tools]
swiftlint = "0.65" # pinned 2026-09
xcbeautify = "1"
"aqua:gitleaks/gitleaks" = "8"
"aqua:evilmartians/lefthook" = "1"
# Xcode's own swift toolchain is already on PATH — don't pin it via a
# `swift = "system"` entry: mise deprecated @system tool versions
# ("use MISE_DISABLE_TOOLS instead"; set that env var if you need to
# suppress a swift entry inherited from a parent .mise.toml).
# Xcode is NOT pinned here; the toolchain SSOT is README / foundations.md +
# the Xcode Cloud workflow setting. `aqua:XcodesOrg/xcodes` can install
# Xcode itself, but it's an installer, not a version pin — the actual
# version lock still lives in the Xcode Cloud workflow Environment.
```

## Deviation considerations

- **Team already uses asdf heavily**: keep it for now, but new repos go to mise; mise can read `.tool-versions` as a transition.
- **Tool not in the mise registry / `aqua:` / `github:`/`gitlab:`**: prefer a non-Homebrew path first.

  | Tool available via | Install with | Note |
  |---|---|---|
  | mise registry / `aqua:` / `github:`/`gitlab:` | a normal `.mise.toml` row | Default |
  | Go module only | `go install <module>@latest` | The Go toolchain can itself come from mise |
  | GitHub Releases binary, no mise backend | Download the plain tarball directly for your platform | Same install pattern as `idb` in `interactive-simulator-ux-audit` |
  | Homebrew only | Last resort | If a project policy bans Homebrew, record the exception in *that project's* README |
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
- After local `mise install`, `mise exec -- <tool> --version` matches CI log.
- CI scripts go through `mise exec`, never calling `/usr/local/bin/<tool>` or other preinstalled paths.
- The repo's contributor setup guide starts with 'install mise → `mise trust` → `mise install`'.

## Related skills

- `xcode-cloud-single-track-ci`: `ci_scripts/` activates tools through mise.
- `apple-public-repo-security`: gitleaks + lefthook installed through mise.
