---
name: swiftpm-modularization
description: Default modularization shape for Apple-platform Swift Apps — single Swift Package, multi-target, thin App target, DI composition root, restricted Apple framework imports, one test target per production target. Invoke when starting a new project, writing Package.swift, deciding how to split modules, planning portability (e.g. Swift on Android), or when asked "single package or multi-package, how should I split modules".
---

# SwiftPM Modularization

## When to invoke

- Starting a new Swift App project and deciding how to split modules.
- Writing the first version of `Package.swift`.
- Wanting to reserve the option of shipping core logic to Android / cross-platform later.
- Introducing CloudKit / GameKit / StoreKit and deciding the import scope.
- User asks "single Package or multiple", "should the App target be thin", "how do I wire DI".

## Default decisions

### Single Package + multiple targets

- **Put all modules in one Swift Package**, splitting by target (named e.g. `<Project>Kit`).
- Don't start with multiple Packages — they only add `Package.swift` maintenance cost and CI resolution time.

### Very thin App target

- The App target only contains:
  - `@main`, the `App` struct
  - `Info.plist`, entitlements
  - Assets / Asset Catalog
  - A single DI composition root (wiring protocols to concrete implementations)
- All views, logic, and Storage live in the Package.
- The App target is **not tested** (it can't really be); all testable logic is in the Package.

### Dependencies flow upward, never downward

```
Engine (pure Swift core)
   ↑
GameState / Domain
   ↑
Service modules (CloudKit / GameKit / Storage / Telemetry)
   ↑
UI module (SwiftUI)
   ↑
App target
```

### Restricted Apple framework imports

- `CloudKit` is imported only in its designated service target.
- Same for `GameKit` / `StoreKit`.
- The UI and logic layers consume these **via injected protocols**, never importing the framework directly.
- This is the precondition for "core ports to Android / Linux" (Swift on Android can consume pure Swift modules directly).

### One test target per production target

- Each production target has a matching test target named `<Module>Tests`.
- Shared fakes / stubs can be factored into a separate `<Project>KitTesting` target imported by multiple test targets.

## Rationale

- Single Package: the App's modules have no need for external publication, so multi-Package's marginal cost outweighs the benefit.
- Thin App target: SwiftUI previews can run straight from the Package, yielding the fastest preview iteration loop.
- Restricted framework imports: enables unit testing, keeps previews free of permission dialogs, and preserves the portability path.
- One-to-one test targets: dependencies are clear, and CI can run only the modules that matter (paired with selective testing tooling).

## Deviation considerations

- **A module needs to be published externally**: upgrade to multi-Package; usually defer until the need is real.
- **A third-party dep is so heavy it harms build time**: pin it inside a single target and fan out from logic layers.
- **Sharing across multiple Apps**: extract into a standalone repo Swift Package.

## Example shape

```
<Project>/
├── App/                          # thin shell
│   ├── <Project>App.swift        # @main + DI composition root
│   └── (Assets, Info.plist, entitlements)
└── Packages/
    └── <Project>Kit/
        ├── Package.swift
        └── Sources/
            ├── <Engine>/         # pure Swift core
            ├── <Domain>/         # domain logic
            ├── <Storage>/        # service module (CloudKit import restricted here)
            ├── <Telemetry>/      # Logger / Tracking facade
            └── <UI>/             # SwiftUI Views
        └── Tests/
            └── <Module>Tests/    # one-to-one
```

## Related skills

- `swift6-concurrency`: Package applies `swiftLanguageModes: [.v6]` in one place.
- `apple-platform-targets`: Package `platforms:` aligned with App target.
- `swift-testing-baseline`: test target framework and location.
- `telemetry-facade-pattern`: why `Telemetry` is a standalone target.
