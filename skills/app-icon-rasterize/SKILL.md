---
name: app-icon-rasterize
description: Rasterize a designer-authored 1024×1024 SVG into the PNG that Apple's asset catalog wants — no Homebrew dependency, no Cloud service, just `qlmanage` already on the Mac.
---

# App icon rasterize (SVG → 1024 PNG)

Use when a designer hands off the icon as SVG and you need the PNG that `AppIcon.appiconset/Contents.json` references.

This is the gap discovered during first-pass icon production on a real project — the SVG → 1024 PNG step was undocumented (only the downstream Pillow Lanczos *downscale* to the macOS ladder was written up). Each appearance — Light, Dark, Tinted — is a single 1024 universal PNG produced by exactly one rasterize step, documented here. (Tinted is now a standard third appearance alongside Light and Dark; all three apps in the reference project ship `AppIcon-Tinted.png`.)

## When to use

- Designer subagent (or human designer) produced a clean `light.svg` + `dark.svg` + `tinted.svg` matching the icon spec
- You need the matching `AppIcon-Light.png` + `AppIcon-Dark.png` in `<app>/Assets.xcassets/AppIcon.appiconset/`
- This Mac does NOT have `rsvg-convert`, `inkscape`, or `imagemagick` (verified absent on the project Mac as of 2026-06-01; Homebrew is not installed)

## When NOT to use

- The SVG uses `<filter>` blurs, `<text>`, embedded fonts, or other features QuickLook's SVG generator may render unreliably. Re-author the SVG with flat shapes first.
- The SVG already ships as PNG from the designer (e.g. Affinity / Figma export). Just commit the PNG.

## macOS ladder reality check (2026-06-02)

**Xcode 26 / macOS Sequoia still requires the explicit 16/32/128/256/512 ladder for macOS app icons.** "Single Size" is iOS-only. The Appearances Inspector for macOS targets does not expose a single-asset option. Without the ladder, Xcode emits "AppIcon has N unassigned children" on the macOS target because the universal idiom does not satisfy AppKit's expected slots.

After producing the 1024 master:

```bash
SRC=<App>/Assets.xcassets/AppIcon.appiconset/AppIcon-Light.png
DST=<App>/Assets.xcassets/AppIcon-macOS.appiconset
mkdir -p "$DST"
cp "$SRC"                                "$DST/icon_512x512@2x.png"   # 1024
sips -Z 512 "$SRC" --out "$DST/icon_256x256@2x.png"  # 512
sips -Z 512 "$SRC" --out "$DST/icon_512x512.png"     # 512
sips -Z 256 "$SRC" --out "$DST/icon_128x128@2x.png"  # 256
sips -Z 256 "$SRC" --out "$DST/icon_256x256.png"     # 256
sips -Z 128 "$SRC" --out "$DST/icon_128x128.png"     # 128
sips -Z 64  "$SRC" --out "$DST/icon_32x32@2x.png"    # 64
sips -Z 32  "$SRC" --out "$DST/icon_32x32.png"       # 32
sips -Z 32  "$SRC" --out "$DST/icon_16x16@2x.png"    # 32
sips -Z 16  "$SRC" --out "$DST/icon_16x16.png"       # 16
```

`sips -Z <max>` resizes the longest dimension to `<max>` (Lanczos-equivalent quality). Each downscale is from the 1024 master, not the previous step.

`Project.swift` needs the SDK-scoped override so iOS targets keep the universal `AppIcon` and macOS targets pick up the ladder:

```swift
let appTargetSettings: SettingsDictionary = swiftSettings.merging([
    "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon",
    "ASSETCATALOG_COMPILER_APPICON_NAME[sdk=macosx*]": "AppIcon-macOS",
]) { _, new in new }
```

## SVG authoring contract — read BEFORE writing the SVG

The designer's SVG **must NOT** bake rounded corners into the artwork. Apple's compositor applies the squircle mask at render time (iOS Springboard, macOS Dock, every preview surface). Baking corners produces a *double-mask* look — the icon shows up smaller than its peers with visible inner padding.

Common mistakes that cause this:

```xml
<!-- WRONG — corners baked into the artwork via clipPath -->
<defs>
  <clipPath id="iconMask">
    <rect width="1024" height="1024" rx="246" ry="246"/>
  </clipPath>
</defs>
<g clip-path="url(#iconMask)">
  <rect width="1024" height="1024" fill="#FAF8F3"/>
  ...
</g>

<!-- ALSO WRONG — rx/ry directly on the background rect -->
<rect width="1024" height="1024" rx="246" ry="246" fill="#FAF8F3"/>
```

```xml
<!-- RIGHT — background fills 1024×1024 to the edges, no clip, no rx/ry -->
<rect x="0" y="0" width="1024" height="1024" fill="#FAF8F3"/>
<!-- artwork on top, also no clip -->
```

After rasterize, `sips -g hasAlpha …png` will still report `yes` because QuickLook writes 8-bit RGBA — but every pixel including the corners must be **opaque**. Quick check: open the PNG in Preview at 100%, hover the corners — Digital Color Meter should report the background color (e.g. `#FAF8F3`), not transparency.

