Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Configuring start conditions | https://developer.apple.com/documentation/xcode/configuring-start-conditions | PR: "merges both branches in a temporary environment"; schedule: "specify the frequency, time, and branch" |
| Writing custom build scripts | https://developer.apple.com/documentation/xcode/writing-custom-build-scripts | Three hooks; `ci_scripts` as root directory |
| Making dependencies available to Xcode Cloud | https://developer.apple.com/documentation/xcode/making-dependencies-available-to-xcode-cloud | Environment ships Homebrew |
| Environment variable reference | https://developer.apple.com/documentation/xcode/environment-variable-reference | `CI_PRIMARY_REPOSITORY_PATH`, `CI_BUILD_NUMBER` |
| Setting the next build number for Xcode Cloud builds | https://developer.apple.com/documentation/xcode/setting-the-next-build-number-for-xcode-cloud-builds | `1.2.2 (1)` is legal on iOS, not on Mac; Mac apps have a different starting value |
| Build settings reference -- VERSIONING_SYSTEM | https://developer.apple.com/documentation/xcode/build-settings-reference#Versioning-System | "Apple Generic: Use the current project version setting" `[apple-generic]` -> the agvtool prerequisite |
| Xcode Cloud Overview | https://developer.apple.com/xcode-cloud/ | "25 compute hours/month Included with Apple Developer Program membership" |
| About protected branches | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches | "Require branches to be up to date before merging" |
