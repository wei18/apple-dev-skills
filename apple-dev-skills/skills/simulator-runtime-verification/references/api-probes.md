# Simulator API probes

A probe is a small command-line program that calls one framework API with chosen inputs and
prints what happens. Running it on a throwaway simulator answers "how does this API treat
input X" in seconds, and the run repeats exactly. A device push or an app rebuild does neither.

## Build and run

```bash
xcrun -sdk iphonesimulator swiftc -target arm64-apple-ios27.0-simulator probe.swift -o probe
xcrun simctl spawn <UDID> "$PWD/probe" "$PWD/input-1" "$PWD/input-2"
```

- Set `-target` to `arm64-apple-ios<runtime>-simulator` for the runtime you test. Without it,
  `xcrun -sdk iphonesimulator swiftc` targets the host macOS triple (checked with
  `swiftc -print-target-info`, Swift 6.4.2, Xcode 27.2), and the probe tests macOS behaviour.
- Give `simctl spawn` an absolute path. Its help text searches a path that contains no `/` on
  the device's `$PATH`, not in your working directory.
- To set environment variables for the probe, prefix them with `SIMCTL_CHILD_` in the calling
  shell (from `simctl help spawn`).

## Limits

A spawned probe is a plain process, not an installed app. It has no bundle identifier, no
entitlements and no app container, so anything that needs those (notification authorization,
Keychain access groups, app group containers) does not behave as it does in the app (inferred
from how `spawn` works; not tested API by API). Use probes for input handling: initializers,
parsers, type detection, ImageIO decoding. Test the rest in the app.

## Worked example: `UNNotificationAttachment` file-type detection

Question: which downloaded images will a Notification Service Extension be able to attach?

```swift
import Foundation
import UserNotifications

for path in CommandLine.arguments.dropFirst() {
    let url = URL(fileURLWithPath: path)
    do {
        let attachment = try UNNotificationAttachment(identifier: url.lastPathComponent, url: url, options: nil)
        print("\(url.lastPathComponent): accepted as \(attachment.type)")
    } catch {
        print("\(url.lastPathComponent): \(error.localizedDescription)")
    }
}
```

Result, with no type-hint option (observed once, 2026-11-05, iOS 27.0 Simulator runtime and
macOS; initializer only, rendering on screen not checked):

| File content | File name | Result |
|---|---|---|
| WebP | `image.webp` | `Unrecognized attachment file type` |
| WebP | `image` (no extension) | `Unrecognized attachment file type` |
| JPEG | `image.webp` | `Unrecognized attachment file type` |
| WebP | `image.jpg` | Accepted as `public.jpeg` |

This matches the documentation. Without `UNNotificationAttachmentOptionsTypeHintKey` the system
takes the type from the file name extension, and the supported image types are JPEG, GIF and
PNG. The page for the `type` property says the value is derived "from the attachment data";
the last row shows the extension wins at least at initialization.

What it means for an extension:

- An extension that names the downloaded file after the URL's last path component can attach
  only images whose URL happens to end in a supported extension.
- Detect the type from the bytes (`CGImageSourceCreateWithData`, then `CGImageSourceGetType`).
  Convert unsupported formats such as WebP to JPEG, and write the file with an extension that
  matches its content, or pass the matching UTI in
  `UNNotificationAttachmentOptionsTypeHintKey`.
- When push images go missing, check the attachment file's name and extension first.