This rule applies to Light, Dark, and Tinted variants. There is no platform on which the artwork should pre-apply its own squircle.

## Procedure

```bash
# 1. Designer writes SVG to ../tmp/ (project-scope scratch
#    dir, NOT /tmp). Each SVG must declare
#    width="1024" height="1024" viewBox="0 0 1024 1024".
ls -la ../tmp/<app>-icon-light.svg ../tmp/<app>-icon-dark.svg

# 2. Rasterize via QuickLook thumbnail generator.
#    -t           thumbnail mode
#    -s 1024      thumbnail size (square)
#    -o <dir>     output directory (-o cannot rename the file, see step 3)
qlmanage -t -s 1024 -o ../tmp \
  ../tmp/<app>-icon-light.svg \
  ../tmp/<app>-icon-dark.svg \
  ../tmp/<app>-icon-tinted.svg

# 3. qlmanage's quirk: it APPENDS `.png` to the source filename instead of
#    swapping the extension. So `light.svg` becomes `light.svg.png`. Rename
#    directly into the asset catalog so the .svg.png artifact never lingers.
mv ../tmp/<app>-icon-light.svg.png \
   <App>/Assets.xcassets/AppIcon.appiconset/AppIcon-Light.png
mv ../tmp/<app>-icon-dark.svg.png \
   <App>/Assets.xcassets/AppIcon.appiconset/AppIcon-Dark.png
mv ../tmp/<app>-icon-tinted.svg.png \
   <App>/Assets.xcassets/AppIcon.appiconset/AppIcon-Tinted.png

# 4. Verify dimensions + format.
file <App>/Assets.xcassets/AppIcon.appiconset/AppIcon-Light.png
# expected: PNG image data, 1024 x 1024, 8-bit/color RGBA, non-interlaced
sips -g pixelWidth -g pixelHeight <App>/Assets.xcassets/AppIcon.appiconset/AppIcon-Light.png
# expected: pixelWidth: 1024 / pixelHeight: 1024

# 5. Commit the SVG source-of-truth alongside, under docs/app-store/icons/.
mkdir -p docs/app-store/icons/<app>/
cp ../tmp/<app>-icon-light.svg  docs/app-store/icons/<app>/light.svg
cp ../tmp/<app>-icon-dark.svg   docs/app-store/icons/<app>/dark.svg
cp ../tmp/<app>-icon-tinted.svg docs/app-store/icons/<app>/tinted.svg
```

## Verify visually

Open the produced PNGs in Preview.app and confirm:

- Background fill reaches all 4 edges (no transparency at canvas border — Apple's compositor adds the squircle mask)
- Light variant uses paper `#FAF8F3` background
- Dark variant uses the project's dark/ink background color (a near-black defined in your design spec)
- Colors match the spec hex values byte-for-byte
- No anti-alias bleed from `<filter>` effects (rare with QuickLook, but inspect the highlight + spark ring areas)
- Both PNGs are 1024×1024 exactly (no off-by-one from QuickLook scaling)

If any check fails, the fix lives in the SVG, not in a post-process pass — re-edit, re-rasterize.

## Asset-catalog metadata

`AppIcon.appiconset/Contents.json` must reference both PNGs as universal idiom (no `"platform": "ios"`), so Apple auto-adapts the 1024 master across iOS + macOS:

```json
{
  "images" : [
    {
      "filename" : "AppIcon-Light.png",
      "idiom" : "universal",
      "size" : "1024x1024"
    },
    {
      "appearances" : [
        { "appearance" : "luminosity", "value" : "dark" }
      ],
      "filename" : "AppIcon-Dark.png",
      "idiom" : "universal",
      "size" : "1024x1024"
    }
  ],
  "info" : { "author" : "xcode", "version" : 1 }
}
```

Tinted entry present — `AppIcon-Tinted.png`, `appearance: luminosity / value: tinted`, universal idiom. No `AppIcon-macOS.appiconset/` (universal idiom covers macOS via auto-scale).

## Why qlmanage and not X

| Tool | Reason rejected |
|---|---|
| `rsvg-convert` (librsvg) | Requires Homebrew, not installed on this Mac |
| `inkscape --export-png` | Requires Homebrew or .app install |
| `imagemagick convert` | Requires Homebrew |
| `sips` | Does not read SVG input on macOS as of Sequoia |
| `cairosvg` (Python) | Requires Homebrew (Cairo system lib) |
| Pillow | No SVG support natively |
| Swift + WebKit CLI | Works but ~80 LOC of bespoke code for a one-step thumbnail render that `qlmanage` already does |
| Browser screenshot | Manual, unreproducible across machines |

`qlmanage` ships with macOS, takes one command, outputs the exact PNG shape Apple wants. The trade-off is that QuickLook's SVG generator may diverge slightly from full-spec SVG 1.1 — keep the SVG simple (flat shapes, no filters, no text) and the output is faithful.

## Companion skill

For the macOS size-ladder downscale workflow (now retired in favor of the universal single-PNG decision described above, but useful as a reference for older Xcode targets), adapt the `sips -Z` ladder shown in the "macOS ladder reality check" section above.
