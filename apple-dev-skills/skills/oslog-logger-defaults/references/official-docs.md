Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Logger | https://developer.apple.com/documentation/os/logger | `Logger(subsystem:category:)` |
| Generating Log Messages from Your Code | https://developer.apple.com/documentation/os/generating-log-messages-from-your-code | Integer/float/Bool values aren't redacted; dynamic strings and complex dynamic objects are; use reverse-DNS notation for the subsystem string |
| OSLogPrivacy | https://developer.apple.com/documentation/os/oslogprivacy | `.private` / `.public` / `.sensitive` / `private(mask:)` |
| Viewing Log Messages | https://developer.apple.com/documentation/os/viewing-log-messages | Xcode's debugger shows log output automatically when attached (doesn't state that `.private` gets unmasked) |
| OSLogStore | https://developer.apple.com/documentation/oslog/oslogstore | Only confirms the API exists -- the "doesn't bypass redaction" / "debugger shows `.private`" claims are not written on any official page; treat as a practice observation |
| apple/swift-log | https://github.com/apple/swift-log | "SwiftLog is an API package" with community-maintained backends |
