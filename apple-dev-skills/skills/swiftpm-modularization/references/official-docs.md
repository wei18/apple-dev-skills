Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| v26 | https://developer.apple.com/documentation/packagedescription/supportedplatform/iosversion/v26 | `.iOS(.v26)` requires SwiftPM 6.2 |
| SE-0466 Control default actor isolation inference | https://github.com/swiftlang/swift-evolution/blob/main/proposals/0466-control-default-actor-isolation.md | `.defaultIsolation` |
| swiftLanguageMode(_:_:) | https://developer.apple.com/documentation/packagedescription/swiftsetting/swiftlanguagemode(_:_:) | Target-level language mode |
| Resolving package versions (SwiftPM docs, source) | https://github.com/swiftlang/swift-package-manager/blob/main/Sources/PackageManagerDocs/Documentation.docc/ResolvingPackageVersions.md | "resolves to those versions as long as they are still eligible"; `--force-resolved-versions` (the docs.swift.org mirror 404s as of 2026-09-13) |
| Workspace+Dependencies.swift (source) | https://github.com/swiftlang/swift-package-manager/blob/main/Sources/Workspace/Workspace%2BDependencies.swift | A mismatched originHash triggers re-resolution and rewrites the file; `--force-resolved-versions` uses the lock file and does not write originHash -- keep the originHash-replacement step |
| Bundling resources with a Swift package | https://developer.apple.com/documentation/xcode/bundling-resources-with-a-swift-package | `.xcassets` section: `Bundle.module` |
| Getting Started with the Swift SDK for Android | https://www.swift.org/documentation/articles/swift-sdk-for-android-getting-started.html | "When to invoke" section: porting core logic to Android (HTTP 200; JS-rendered, content not verbatim-verified) |
