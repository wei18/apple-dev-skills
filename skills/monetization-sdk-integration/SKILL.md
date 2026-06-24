---
name: monetization-sdk-integration
description: Invoke when adding, upgrading, or auditing any third-party monetization SDK (AdMob, UMP, StoreKit wrappers, RevenueCat, ironSource, etc.). Also invoke when reviewing PR diffs that touch your monetization target's ad-bridge sources, or when anyone proposes `import GoogleMobileAds` outside the existing live-bridge file.
---

# Monetization SDK Integration

## When to invoke

- Adding a new monetization SDK (AdMob, ATT, UMP, AdMob mediation networks, RevenueCat, etc.)
- Upgrading existing AdMob / UMP versions (e.g. v11 → v13)
- Auditing PR diff that touches your monetization target's ad-bridge sources (e.g. `Sources/<AdsBridge>/`)
- Cross-platform SDK questions (iOS only? macOS catalyst? watchOS?)
- Anyone proposing "let's just `import GoogleMobileAds` over here too" — IMMEDIATE invoke

Skip when: changing pure values / protocols inside your monetization core target (no third-party touch).

## The contract

Default rule: **no third-party SDKs** in the app. Apple-platform native APIs preferred (OSLog over Sentry, MetricKit over Firebase Crashlytics, GameKit over Steam-style backend, etc.).

**Break-glass exception** is granted when ALL of:
1. The capability genuinely requires the SDK (no Apple-native alternative); e.g. AdMob banner serving has no Apple-platform equivalent
2. The SDK is shippable under the project's privacy regime (PrivacyInfo.xcprivacy supports its tracking domains)
3. The SDK's import is isolated to a SINGLE source file behind a protocol seam (see §isolation contract below)
4. The dep arrow is one-way (consumer → SDK; SDK does not call back into our code beyond delegate/callback bridges)
5. iOS-only conditional compile gating (`canImport`) — macOS / Catalyst paths must build without the SDK

If any of (1)-(5) fails: deny. Reject the SDK proposal; suggest Apple-native fallback or sit it out.

## The isolation contract (§9.1)

For every accepted SDK:

### File-layout invariant
- Protocol file `<SdkName>Bridge.swift` defines the seam. Plain Swift; no SDK import.
- Live impl file `Live<SdkName>Bridge.swift` is the ONLY file allowed to `import <SDKModule>`.
- All other code uses `any <SdkName>Bridge` for DI. Test seam: `Fake<SdkName>Bridge` in the matching test target (e.g. `Tests/<AdsBridge>Tests/FakeAdMobBridge.swift`).

