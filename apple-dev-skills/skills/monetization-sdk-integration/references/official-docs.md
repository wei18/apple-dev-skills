Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Set up Google Mobile Ads SDK (iOS) | https://developers.google.com/admob/ios/quick-start | SPM repo `swift-package-manager-google-mobile-ads`; `GADApplicationIdentifier` |
| Migrate SDK versions (iOS) | https://developers.google.com/admob/ios/migration | Anti-pattern: v12.0.0's Swift API dropped the `GAD` prefix |
| Set up UMP SDK (iOS) | https://developers.google.com/admob/ios/privacy | UMP consent flow |
| Third-party SDK requirements | https://developer.apple.com/support/third-party-SDK-requirements/ | The listed Google entries are GoogleDataTransport / GoogleSignIn / GoogleToolboxForMac / GoogleUtilities only -- not GoogleMobileAds / UMP |
| Privacy manifest files | https://developer.apple.com/documentation/bundleresources/privacy-manifest-files | An SDK's own manifest obligations (including tracking domains) |
| NSPrivacyTrackingDomains | https://developer.apple.com/documentation/bundleresources/app-privacy-configuration/nsprivacytrackingdomains | "If the user has not granted tracking permission ... network requests to these domains fail" |
| TN3181: Debugging an invalid privacy manifest | https://developer.apple.com/documentation/technotes/tn3181-debugging-invalid-privacy-manifest | Upload-time validation since 2024-11-12 (ITMS-91056); `NSPrivacyTracking=true` with empty domains (or false with domains present) is invalid |
| App Tracking Transparency | https://developer.apple.com/documentation/apptrackingtransparency | Pre-integration checklist's "Tracking ATT required" |
| when(platforms:) (SwiftPM 5.7+) | https://developer.apple.com/documentation/packagedescription/targetdependencycondition/when(platforms:)-5bxhc | Conditional-compile invariant: `condition: .when(platforms: [.iOS])` |
