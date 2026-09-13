Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Adopting strict concurrency in Swift 6 apps | https://developer.apple.com/documentation/swift/adoptingswift6 | Raise Strict Concurrency Checking to Complete before adopting the Swift 6 language mode |
| Build settings reference -- SWIFT_STRICT_CONCURRENCY | https://developer.apple.com/documentation/xcode/build-settings-reference#Strict-Concurrency-Checking | "This is always 'complete' when in the Swift 6 language mode" -> setting `targeted` has no effect once in Swift 6 mode |
| Enable Complete Concurrency Checking (Swift 6 Concurrency Migration Guide) | https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/enabledataracesafety | "Targets that adopt the Swift 6 language mode have complete checking" (official page; JS-rendered) |
| EnableDataRaceSafety.md (source) | https://github.com/swiftlang/swift-migration-guide/blob/main/Guide.docc/EnableDataRaceSafety.md | Offline mirror of the same guidance ("pre-Swift 6 language mode target") |
| SE-0466 Control default actor isolation inference | https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md | `.defaultIsolation(MainActor.self)` / `nil` |
| SE-0461 Run nonisolated async functions on the caller's actor by default | https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md | `@concurrent` |
| SE-0337 Incremental migration to concurrency checking | https://github.com/swiftlang/swift-evolution/blob/main/proposals/0337-support-incremental-migration-to-concurrency-checking.md | `@preconcurrency import` |
| swiftLanguageMode(_:_:) | https://developer.apple.com/documentation/packagedescription/swiftsetting/swiftlanguagemode(_:_:) | SwiftPM 6.0+ per-target language mode, including `.v5` |