Example for AdMob (currently shipped):
- `Sources/<AdsBridge>/AdMobBridge.swift` — protocol (your monetization target's bridge protocol file)
- `Sources/<AdsBridge>/LiveAdMobBridge.swift` — sole `import GoogleMobileAds` site
- `Tests/<AdsBridge>Tests/FakeAdMobBridge.swift` — test seam

### Build-time audit (run before every monetization PR merge)

Canonical regex (matches Swift 6 access-level imports too):
```bash
rg '^(internal |private |public |@_implementationOnly |@preconcurrency )*import <SDKModule>' Sources/
```

Expected count: **1** (live bridge file).

If > 1: the contract is broken. Either consolidate behind the existing bridge OR file an exception in `docs/foundations.md` documenting WHY a second import site is necessary (with prior reviewer sign-off).

Documentation references:
- Your project's `docs/foundations.md` — the contract text itself
- Your project's plan / readiness doc — audit acceptance criteria and pre-submission audit step

### Conditional compile invariant

iOS-only SDKs (AdMob/UMP/most monetization stack):
```swift
#if canImport(GoogleMobileAds)
import GoogleMobileAds
// ... live impl code
#else
// macOS / catalyst fallback — usually NoOp returning sensible empty values
#endif
```

The Package.swift dep arrow itself must also gate the SDK to iOS:
```swift
.product(
    name: "GoogleMobileAds",
    package: "swift-package-manager-google-mobile-ads",
    condition: .when(platforms: [.iOS])
),
```

Without `condition:`, macOS build fails on `swift build` because Google ships iOS-only xcframeworks.

### Test seam invariant

A test target for the bridge ships `Fake<SdkName>Bridge` (actor or class). All unit tests inject the fake; real SDK only loaded at runtime via DI in the app's composition root. A shared testing-scaffolding target may ship shared fakes used across both ad and IAP test targets (e.g. `FakeAdProvider`, `FakeIAPClient`); the per-SDK bridge fakes live in their own test target.

`Fake` must:
- Be `Sendable` (Swift 6 actor or @unchecked Sendable + lock-guarded)
- Have a `script(...)` or per-call setter API for deterministic test outcomes
- Not import the real SDK (zero hidden dependency)

## Real-world incidents this skill encodes

### AdMob v11 → v13 upgrade (from a real project)
- Symbol renames: `GADBannerView` → `BannerView`, `GADRequest` → `Request`, etc.
- Audit broke briefly when migrator missed file boundary; recovered by re-running isolation audit

### Production ID swap safety
- A Release build's `bannerAdUnitID` constant used `fatalError("REPLACE_BEFORE_RELEASE: …")` rather than a placeholder string — prevents accidental Release build silently serving test creatives against production app ID
- A paired-flip checklist ensures Info.plist `GADApplicationIdentifier` + bridge constant are always updated together

### Real banner landed + SDK-view-crossing seam
- The `GADBannerView` SwiftUI host shipped. `import GoogleMobileAds` stays confined to the live bridge file; the live banner crosses into the UI layer via `BannerViewProviding.bannerView(for:) -> AnyView?` — an **`AnyView` (SwiftUI), never a GoogleMobileAds type** — so UI targets import zero SDK. One shared `BannerSlotView` replaced per-app placeholder slots.
- ID split: `#if DEBUG` forces Google's universal test unit; Release reads the per-app prod id from `Bundle.main` via xcconfig.

### macOS conditional gating
- Initial AdMob integration left `import GoogleMobileAds` ungated → macOS build broke
- Fix: `canImport(GoogleMobileAds)` + Package.swift `condition: .when(platforms: [.iOS])` + macOS fallback uses `NoopAdProvider`

### lefthook parallel deadlock — secondary effect
- Multiple SDK installs triggered concurrent `mise exec` invocations
- `lefthook.yml pre-commit.parallel: false` makes hook timing predictable

## Anti-patterns

- **"Just import it where you need it"** — NO. Single-file isolation is the contract; multiple imports = no audit signal, no clean removal path.
- **"Skip the Fake for now, we'll add it later"** — NO. Unit tests must work from day one; integrating SDK without a test seam means every test becomes integration-test territory.
- **"Macros + canImport are too verbose; let's drop conditional gating for v2"** — NO. macOS build will break the moment a maintainer runs `swift build` on a Mac, blocking PRs.
- **"Production IDs in source for ease of swap"** — NO. Use `fatalError` guard or build-config injection; hard-coded prod IDs in DEBUG/Release pivot risk accidental Release ship with wrong combination.
- **"PrivacyInfo.xcprivacy can wait until submission"** — NO. ASC will reject TestFlight + production builds without the manifest matching declared tracking. Update PrivacyInfo BEFORE adding the SDK.

## Pre-integration checklist

When proposing a new SDK, fill this in:

```
SDK: <name + version + GitHub URL>
Capability: <what it does that Apple-native can't>
Privacy domains: <list — must match PrivacyInfo.xcprivacy>
iOS-only / cross-platform: <iOS-only | iOS+macOS | etc.>
Bundle size impact: <KB / MB>
Tracking ATT required: <yes/no>
UMP consent required: <yes/no>
Test seam plan: <how Fake<SdkName>Bridge will look>
Isolation audit grep target count: <expected 1>
Fallback platform behaviour: <Noop / throw / etc.>
```

If any field is "TBD" or "?", do NOT proceed — research first.

## Documentation pointers

- Your project's `docs/foundations.md` — the no-3rd-party rule + break-glass exception + isolation contract text
- Your project's design doc — monetization design intent
- Your project's plan / readiness doc — AdMob impl phase, isolation acceptance criteria, pre-submission audit step
- `Sources/<AdsBridge>/<SdkName>Bridge.swift` — protocol seam example
- `Sources/<AdsBridge>/Live<SdkName>Bridge.swift` — single-import-site example
- `<App>/Resources/PrivacyInfo.xcprivacy` — tracking domains declaration
