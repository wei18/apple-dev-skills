Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| mise generate install-script | https://mise.jdx.dev/cli/generate/install-script.html | `--localize` / `--write`; `generate bootstrap` retires in 2027.9.0 |
| Continuous integration | https://mise.jdx.dev/continuous-integration.html | Bootstrapping: `mise generate install-script -l -w`, commit `bin/mise`, add `.mise/` to `.gitignore` |
| Ubi Backend | https://mise.jdx.dev/dev-tools/backends/ubi.html | "The ubi backend is deprecated. Use the GitHub backend instead." |
| mise trust | https://mise.jdx.dev/cli/trust.html | Normal mode auto-trusts the active config on install/exec; safe configs skip trust; trust is shared across worktrees; paranoid mode is the exception |
| mise v2026.8.9 release notes | https://github.com/jdx/mise/releases/tag/v2026.8.9 | The version boundary for implicit trust (#12107); worktree-shared trust landed in v2026.7.5 (#10890) |
| Dev Tools | https://mise.jdx.dev/dev-tools/ | "OS-Specific Tools": the `os` field |
| mise registry (source) | https://github.com/jdx/mise/tree/main/registry | `swiftlint.toml` / `xcbeautify.toml` carry no `os` restriction; `tuist.toml` is `os = ["macos", "linux"]` |
| aqua registry | https://github.com/aquaproj/aqua-registry/tree/main/pkgs | Per-version `supported_envs`: tuist > 4.139.1 supports linux; the latest xcbeautify only supports linux/amd64 + darwin |
| Making dependencies available to Xcode Cloud | https://developer.apple.com/documentation/xcode/making-dependencies-available-to-xcode-cloud | The environment ships macOS/Xcode's own tools plus Homebrew -- no mise |
| Writing custom build scripts | https://developer.apple.com/documentation/xcode/writing-custom-build-scripts | "runs your custom build scripts with this directory [`ci_scripts`] as the root directory" -> `cd "$CI_PRIMARY_REPOSITORY_PATH"` first |
