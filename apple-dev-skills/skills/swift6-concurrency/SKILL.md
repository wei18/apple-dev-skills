---
name: swift6-concurrency
description: Default to Swift 6 language mode with complete concurrency checking from the first line of code; treat all in-house types as needing Sendable; isolate third-party deps that lag with @preconcurrency. Invoke when starting a new Swift Apple-platform project, writing Package.swift, picking the Swift language mode in Xcode build settings, or when asked "should I turn on strict concurrency?".
---

# Swift 6 / Strict Concurrency

## When to invoke

- Starting a new Swift iOS / macOS App project and deciding the language mode.
- Writing `Package.swift` and setting `swiftLanguageModes` / `SWIFT_STRICT_CONCURRENCY`.
- Adding a new third-party dependency and hitting concurrency warnings / errors.
- User asks "how do I configure Swift 6 / complete concurrency / Sendable / actor / `@preconcurrency`".

## Default decisions

- **Swift 6 language mode + complete concurrency checking**, applied from the first line of code.
- All in-house types are treated as **needing `Sendable`** by default; any type shared across actors must declare it explicitly (`struct Foo: Sendable` or `final class Foo: Sendable` — the latter only valid when all stored properties are Sendable and the class is non-inheritable; for classes with mutable state, prefer `actor Foo` or `@unchecked Sendable` with manual synchronisation).
- Protocols that cross actor boundaries (DI injection points) are always declared `Sendable`, with methods `async throws`.
- For third-party deps that don't support Swift 6 complete checking, in order of preference:
  1. `@preconcurrency import X` to isolate the import
  2. Switch packages
  3. Defer adoption

## Rationale

- A greenfield project has no legacy code to migrate, so the pain of complete checking gets amortised — solved once per actor / Sendable as you write — rather than as a one-shot big-bang migration later.
- Swift 6 is the long-term direction of the language; early adoption avoids technical debt.
- Complete checking catches data races at compile time, more than minimal / targeted can.

## Deviation considerations

- **Migrating existing Swift 5 code**: switch to minimal or targeted concurrency checking and upgrade in stages; ramp up one file / module at a time, allowing `@preconcurrency` during transition.
- **Significant third-party lag**: if a critical dep doesn't support it, drop the whole project to targeted and patch module by module.
- **Teaching / demo projects**: if the goal is to demonstrate older API behaviour, keeping Swift 5 mode is fine.

## Related skills

- `apple-platform-targets`: Xcode 16+ is the first toolchain that formally supports Swift 6 language mode; consider this alongside deployment target decisions.
- `swiftpm-modularization`: `swiftLanguageModes: [.v6]` sets the default for the whole package; individual targets can opt down with `swiftSettings: [.swiftLanguageMode(.v5)]` (available since swift-tools-version 6.0) — useful when migrating a legacy dependency without blocking the rest of the package.
