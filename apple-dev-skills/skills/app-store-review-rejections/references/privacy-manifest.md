# Privacy manifest (`PrivacyInfo.xcprivacy`)

The upload-time and review-time rules around the privacy manifest, condensed from
Apple's documentation. Every falsifiable claim carries its source in §Sources;
reason codes are quoted from Apple's page, not paraphrased — copy them exactly.

## Contents

- [What the file is and where it lives](#what-the-file-is-and-where-it-lives)
- [The four top-level keys](#the-four-top-level-keys)
- [Required-reason APIs and their reason codes](#required-reason-apis-and-their-reason-codes)
- [Third-party SDKs](#third-party-sdks)
- [Reading the Xcode privacy report](#reading-the-xcode-privacy-report)
- [Upload-time emails](#upload-time-emails)
- [Parity with the App Privacy label](#parity-with-the-app-privacy-label)
- [Info.plist purpose strings](#infoplist-purpose-strings)
- [Pre-submit checklist](#pre-submit-checklist)
- [Sources](#sources)

## What the file is and where it lives

- A property list named exactly `PrivacyInfo.xcprivacy` ("the required file name for
  bundled privacy manifests"). Create it in Xcode via File > New File > Resource >
  **App Privacy** File type, and check the target so it lands in the target's
  resources — "You need to add the privacy manifest file to your target's resources
  for Xcode to use it when you generate a privacy report." [S1]
- Location: iOS / iPadOS / tvOS / visionOS / watchOS apps place it at the **root of
  the app bundle** (`Sample.app/PrivacyInfo.xcprivacy`); macOS and Mac Catalyst apps
  at `Contents/Resources/`. Frameworks follow the same split (root vs
  `Versions/A/Resources/`). Xcode places it correctly when the file is a target
  resource. [S2]
- Swift packages: Xcode "doesn't recognize privacy manifest files as resources by
  default" — declare it explicitly, e.g. `resources: [.process("PrivacyInfo.xcprivacy")]`. [S2]
- A `.a` static library "doesn't support resources such as the privacy manifest";
  ship a static *framework* target instead. [S2]
- "All privacy manifest files in your app must be valid, containing only the expected
  keys and values." App Store Connect rejects submissions with invalid manifests. [S2]

## The four top-level keys

| Key | Type | When it is required |
|---|---|---|
| `NSPrivacyTracking` | Boolean | "indicates whether your app or third-party SDK uses data for tracking as defined under the App Tracking Transparency framework. When set to `true` you need to provide a list of internet domains in `NSPrivacyTrackingDomains`." [S1] |
| `NSPrivacyTrackingDomains` | Array of String | "lists the internet domains your app or third-party SDK connects to that engage in tracking. If the user has not granted tracking permission through the App Tracking Transparency framework, network requests to these domains fail and your app receives an error. To provide a list of internet domains in `NSPrivacyTrackingDomains`, set `NSPrivacyTracking` to `true`." [S1] Each entry: top-level domain or subdomain, no path/query, no trailing slash. `NSPrivacyTracking: false` with a non-empty domains array is *invalid*; `true` with an empty array is *invalid*. [S7] |
| `NSPrivacyCollectedDataTypes` | Array of Dictionary | The data types collected — required "on all platforms". Each dictionary has `NSPrivacyCollectedDataType`, `NSPrivacyCollectedDataTypeLinked` (Bool), `NSPrivacyCollectedDataTypeTracking` (Bool), `NSPrivacyCollectedDataTypePurposes` (Array). Only Apple's listed type and purpose values are accepted: "Xcode won't generate a privacy report correctly if you define your own collected data types". [S1][S3] |
| `NSPrivacyAccessedAPITypes` | Array of Dictionary | The required-reason API categories used — required "on iOS, iPadOS, tvOS, visionOS, and watchOS". Each dictionary has exactly `NSPrivacyAccessedAPIType` (String) and `NSPrivacyAccessedAPITypeReasons` (Array of String). [S1][S4][S8] |

Omission rules (from TN3181): if the app contacts no tracking domains, either remove
both tracking keys or set `NSPrivacyTracking` to `false` and remove
`NSPrivacyTrackingDomains`; if `NSPrivacyAccessedAPITypes` would be empty, remove
the key rather than ship an empty array. [S7]

## Required-reason APIs and their reason codes

Why this exists: "Regardless of whether a user gives your app permission to track,
fingerprinting is not allowed." Since May 1, 2024 "apps that don't describe their use
of required reason API in their privacy manifest file aren't accepted by App Store
Connect." The app declares APIs used in *its own* code; an SDK declares its own —
"Your third-party SDK can't rely on the privacy manifest files for apps that link the
third-party SDK". "For each executable or dynamic library in an app that uses a
required reason API, the bundle that includes the executable or dynamic library needs
to include a privacy manifest file that reports the API." [S4]

The five `NSPrivacyAccessedAPIType` values and the reason codes each accepts. The
reason text is the first sentence of Apple's definition; every reason also carries
an off-device / usage restriction paragraph on the source page — read it before
declaring. [S5][S8]

### `NSPrivacyAccessedAPICategoryFileTimestamp`

APIs: `creationDate`, `modificationDate`, `fileModificationDate`,
`contentModificationDateKey`, `creationDateKey`, `getattrlist`, `getattrlistbulk`,
`fgetattrlist`, `stat`, `fstat`, `fstatat`, `lstat`, `getattrlistat`.

| Code | Reason |
|---|---|
| `DDA9.1` | "Declare this reason to display file timestamps to the person using the device." |
| `C617.1` | "Declare this reason to access the timestamps, size, or other metadata of files inside the app container, app group container, or the app's CloudKit container." |
| `3B52.1` | "Declare this reason to access the timestamps, size, or other metadata of files or directories that the user specifically granted access to, such as using a document picker view controller." |
| `0A2A.1` | "Declare this reason if your third-party SDK is providing a wrapper function around file timestamp API(s) for the app to use, and you only access the file timestamp APIs when the app calls your wrapper function. This reason may only be declared by third-party SDKs." |

### `NSPrivacyAccessedAPICategorySystemBootTime`

APIs: `systemUptime`, `mach_absolute_time()`.

| Code | Reason |
|---|---|
| `35F9.1` | "Declare this reason to access the system boot time in order to measure the amount of time that has elapsed between events that occurred within the app or to perform calculations to enable timers." |
| `8FFB.1` | "Declare this reason to access the system boot time to calculate absolute timestamps for events that occurred within your app, such as events related to the UIKit or AVFAudio frameworks." |
| `3D61.1` | "Declare this reason to include system boot time information in an optional bug report that the person using the device chooses to submit." |

### `NSPrivacyAccessedAPICategoryDiskSpace`

APIs: `volumeAvailableCapacityKey`, `volumeAvailableCapacityForImportantUsageKey`,
`volumeAvailableCapacityForOpportunisticUsageKey`, `volumeTotalCapacityKey`,
`systemFreeSize`, `systemSize`, `statfs`, `statvfs`, `fstatfs`, `fstatvfs`,
`getattrlist`, `fgetattrlist`, `getattrlistat`.

| Code | Reason |
|---|---|
| `85F4.1` | "Declare this reason to display disk space information to the person using the device." |
| `E174.1` | "Declare this reason to check whether there is sufficient disk space to write files, or to check whether the disk space is low so that the app can delete files when the disk space is low." |
| `7D9E.1` | "Declare this reason to include disk space information in an optional bug report that the person using the device chooses to submit." |
| `B728.1` | "Declare this reason if your app is a health research app, and you access this API category to detect and inform research participants about low disk space impacting the research data collection." |

### `NSPrivacyAccessedAPICategoryActiveKeyboards`

API: `activeInputModes`.

| Code | Reason |
|---|---|
| `3EC4.1` | "Declare this reason if your app is a custom keyboard app, and you access this API category to determine the keyboards that are active on the device." |
| `54BD.1` | "Declare this reason to access active keyboard information to present the correct customized user interface to the person using the device." |

### `NSPrivacyAccessedAPICategoryUserDefaults`

API: `UserDefaults`. This is the category almost every app hits — any
`UserDefaults.standard` read or write needs a declaration.

| Code | Reason |
|---|---|
| `CA92.1` | "Declare this reason to access user defaults to read and write information that is only accessible to the app itself." |
| `1C8F.1` | "Declare this reason to access user defaults to read and write information that is only accessible to the apps, app extensions, and App Clips that are members of the same App Group as the app itself." |
| `C56D.1` | "Declare this reason if your third-party SDK is providing a wrapper function around user defaults API(s) for the app to use, and you only access the user defaults APIs when the app calls your wrapper function. This reason may only be declared by third-party SDKs." |
| `AC6B.1` | "Declare this reason to access user defaults to read the `com.apple.configuration.managed` key to retrieve the managed app configuration set by MDM, or to set the `com.apple.feedback.managed` key to store feedback information to be queried over MDM". |

Apple "continually reviews the list of required reason APIs and reasons for usage" —
re-check the source page when a new category or code appears in an upload email. [S4]

## Third-party SDKs

- Apple's list of "SDKs that require a privacy manifest and signature" (Abseil,
  AFNetworking, Alamofire, Firebase modules, FBSDK*, GoogleUtilities, Sentry, …) lives
  at [S6]. "You must include the privacy manifest for any SDK listed below when you
  submit new apps in App Store Connect that include those SDKs, or when you submit an
  app update that adds one of the listed SDKs as part of the update." "Signatures are
  also required in these cases where the listed SDKs are used as binary dependencies.
  Any version of a listed SDK, as well as any SDKs that repackage those on the list,
  are included in the requirement." [S6]
- Unlisted SDKs still need a manifest "if it uses a required reasons API, collects
  data about the person using apps that include the third-party SDK, enables the app
  to collect data about people using the app, or contacts tracking domains". [S1]
- **Do not duplicate an SDK's declarations in the app manifest.** "Third-party SDKs
  need to provide their own privacy manifest files that record the types of data they
  collect. Your app's privacy manifest file doesn't need to cover data collected by
  third-party SDKs that your app links to." [S3] DTS repeats it for the ITMS-91061
  case: the app manifest must "**only** describe the privacy practices of your app.
  Do not add the privacy practices of the SDK to your app's privacy manifest." [S10]
- Enforcement dates: required-reason declarations since May 1, 2024 [S4][S9]; a valid
  manifest for every file since November 12, 2024 [S7]; a manifest inside each listed
  SDK since February 12, 2025 [S2][S10].
- Escape hatch when an SDK ships an *invalid* manifest and the vendor is slow: locate
  it in the archive (Organizer → Archives → Show in Finder → Show Package Contents),
  delete or fix it, and distribute from the Archives organizer so Xcode re-signs. [S2]

## Reading the Xcode privacy report

Product > Archive → in the Organizer, Control-click the archive → **Generate Privacy
Report** → save and open the PDF. "Xcode can create a privacy report by aggregating
the privacy manifests from your app and the third-party SDKs it links to." "The
privacy report is organized in a similar way to Privacy Nutrition Labels. Refer to
this report when you provide your app's privacy details in App Store Connect." [S3]
Use it as the source of truth for the App Privacy questionnaire (see parity below),
and as the diff when an SDK bump changes what is collected.

## Upload-time emails

Apple identifies each upload-time problem with an `ITMS-` code in the email. The codes
below have an Apple-authored source; other codes circulating in forum posts are quoted
from developer emails only, so they are not listed here.

| Code | Meaning | Fix |
|---|---|---|
| `ITMS-91056: Invalid privacy manifest` | "The PrivacyInfo.xcprivacy file from the following path is invalid … Keys and values in your app's privacy manifests must be valid." Either a malformed plist or a valid plist with unexpected keys/values (wrong types, empty arrays, reason strings that don't match the category, a `false` tracking flag with domains listed). [S7] | `plutil -lint /path/to/PrivacyInfo.xcprivacy`, then walk TN3181's reason/solution tables. If the path in the email is inside an SDK's bundle, update the SDK. [S7] |
| `ITMS-91061: Missing privacy manifest` | "Your app includes "<path/to/SDK>", which includes <SDK>, an SDK that was identified in the documentation as a privacy-impacting third-party SDK. Starting February 12, 2025, if a new app includes a privacy-impacting SDK, or an app update adds a new privacy-impacting SDK, the SDK must include a privacy manifest file." [S10] | Get an SDK version that bundles its own manifest at the expected location; never paper over it by adding the SDK's practices to the app manifest. [S10] |
| Missing-reason email (required-reason API) | "If you upload an app to App Store Connect that uses required reason API without describing the reason in its privacy manifest file, Apple sends you an email reminding you to add the reason to the app's privacy manifest." Since May 1, 2024 the upload is not accepted. [S4] | Add the category + reason dictionary to whichever bundle's code uses the API (app or SDK). The email names the offending file, so a category reported for the app binary is yours to declare; one reported for `Frameworks/X.framework` is the SDK's. [S4] |
| `ITMS-90683: Missing purpose string in Info.plist` | "Your app's code references one or more APIs that access sensitive user data, or the app has one or more entitlements that permit such access. The Info.plist file for the "{app-bundle-path}" bundle should contain a NSLocationWhenInUseUsageDescription key with a user-facing purpose string". [S11] | Add the `…UsageDescription` key for every protected resource the code (including SDK code) can reach — see purpose strings below. |

## Parity with the App Privacy label

The `SKILL.md` "Privacy-label parity" row is the rule; this is the mechanism. App Store
Connect's App Privacy answers, the aggregated privacy report, and the actual SDK
behavior must describe the same collection. Apple ties them together explicitly: the
privacy report is "organized in a similar way to Privacy Nutrition Labels" and is
what you "refer to … when you provide your app's privacy details in App Store
Connect" [S3]. So the workflow is one-directional — regenerate the privacy report
after every SDK change, then update the App Privacy questionnaire from it, never the
other way round.

## Info.plist purpose strings

Purpose strings are a separate mechanism from the manifest, but they fail at the same
two gates: at runtime and at upload/review.

- **Runtime.** "Always provide a valid purpose string in the Signing and Capabilities
  editor if your app uses a protected resource. If you don't, attempts to access the
  resource fail, and might cause your app to crash." The crash report's
  `Termination Reason` field can carry this — Apple lists "accessing privacy sensitive
  information without a purpose string" among its example messages. [S11][S13]
- **Upload / review.** "App Review checks for the use of protected resources, and
  rejects apps that contain code accessing those resources without a purpose string"
  (ITMS-90683 above). A *vague* string is a Guideline 5.1.1(ii) problem: "Ensure your
  purpose strings clearly and completely describe your use of the data." Apple's
  validity rules: not blank / whitespace, under 4,000 bytes, correct type, and "a
  description that's accurate, meaningful, and specific about why the app needs to
  access the protected resource" — for every localization. [S11][S12]
- Localize them in `InfoPlist.xcstrings`; Xcode writes them as
  `INFOPLIST_KEY_<KeyName>` build settings. [S11]

Common keys (current, non-deprecated names): [S14]

| Resource | Key |
|---|---|
| Camera | `NSCameraUsageDescription` |
| Microphone | `NSMicrophoneUsageDescription` |
| Photos (read) / (add only) | `NSPhotoLibraryUsageDescription` / `NSPhotoLibraryAddUsageDescription` |
| Location (when in use) / (always) | `NSLocationWhenInUseUsageDescription` / `NSLocationAlwaysAndWhenInUseUsageDescription` (`NSLocationAlwaysUsageDescription` is deprecated) |
| Contacts | `NSContactsUsageDescription` |
| Calendars (full) / (write-only) | `NSCalendarsFullAccessUsageDescription` / `NSCalendarsWriteOnlyAccessUsageDescription` |
| Reminders | `NSRemindersFullAccessUsageDescription` |
| Bluetooth | `NSBluetoothAlwaysUsageDescription` (`NSBluetoothPeripheralUsageDescription` is deprecated) |
| Face ID | `NSFaceIDUsageDescription` |
| Motion | `NSMotionUsageDescription` |
| Health (read) / (write) | `NSHealthShareUsageDescription` / `NSHealthUpdateUsageDescription` |
| Local network | `NSLocalNetworkUsageDescription` |
| Speech recognition | `NSSpeechRecognitionUsageDescription` |
| Tracking (ATT) | `NSUserTrackingUsageDescription` |
| Game Center friends | `NSGKFriendListUsageDescription` |

HIG rules for the prompt itself: "Request permission only when your app clearly needs
access to the data or resource"; "Avoid requesting permission at launch unless the
data or resource is required for your app to function"; write "a brief, complete
sentence that's straightforward, specific, and easy to understand" in sentence case,
active voice, ending with a period. Apple's own good/bad pair: "The app records during
the night to detect snoring sounds." vs "Microphone access is needed for a better
experience." If you show a pre-alert screen, it must have exactly one button labeled
like "Continue" / "Next" that opens the system alert, no cancel/close, and must never
imitate or annotate the system alert; for tracking, incentives or look-alike screens
"will lead to rejection by App Store review". [S15]

## Pre-submit checklist

1. `PrivacyInfo.xcprivacy` is a target resource of the app (and of every first-party
   framework / package target that uses a required-reason API); for packages the
   `resources:` entry exists. [S1][S2]
2. `plutil -lint` passes on the app manifest **and** every manifest under
   `Frameworks/` in the archive. [S7]
3. Every `NSPrivacyAccessedAPITypes` entry has a category string from the list of five
   and at least one reason code copied verbatim from the table above; no empty arrays;
   `UserDefaults` usage is declared (`CA92.1` for app-private defaults). [S5][S7]
4. Tracking keys are consistent: both present with `true` + non-empty, well-formed
   domains, or `NSPrivacyTracking: false` with no domains key. [S7]
5. Every SDK on Apple's list is at a version that bundles its own manifest (and a
   signature when consumed as a binary); the app manifest does not restate SDK
   practices. [S6][S10]
6. Product > Archive → Generate Privacy Report; the report matches the App Privacy
   answers in App Store Connect and the ATT stance in `SKILL.md`'s 5.1.2 row. [S3]
7. Every protected resource reachable from app or SDK code has its
   `…UsageDescription` key, localized in every shipped locale, with a specific
   sentence (not "needed for a better experience"). [S11][S12][S15]
8. Permission prompts fire in context, not at launch; any pre-alert screen follows
   the single-"Continue"-button rule. [S15]

## Sources

- [S1] Privacy manifest files — https://developer.apple.com/documentation/bundleresources/privacy-manifest-files
- [S2] Adding a privacy manifest to your app or third-party SDK — https://developer.apple.com/documentation/bundleresources/adding-a-privacy-manifest-to-your-app-or-third-party-sdk
- [S3] Describing data use in privacy manifests — https://developer.apple.com/documentation/bundleresources/describing-data-use-in-privacy-manifests
- [S4] Describing use of required reason API — https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api
- [S5] `NSPrivacyAccessedAPIType` (categories, APIs, reason codes) — https://developer.apple.com/documentation/bundleresources/app-privacy-configuration/nsprivacyaccessedapitypes/nsprivacyaccessedapitype
- [S6] Upcoming third-party SDK requirements (SDK list) — https://developer.apple.com/support/third-party-SDK-requirements/
- [S7] TN3181: Debugging an invalid privacy manifest — https://developer.apple.com/documentation/technotes/tn3181-debugging-invalid-privacy-manifest
- [S8] TN3183: Adding required reason API entries to your privacy manifest — https://developer.apple.com/documentation/technotes/tn3183-adding-required-reason-api-entries-to-your-privacy-manifest
- [S9] Privacy updates for App Store submissions (Feb 29, 2024) — https://developer.apple.com/news/?id=3d8a9yyh
- [S10] Handling ITMS-91061: Missing privacy manifest (DTS Engineer) — https://developer.apple.com/forums/thread/774960
- [S11] Requesting access to protected resources — https://developer.apple.com/documentation/uikit/requesting-access-to-protected-resources
- [S12] App Store Review Guidelines 5.1.1 — https://developer.apple.com/app-store/review/guidelines/#privacy
- [S13] Examining the fields in a crash report (Termination Reason) — https://developer.apple.com/documentation/xcode/examining-the-fields-in-a-crash-report
- [S14] Protected resources (Info.plist keys) — https://developer.apple.com/documentation/bundleresources/protected-resources
- [S15] Human Interface Guidelines: Privacy — https://developer.apple.com/design/human-interface-guidelines/privacy
- Also relevant: TN3182 (tracking keys) — https://developer.apple.com/documentation/technotes/tn3182-adding-privacy-tracking-keys-to-your-privacy-manifest ; TN3184 (data collection keys) — https://developer.apple.com/documentation/technotes/tn3184-adding-data-collection-details-to-your-privacy-manifest
