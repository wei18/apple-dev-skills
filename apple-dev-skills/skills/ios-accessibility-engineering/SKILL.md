---
name: ios-accessibility-engineering
description: Concrete VoiceOver / Dynamic Type / touch-target / Reduce Motion implementation guide for SwiftUI and UIKit. Invoke when building or auditing any user-facing iOS/macOS UI, when asked "make this accessible", or before an App Review submission a11y pass.
---

# iOS Accessibility Engineering

## When to invoke

- Adding or modifying any user-facing View, screen, or interactive control.
- Running a pre-submission accessibility audit against App Store Review guidelines.
- User says "make this accessible", "check a11y", "VoiceOver doesn't read this", or "does this pass WCAG".
- Reviewing a PR that introduces new SwiftUI `View` or UIKit `UIView` / `UIViewController` code.

## VoiceOver: labelling and semantics

**Labels, values, and hints** are three distinct channels:

- `.accessibilityLabel("Done")` — the noun identifying the element. Keep it short; VoiceOver reads it first.
- `.accessibilityValue("3 of 9")` — the current state or quantity. Changes without re-reading the label.
- `.accessibilityHint("Double-tap to submit")` — what happens on activation. Users can turn hints off; never put essential info here.

In UIKit, set `accessibilityLabel`, `accessibilityValue`, and `accessibilityHint` on any `UIView`. In SwiftUI, use the `.accessibilityLabel(_:)`, `.accessibilityValue(_:)`, and `.accessibilityHint(_:)` modifiers.

**Traits** communicate the element's role and state. Common SwiftUI traits:

```swift
.accessibilityAddTraits(.isButton)     // tappable action
.accessibilityAddTraits(.isHeader)     // section heading — VoiceOver lets users jump by heading
.accessibilityAddTraits(.updatesFrequently)  // live score, timer — suppresses constant interruptions
.accessibilityAddTraits(.isSelected)   // toggle / tab selection state
```

**Grouping** — combine several sub-views into one focusable element so VoiceOver reads it as a single sentence:

```swift
HStack { thumbnail; title; subtitle }
    .accessibilityElement(children: .combine)
```

Use `.accessibilityElement(children: .ignore)` when the children are redundant and you supply a custom label on the container. Use `.accessibilityElement(children: .contain)` to keep individual children focusable inside a group (e.g. a toolbar).

**Hiding decorative content:**

```swift
Image("confetti-background")
    .accessibilityHidden(true)   // purely decorative; skip in VoiceOver rotor
```

Meaningful images need a label: `Image("trophy").accessibilityLabel("Achievement unlocked")`.

**Announcing dynamic changes** — when content updates in place without a navigation event:

```swift
AccessibilityNotification.Announcement("Level complete").post()
// or for a layout change:
AccessibilityNotification.LayoutChanged(element: focusTarget).post()
// or for a screen change (modal, full replacement):
AccessibilityNotification.ScreenChanged(element: focusTarget).post()
```

In UIKit: `UIAccessibility.post(notification: .announcement, argument: "Level complete")`.

## Dynamic Type

- Use `Font.body`, `.headline`, `.caption` etc. (text styles), or `UIFont.preferredFont(forTextStyle:)` in UIKit. Never hard-code `Font.system(size: 17)` without a text style.
- SwiftUI text styles scale automatically. If a control must cap scaling (compact digit grids, icon labels), apply `.dynamicTypeSize(...DynamicTypeSize.xLarge)` — this clamps only sizes above `.xLarge`; default `.large` stays byte-identical and snapshot baselines are unaffected.
- Test at AX5 (`accessibility-extra-extra-extra-large`) in Simulator: `xcrun simctl ui <udid> content_size accessibility-extra-extra-extra-large`.
- **`minimumScaleFactor` is width-only.** It shrinks glyphs that overflow horizontally; it does nothing for a glyph that overflows vertically. A digit at AX5 can be 50–60pt tall inside a 44pt cell — `minimumScaleFactor` never engages and the cell just clips blank. The fix is a size cap, not a scale factor.
- In `fullScreenCover` / `sheet` modals, `@Environment(\.dynamicTypeSize)` can return a stale value from the presenting context. Use geometry-driven layout (`ViewThatFits`) rather than an `if dynamicTypeSize.isAccessibilitySize` branch inside a modal.
- Avoid fixed `frame(height:)` on text containers; prefer `frame(minHeight:)` with unlimited vertical growth.

## Touch targets

- Apple HIG minimum: **44 × 44 pt**. A visually small button (e.g. a 20pt icon) passes if its hit region is padded to 44pt.
- `.contentShape(Rectangle())` enlarges the hit region for `.buttonStyle(.plain)` containers or custom `onTapGesture` views where Spacers don't automatically expand the hit area.
- Voice Control and Switch Control rely on `accessibilityLabel` to identify targets by name; if two same-named buttons exist on screen, add `.accessibilityInputLabels(["Submit order", "Submit"])` to disambiguate.

