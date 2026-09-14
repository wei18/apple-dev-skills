Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| currentEntitlements | https://developer.apple.com/documentation/storekit/transaction/currententitlements | Unlock state derives from entitlements |
| updates | https://developer.apple.com/documentation/storekit/transaction/updates | Listener starts at launch; unfinished transactions arrive at launch |
| finish() | https://developer.apple.com/documentation/storekit/transaction/finish() | Call only after delivering content |
| sync() | https://developer.apple.com/documentation/storekit/appstore/sync() | "Include some mechanism ... such as a Restore Purchases button"; "Call this function only in response to an explicit user action"; "In regular operations, there's no need to call sync()" |
| purchase(options:) | https://developer.apple.com/documentation/storekit/product/purchase(options:) | Platform table doesn't include visionOS; with the rows above, the bridge/skeleton's symbols (`Transaction.updates`, `.currentEntitlements`, `.finish()`, `.revocationDate`, `AppStore.sync()`, `Product.products(for:)`, `.purchase(options:)`, `.PurchaseResult`, `VerificationResult`) were checked against Apple's StoreKit docs (*Apple-doc-verified*) |
| Setting up StoreKit Testing in Xcode | https://developer.apple.com/documentation/xcode/setting-up-storekit-testing-in-xcode | Edit Scheme -> Run -> Options -> StoreKit Configuration |
| In-App Purchases | https://developer.apple.com/documentation/appstoreconnectapi/in-app-purchases | Scope: the `/v2/inAppPurchases` endpoint family |
| App Review Guidelines §3.1.1 | https://developer.apple.com/app-store/review/guidelines/#in-app-purchase | "you should make sure you have a restore mechanism for any restorable in-app purchases" (no API or placement mandated) |
| Statements — Switching Over Future Enumeration Cases (The Swift Programming Language) | https://docs.swift.org/swift-book/documentation/the-swift-programming-language/statements/#Switching-Over-Future-Enumeration-Cases | `@unknown default` semantics; omitting it is an error in Swift 6. The skill's bridge/skeleton typechecks clean under `swiftc -swift-version 6 -typecheck` (Swift 6.3.2 / Xcode 26.5), 0 errors/warnings (*Compiled-verified*) |
