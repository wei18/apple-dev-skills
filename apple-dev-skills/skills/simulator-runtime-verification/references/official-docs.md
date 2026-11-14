Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

Apple pages were read through the `https://developer.apple.com/tutorials/data/documentation/<path>.json` form on 2026-11-14.

| Page | URL | Backs |
|---|---|---|
| Xcode 14 Release Notes | https://developer.apple.com/documentation/xcode-release-notes/xcode-14-release-notes | Simulator receives remote notifications (iOS 16, macOS 13, Apple silicon or T2); APNs sandbox only; token unique per simulator and Mac; variable token length; locally simulated pushes (`.apns` files, `simctl push`) support fewer features than remote ones, for example Notification Service Extensions |
| `application(_:didRegisterForRemoteNotificationsWithDeviceToken:)` | https://developer.apple.com/documentation/uikit/uiapplicationdelegate/application(_:didregisterforremotenotificationswithdevicetoken:) | The delegate method the `lldb` token injection calls |
| `errSecMissingEntitlement` | https://developer.apple.com/documentation/security/errsecmissingentitlement | "A required entitlement is missing"; inspect entitlements with `codesign` on a build for a hardware target, not a Simulator build. The value `-34018` is from the SDK's `Security/SecBase.h` (iPhoneSimulator 27.2 SDK), not this page |
| Supporting associated domains | https://developer.apple.com/documentation/xcode/supporting-associated-domains | Association file fetched at install; Apple CDN since iOS 14 / macOS 11; alternate mode for servers the CDN cannot reach |
| `UNNotificationAttachment` | https://developer.apple.com/documentation/usernotifications/unnotificationattachment | Supported image types JPEG, GIF, PNG (10 MB); remote attachments are validated after the Notification Service Extension finishes |
| `UNNotificationAttachmentOptionsTypeHintKey` | https://developer.apple.com/documentation/usernotifications/unnotificationattachmentoptionstypehintkey | Without the hint, the system uses the file name extension to determine the type |
| `xcrun simctl help <subcommand>` (Xcode 27.2) | local tool help | `push` payload rules (top-level `aps`, at most 4,096 bytes); `privacy` services list and "Some permission changes will terminate the application if running"; `addmedia` accepts vCard contacts; `get_app_container … data`; `spawn` path search and `SIMCTL_CHILD_` variables; `launch --wait-for-debugger` |

Claims no official page states (practice observations, stamped in the skill body):

- `simctl spawn … defaults write <bundle-id>` missing the app's data container, and whether a host-side plist write needs the simulator shut down.
- A signed Simulator build carrying its entitlements in an `__entitlements` section readable with `strings`, and `codesign -d` printing nothing for it.
- `CODE_SIGNING_ALLOWED=NO` or `CODE_SIGN_IDENTITY=""` builds lacking entitlements on the Simulator, and the ad hoc signing settings that restore them.
- A debugger-launched process not presenting foreground banners.
- `simctl privacy … reset all` resetting ATT.
- `simctl openurl` being unreliable for Universal Links on a fresh simulator, and a reboot making the system fetch the association file again.
- No device token on a freshly created simulator's first launch.
