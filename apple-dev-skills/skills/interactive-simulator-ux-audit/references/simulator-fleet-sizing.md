# Simulator Fleet Sizing — Optional `simslim` Step

3. **Only if still constrained and willing to trade away some background services**, a
   persistent per-simulator daemon-disable is available via third-party tooling. Gate on
   `command -v simslim` first — if it's absent, that's fine, stop at step 2, nothing else in
   this skill depends on it. To install without Homebrew: `go install
   github.com/mobai-app/simslim/cmd/simslim@latest` (a Go toolchain can be provisioned
   through `mise`, see `mise-tool-management`); or download the plain release tarball
   directly, `simslim-v0.8.0-macos-arm64.tar.gz` from
   `https://github.com/MobAI-App/simslim/releases/download/v0.8.0/` (asset name/version
   verified via `gh release view MobAI-App/simslim`, 2026-09-03 — simslim's own README
   documents only Homebrew and `go install`, so this direct-tarball
   path isn't in its docs either). Once present, it's one command per simulator: `simslim on
   <udid>` to disable, `simslim off <udid>` to revert.
   - Persistence only survives reboot on iOS 18.5+ runtimes; older runtimes are rejected
     before anything is touched. See `https://github.com/MobAI-App/simslim` for current behavior.
   - Slimming drops Spotlight/in-Settings search, push notifications (`apsd`) and StoreKit
     testing (`storekitd`), and universal links (`swcd`) unless kept via `--except`/`--keep`.
     See `https://github.com/MobAI-App/simslim` for current behavior.
   - `erase`, delete+recreate, and "Erase All Content and Settings" all revert to stock; the
     profile must be reapplied. See `https://github.com/MobAI-App/simslim` for current behavior.
   - This skill doesn't track simslim's CLI beyond the two commands above — its own README
     is the source of truth for anything else.
