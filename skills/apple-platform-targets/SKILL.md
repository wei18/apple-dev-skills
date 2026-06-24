---
name: apple-platform-targets
description: Default minimum deployment targets for Apple-platform Swift Apps and how to deviate up or down. Default is iOS 18 / macOS 15 with Xcode 16+ (first toolchain to formally support Swift 6 language mode). Invoke when starting a new Apple-platform project, writing Package.swift `platforms:` list, deciding whether to adopt Liquid Glass / latest-OS-only APIs, or when asked "what should the minimum iOS / macOS version be?".
---

# Apple Platform Deployment Targets

## When to invoke

- Starting a new iOS / macOS App and setting the minimum deployment version.
- Writing the `platforms:` block in `Package.swift`.
- Deciding whether to adopt latest-OS-only APIs (Liquid Glass `.glassEffect()`, new Observation, new SwiftData behaviour, etc.).
- User asks about minimum iOS / macOS version or whether to support the previous major version.

## Default decisions

- **iOS 18 / macOS 15** as the default minimum.
- Toolchain: **Xcode 16+** (the first version with formal Swift 6 language mode support).
- Do not auto-bump with each Xcode major — bumping requires an explicit decision recorded in `foundations.md`.
- Keep `Package.swift` `platforms:` **aligned** with the App target deployment target; no skew.

## Rationale

- iOS 18 / macOS 15 aligns with the Swift 6 toolchain, unlocking Observation / SwiftData improvements and async sequence enhancements.
- Locking out auto-bumps prevents blindly chasing each Xcode major and losing users who haven't upgraded.
- For solo / small projects the user base is small, so the compatibility tax is low compared to the stability benefit.

## Deviation considerations

### Bump up to iOS 26 / macOS 26 (or newer)

- **Trigger**: adopting Liquid Glass (`.glassEffect()` is iOS 26+) or other latest-OS-only APIs.
- **Conditions**: the project has no backward-compat baggage (brand new App, no existing user base); or it's a personal / showcase project willing to cut off older versions.
- **Cost**: lose users on older OS; TestFlight beta testers must upgrade.
- **How to record**: explicitly note "deviating from apple-platform-targets default" in `foundations.md` with a reason.

### Drop down to iOS 17- / macOS 14-

- **Trigger**: the App needs a large pool of older-device users (education, enterprise intranet, low-end markets).
- **Cost**: lose full Observation behaviour, SwiftData fixes, parts of Swift 6 mode checking.
- **Advice**: explicitly record which APIs are off-limits and which behaviours need polyfills.

## Verification checklist when locking targets

- `Package.swift` `platforms:` matches every App target's `IPHONEOS_DEPLOYMENT_TARGET` / `MACOSX_DEPLOYMENT_TARGET`.
- Xcode version is locked via `.mise.toml` or the project README.
- CI (e.g. Xcode Cloud) Xcode version matches the local lock.

## Related skills

- `swift6-concurrency`: Xcode 16+ / Swift 6 mode is coupled to this skill's version choice.
- `xcode-cloud-single-track-ci`: CI Xcode version lock.
- `mise-tool-management`: local Xcode-select / toolchain version management.
