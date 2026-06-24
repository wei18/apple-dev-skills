---
name: swiftui-interaction-footguns
description: Checklist of known SwiftUI interaction bugs that slipped past pure-code review (tap-target shrink, sidebar inert Labels, sizeClass on Mac, .task re-fire, theme tint propagation, NSHostingView env). Invoke automatically during Code Reviewer dispatch on any `.swift` file under your UI target (e.g. `Sources/.../AppUI/`) or any file matching `*View*.swift`, and whenever reviewing new SwiftUI View components, Button / NavigationLink / TabView / Form, or Mac NavigationSplitView variants.
---

# SwiftUI Interaction Footguns

A class of bugs that look fine in code but break at runtime. These have shipped to production from real projects (see Sightings section). Sweep this checklist on every SwiftUI View review.

## When to invoke

- Reviewing any new or modified SwiftUI View
- Reviewing `Button` / `NavigationLink` / `TabView` / `Form` / `Menu`
- Reviewing Mac variants (`NavigationSplitView` / sidebar)
- After a macOS or iPad smoke test surfaces a tap or navigation bug
- Before declaring a Phase complete that ships new View code

## Checklist

### Tap target & hit-test

- `Button { } label: { LayoutWithSpacer }` `.buttonStyle(.plain)` → hit-test shrinks to drawn content; the Spacer-expanded area is **not** tappable. **Fix:** `.contentShape(Rectangle())` on the label's outermost container.
- Same trap for `NavigationLink`, `Menu`, and any custom interactive view with `.onTapGesture` + Spacer / `frame(maxWidth: .infinity)` / padding.
- Padding and `frame(maxWidth: .infinity)` enlarge the visual frame but do **not** automatically enlarge the hit region under `.plain`. When in doubt, add `.contentShape`.

### NavigationSplitView (Mac / iPad)

- Sidebar items must be `NavigationLink(value:)` or `Button` — a bare `Label` is non-interactive even if it visually looks like a row.
- iPhone compact size class should fall back to `NavigationStack`, not split. Snapshot tests for iPhone fixtures must force `.compact` (see next item).
- Selection binding pitfall: sidebar selection and detail's path must share the same source of truth, or selection won't navigate.

### `horizontalSizeClass` on Mac

- `@Environment(\.horizontalSizeClass)` returns `.regular` for every macOS-hosted SwiftUI view — even iPhone-shaped fixtures inside `NSHostingView`. iPhone snapshot tests must inject `.compact` explicitly via `.environment(\.horizontalSizeClass, .compact)`.

### Async state load timing

- `.task { await viewModel.bootstrap() }` re-fires on every view mount / identity change. If a test pre-seeds VM state, the task overwrites it back to `.loading`. **Fix:** `hasBootstrapped` latch in the VM + a separate `retry()` method for user-driven retry.
- `.task(id:)` cancels and restarts when `id` changes — confirm that's the intent.

### Dynamic Type / AX3–AX5

- **Do NOT gate layout on `@Environment(\.dynamicTypeSize)` inside a `fullScreenCover` / `sheet` modal.** The env value can read a **stale `.large`** there even while the Text views actually scale via UIFont metrics — so a `dynamicTypeSize.isAccessibilitySize ? VStack : HStack` reflow **never fires** and labels still clip off-screen (negative-x frame). (Proved in a real project: a game board presented in a modal; cells/labels enlarged but the gate read `.large`.) Use a **geometry-driven** layout instead — `ViewThatFits(in: .horizontal) { HStack; VStack }` picks the row/column from the *actual offered width*, no env read.
- **`minimumScaleFactor` is WIDTH-driven** — it shrinks text too WIDE for its frame. It does **not** rescue a glyph that overflows **vertically**. A single digit "5" at AX5 is ~50–60pt tall in a 44pt pill → clipped top/bottom to a **blank** pill; `minimumScaleFactor` never engages and `.frame(maxHeight:)` alone just clips it.
- **Fix for compact fixed-size controls** (digit pad, board chrome/header) that must stay legible without honoring full AX scaling: **cap the Dynamic Type** — `.dynamicTypeSize(...DynamicTypeSize.xLarge)`. The cap clamps only sizes ABOVE `.xLarge`, so default `.large` rendering — and committed snapshot baselines — stay **byte-identical**; surrounding content (e.g. 9×9 board cells) keeps scaling. Standard compact-numeric-control approach; geometry/UIFont-driven, so a modal's stale env can't defeat it.
- **Snapshot tests do NOT prove a Dynamic Type fix.** A snapshot that injects `DynamicTypeSize.accessibility3` into an `NSHostingView` bypasses the modal env-propagation path and gives a **false pass** (real example: three rounds passed snapshots, all failed on device). **idb-sim-verify AX4 AND AX5 on a booted sim** (`simctl ui <udid> content_size accessibility-extra-extra-large` / `…-extra-extra-extra-large`), eyeball the screenshot — don't trust the injected-env snapshot. Size map: AX1=`accessibility-medium`, AX2=`accessibility-large`, AX3=`accessibility-extra-large`, AX4=`accessibility-extra-extra-large`, AX5=`accessibility-extra-extra-extra-large`.
- Keep grids and critical regions fixed-metric (e.g. 9×9 board uses fixed cell metrics); let body/label text scale.

### Theme propagation to SwiftUI system controls

