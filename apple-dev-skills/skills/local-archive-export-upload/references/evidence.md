# Evidence

## War stories (evidence tier in italics)

- **A pre-`touch`ed ExportOptions.plist breaks `PlistBuddy`** — it can't parse
  a 0-byte file ("Cannot parse a NULL or zero-length data"); remove the file
  first and let `PlistBuddy Add` create it fresh. *Practice observed* — the
  actual first-run failure on a real project's local-upload script.
- **Export-compliance can silently gate a build in "Processing."** Declaring
  `ITSAppUsesNonExemptEncryption` (`false` if you ship no custom encryption)
  once means every future upload skips ASC's interactive compliance question;
  a new app without it isn't blocked outright but holds pending a human answer
  in the ASC web UI (see `app-store-review-rejections`'s 2.5.x row). *Practice
  observed.*
- **`app-store` → `app-store-connect` rename (Xcode 15+)** confirmed live in
  `xcodebuild -help`'s own deprecation note. *Doc-verified*, Xcode 26.5.
- **The six load-bearing exportOptionsPlist keys** — confirmed as the common
  shape across four real ExportOptions.plist files (2 apps × 2 platforms) and
  cross-checked against `xcodebuild -help`'s key list. *Doc-verified +
  cross-project-observed.*