## Motion, transparency, and contrast

```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion
// Skip or replace animations when true:
withAnimation(reduceMotion ? nil : .easeInOut) { state.toggle() }
```

- `\.accessibilityReduceTransparency` — remove blur / frosted-glass effects when true; use an opaque fill instead. **SwiftUI `.background(.ultraThinMaterial)` does NOT automatically drop its blur when Reduce Transparency is on — you must branch on `\.accessibilityReduceTransparency` manually and substitute a solid background.**
- `\.accessibilityDifferentiateWithoutColor` — never rely on color alone to convey state; add an icon or label.
- `\.colorSchemeContrast` (`.increased`) — if you draw custom backgrounds, check this and raise contrast when set.

## Verification and testing

**Accessibility Inspector** (Xcode → Open Developer Tool → Accessibility Inspector): point the inspector at your app in Simulator, run the automated audit (the triangle icon), and fix every reported issue before submission. It surfaces missing labels, low-contrast text, small touch targets, and missing traits.

**Snapshot tests do not verify Dynamic Type or VoiceOver.** An `NSHostingView` in a headless test process has no live AX client; `accessibilityLabel` / `accessibilityChildren` traversal returns empty trees. Injecting `DynamicTypeSize.accessibility3` into an `NSHostingView` bypasses the modal env-propagation path, giving a false pass. Reliable verification requires a booted simulator with idb or `xcrun simctl`:

```bash
# Set content size to AX5 and screenshot
xcrun simctl ui <udid> content_size accessibility-extra-extra-extra-large
idb screenshot <udid> after-ax5.png
# Tap through the UI with VoiceOver via idb ui_tap / ui_describe_all
```

**CI a11y gate** — CVS Health's `a11y-audit` (open source, Swift-based) provides a programmatic audit runner that can fail CI on missing labels or contrast violations; treat it as a complementary gate, not a replacement for manual Accessibility Inspector review.

## WCAG 2.2 mapping for App Review

| WCAG criterion | What it requires | How it surfaces in iOS |
|---|---|---|
| 1.1.1 Non-text content | Meaningful images have text alternatives | `accessibilityLabel` on `Image` |
| 1.4.3 Contrast (minimum) | ≥ 4.5:1 for normal text, 3:1 for large text | Check in Accessibility Inspector |
| 1.4.4 Resize text | Text reflows up to 200% without loss of content | Dynamic Type + `ViewThatFits` |
| 2.5.8 Target size (Minimum) — **AA** | Interactive targets ≥ 24×24 CSS px (WCAG 2.2 new AA criterion) | `.contentShape` + padding; the **AA conformance gate** |
| 2.5.5 Target size — AAA | Interactive targets ≥ 44×44 CSS px (≈44pt on 1× devices) | Apple HIG minimum; stronger than AA — aim for this |

App Review does not formally audit against WCAG, but the Human Interface Guidelines cite these thresholds and reviewers reject apps that are obviously unusable with VoiceOver or at accessibility text sizes.

## Verification checklist

- All interactive controls have an `accessibilityLabel`; decorative images have `accessibilityHidden(true)`.
- Dynamic type tested at AX5 on a booted simulator — not only at default `.large`.
- No fixed `frame(height:)` on text containers; `minimumScaleFactor` is not used as a substitute for layout flexibility.
- Touch targets ≥ 44pt; `.contentShape` applied wherever Spacers or padding would otherwise shrink the hit region.
- `AccessibilityNotification` posted for in-place content changes.
- `accessibilityReduceMotion` checked before all non-trivial animations.
- Accessibility Inspector automated audit passes with zero errors.
- VoiceOver reading order verified manually (not inferred from visual order alone).

## Related skills

- `swiftui-interaction-footguns`: Dynamic Type / modal env footguns and the `minimumScaleFactor` pitfall in detail.
- `swift-testing-baseline`: headless AX-tree limitation and why sim verification is the reliable gate.

## External references

- [`dadederk/iOS-Accessibility-Agent-Skill`](https://github.com/dadederk/iOS-Accessibility-Agent-Skill)
  (Daniel Devesa Derksen-Staats, MIT) — a complementary, high-authority a11y skill. It goes
  deeper on **Large Content Viewer** (`UILargeContentViewerItem`), **`accessibilityRotor` /
  `accessibilityRepresentation` / `AccessibilityFocusState`**, **Full Keyboard Access**, and
  VoiceOver **custom actions** — areas this skill keeps brief. This skill's strength is the
  runtime-verification pitfalls (the `minimumScaleFactor` vertical-clip trap, headless-AX-tree
  false passes, idb/simctl sim-verify, WCAG 2.2 mapping). Use both.