- `Picker`, `Button(.borderedProminent)`, `ProgressView`, `Toggle`, `Stepper` etc. follow `.tint` / `.accentColor`. The project's `theme.accent.primary` does **not** auto-propagate — apply `.tint(theme.accent.primary.resolved)` on each system control or at a high-enough ancestor.

### `NSHostingView` snapshot environment

- `colorScheme` override needs `host.appearance = NSAppearance(named: ...)` on macOS — SwiftUI's `.preferredColorScheme` does not propagate through `NSHostingView`.
- `locale` and `horizontalSizeClass` overrides must be set on the View **before** wrapping in `NSHostingView`; mutating after host creation is unreliable.

### Button / Picker styling

- `.labelsHidden()` on `Picker` when the label is provided externally (avoids duplicated label rendering on Mac).
- `.buttonStyle(.borderedProminent)` honours `.tint` from **iOS 15+ / macOS 12+**; both APIs were introduced together in SwiftUI 3.

### Touch target minimums

- Apple HIG: 44×44pt minimum. Buttons that look smaller due to compact text + tight padding fail accessibility audit even if visually balanced.

### View identity & `if/else`

- Branching between `if A { ViewA } else { ViewB }` gives the two branches distinct identities; state (`@State`, `.task` latches, focus) resets on switch. Use a single view with conditional modifiers when identity preservation matters.

### Sheet / fullScreenCover presentation vs data race

- `fullScreenCover(isPresented: $bool)` / `sheet(isPresented:)` driven by a **separate** optional `@State` for the content, set back-to-back (`data = x; isPresented = true`), races: the cover presents from the Bool before the optional propagates into the content closure, so `if let data { … }` renders the **empty branch** → a **blank cover**. Looks correct in code; only a runtime drive (not snapshots, not unit tests) catches it. **Fix:** make the payload `Identifiable` and use `fullScreenCover(item: $data) { data in … }` — presentation and data are then atomic. (`@MainActor` payload → mark `id` `nonisolated`.)

### `@Observable` + `@Bindable`

- Reading an `@Observable` model via `let vm = …` does not establish a binding scope; passing `vm` into a child that needs `@Bindable var vm` requires the child to redeclare with `@Bindable`. Forgetting this silently breaks two-way bindings (TextField, Toggle).
- **Swift 6 mode:** `@Observable` view-models accessed from a View `body` must themselves be `@MainActor`-isolated (or all accessed properties must be `nonisolated`). A non-isolated `@Observable` class causes "Sending 'X' risks causing data races" because `View.body` is `@MainActor`-isolated. **Fix:** annotate the view-model class with `@MainActor`.

### View-model built inside a `navigationDestination` / factory closure

- A view-model constructed **inline inside the `.navigationDestination(for:)` closure** (or a `RouteFactory.view(for:)` that the destination calls) and stored as `@Bindable` is **re-minted on every destination re-render** — any parent re-render (e.g. an ad banner WebView finishing its load) gives the view a **fresh `.idle` instance**, and because the view keeps the same SwiftUI identity its `.task { bootstrap() }` does **NOT re-fire**, so it's stuck loading forever while the original (already-`.loaded`) instance is orphaned. Symptom: a screen stuck on its spinner even though the VM reached `.loaded` (confirm by logging `ObjectIdentifier(self)` in `bootstrap()` vs `ObjectIdentifier(viewModel)` in `body` — a vmid mismatch = orphaned VM). (Real-world example: same class of bug appears as "transient VM loses state" in multiple forms.) **Fix:** the destination view must **own** the VM via `@State` (first-value-wins: `_viewModel = State(wrappedValue: viewModel)`), so SwiftUI retains the first instance across destination re-invocations. Never `@Bindable` for a factory-built destination VM. This is a runtime-only bug — only an idb drive (often with network/ads active) catches it; offline it stays hidden.

## How to apply

1. Before approving any PR touching SwiftUI Views, sweep the checklist mentally.
2. For each item that *could* apply, grep / re-read the diff for the trigger pattern.
3. If a footgun is present, flag it with a concrete fix (cite the bullet).

## Sightings (real bugs that shipped past review)

- **Tap-target shrink** — A home screen mode card used `Button { } label: { card-with-Spacer }` with `.buttonStyle(.plain)`, shrinking the tap target to drawn content only. Caught by macOS smoke test, **not** by Code Reviewer. Fix: `.contentShape(Rectangle())`.
- **Inert sidebar Labels** — Mac `NavigationSplitView` sidebar items were bare `Label`s with no `NavigationLink` / `Button`, so clicking did nothing. Same review-blind-spot path.
- **Blank `fullScreenCover`** — A near-win hook presented a **blank** `fullScreenCover`: `fullScreenCover(isPresented: $bool)` + a separate optional `@State` for content, set back-to-back, raced → content closure's `if let` rendered the empty branch (a11y tree = 1 element vs 99 for a real board). Dual-model CR + unit tests passed; only the idb interactive audit caught it. Fix: `fullScreenCover(item:)` with an `Identifiable` payload.
- (Future: append as more are caught.)

## Related skills

- `subagent-review-cycles` — Code Reviewer dispatch brief should explicitly name this skill when reviewing SwiftUI Views.
- `swiftui-expert-skill` — broader domain skill (Instruments traces, hang/hitch profiling); different scope.
