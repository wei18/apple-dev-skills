---
name: swiftui-state-and-composition
description: Best practices for structuring SwiftUI state, data flow, view composition, and render performance — @Observable vs ObservableObject migration, single-source-of-truth ownership, view identity, and render minimisation. Invoke when writing or refactoring SwiftUI views, choosing a state management approach, debugging view re-renders too often, deciding between @Observable and ObservableObject, or structuring a new screen.
---

# SwiftUI State & Composition

## When to invoke

- Writing or refactoring any SwiftUI `View`.
- Choosing between `@State`, `@Binding`, `@Observable`, `@StateObject`, `@ObservedObject`, or `@Environment`.
- Debugging a view that re-renders more than expected, or a state value that appears to reset unexpectedly.
- Extracting a large `body` into smaller components.
- Adding async data loading to a view.

## State ownership

### The single-source-of-truth rule

Every piece of mutable state lives in **exactly one place**. Views that need to read it receive a binding or observe the model directly; they never own a copy.

### `@State` — value-type, view-owned

Use for state that is **local and ephemeral**: expanded/collapsed bools, text field content, animation phase. SwiftUI initialises a `@State` variable exactly once (on the view's first appearance), even if the parent re-renders with a new proposed value. Pass write access down with `$binding`.

```swift
struct CounterView: View {
    @State private var count = 0
    var body: some View {
        Button("Tap \(count)") { count += 1 }
    }
}
```

### `@Binding` — delegated mutation

A `@Binding` is a reference into a parent's state. Use it when a child view needs to mutate state owned by its parent.

```swift
struct ToggleRow: View {
    @Binding var isOn: Bool   // owner is the parent; child just mutates
    var body: some View { Toggle("Enable", isOn: $isOn) }
}
```

Never store a `@Binding` in a class; it is a SwiftUI-managed reference that must not outlive a render pass.

### `@Observable` — the modern reference-type model (iOS 17+ / macOS 14+)

`@Observable` (Observation framework) replaces the `ObservableObject` / `@Published` / `@StateObject` / `@ObservedObject` stack:

| Old (iOS 16 and earlier) | New (iOS 17+) |
|---|---|
| `class VM: ObservableObject` | `@Observable class VM` |
| `@Published var x` | `var x` (no annotation needed) |
| `@StateObject var vm = VM()` | `@State var vm = VM()` |
| `@ObservedObject var vm: VM` | `let vm: VM` (or `@Bindable`) |

Key improvement: `@Observable` tracks **property-level access**. A view re-renders only when a property it actually _read_ changes. `ObservableObject` invalidates the entire view on any `@Published` change — even ones the view never read.

```swift
@Observable final class GameViewModel {
    var score = 0
    var isPaused = false
}

struct GameView: View {
    @State private var vm = GameViewModel()  // owned here
    var body: some View {
        ScoreDisplay(vm: vm)   // only re-renders when score changes
        PauseButton(vm: vm)    // only re-renders when isPaused changes
    }
}
```

**`@Bindable`** — when a child view needs a two-way binding into an `@Observable` model, redeclare with `@Bindable`:

```swift
struct NameEditor: View {
    @Bindable var vm: GameViewModel   // enables $vm.playerName bindings
    var body: some View { TextField("Name", text: $vm.playerName) }
}
```

Passing `vm` as `let vm: VM` silently breaks `TextField` / `Toggle` bindings — `@Bindable` is required.

**Older deployment targets**: fall back to `ObservableObject` + `@Published` + `@StateObject` / `@ObservedObject`. The concepts are the same; only the annotation syntax differs. Avoid mixing the two systems in the same module.

### `@Environment` — cross-cutting propagation

Use `@Environment` for values that many unrelated views need (theme, locale, feature flags, dependencies). Define a key; inject at the root; consume anywhere without threading through every initialiser.

```swift
extension EnvironmentValues {
    @Entry var theme: AppTheme = .default
}

// Inject at root
ContentView().environment(\.theme, liveTheme)

// Consume deep in the tree
struct HeaderView: View {
    @Environment(\.theme) var theme
}
```

Prefer constructor injection for logic-heavy dependencies and `@Environment` for cross-cutting concerns (see `swift-dependency-injection`).

## Lifting state up vs pushing it down

Lift state to the **lowest common ancestor** of all views that need it — no higher. Pushing it further up than necessary enlarges the invalidation scope (every child of that ancestor may re-render on change). Pushing it too low requires a `@Binding` chain that becomes brittle.

A simple test: if only one view reads and writes a value, keep it `@State` in that view. If two sibling views need it, lift to their parent. If many unrelated views need it, put it in an `@Observable` model injected via `@Environment`.

## View identity and lifecycle

SwiftUI distinguishes views by **structural identity** (position in the `body` tree) and **explicit identity** (the `.id()` modifier).

- `@State` is initialised **once per identity**. If the view's identity changes, SwiftUI destroys the old instance and creates a new one — resetting all `@State` back to initial values. This is a source of unexpected state loss.
- In `ForEach`, always supply a stable, unique `id`. Using the array index as the id causes every element's identity to shift on insertions or deletions, triggering state resets and animation glitches.

```swift
// Correct — stable Identifiable id
ForEach(items) { item in ItemRow(item: item) }

// Avoid — index-based id causes thrash on mutation
ForEach(0..<items.count, id: \.self) { i in ItemRow(item: items[i]) }
```

Use `.id(someValue)` to **force-reset** a view (recreate it from scratch) when an input changes fundamentally — for example, resetting an edit form when the user switches to a different record.

`if/else` branches give each branch a **distinct** structural identity. State, `.task` latches, and focus reset when switching branches. When identity preservation across a condition matters, use a single view with conditional modifiers instead.

## Composition: small views, small invalidation

Break large `body` implementations into smaller subviews. Benefits:

1. **Readability** — each view has a clear, named purpose.
2. **Performance** — SwiftUI's diff engine only re-evaluates the `body` of views whose inputs changed. A smaller view reads fewer properties and therefore re-renders less often.

Prefer passing values as parameters over `@Environment` when the child is tightly coupled to the parent — the explicit dependency is easier to reason about.

```swift
// Instead of one 200-line body, extract by responsibility:
struct GameScreen: View {
    @State private var vm = GameViewModel()
    var body: some View {
        VStack {
            ScoreHeader(score: vm.score)        // only re-renders on score change
            BoardGrid(cells: vm.cells)          // only re-renders on cells change
            ControlBar(isPaused: $vm.isPaused)  // only re-renders on isPaused change
        }
    }
}
```

Use `@ViewBuilder` to compose conditional content in helper functions while keeping the caller's `body` clean.

## Render performance

**What triggers a re-render**: a view's `body` is re-evaluated when any stored property it **read** during the previous render changes. With `@Observable` this is property-level; with `ObservableObject` it is object-level.

Practical rules:
- Read only the properties you need. Extract a focused subview instead of passing the entire model if the subview only needs two fields.
- Avoid expensive computations in `body` — derive them once in the model or use `let` constants before the view builder.
- Stable closures: a closure capturing `self` created inline in `body` creates a new value each render. Factor out methods or use `let` local bindings to stabilise them.
- For large, uniformly-typed lists, use `LazyVStack` or `LazyVGrid` — they create child views on demand rather than all at once. For heterogeneous or short lists, `VStack` has lower overhead.
- `EquatableView` / `.equatable()` lets SwiftUI skip re-rendering a view when its inputs are `Equatable` and unchanged. Apply it to expensive leaf views whose inputs rarely change.

## Data flow: unidirectional and async

Keep data flowing in one direction: model → view → user action → model update → view re-render. Avoid state scattered across multiple views that write to each other's bindings.

**Where async loading lives**: use `.task(id:)` keyed to the input that should trigger (re)loading. The task is cancelled and restarted when `id` changes.

```swift
struct ArticleView: View {
    let articleID: Article.ID
    @State private var article: Article?

    var body: some View {
        ArticleContent(article: article)
            .task(id: articleID) {
                article = await loader.fetch(articleID)
            }
    }
}
```

Avoid storing derived values that can be computed from other state — derive them in `body` or in a computed property on the model. Redundant stored state goes stale.

Avoid god-view-models that own all state for an entire screen hierarchy. Split by responsibility and inject (see `swift-dependency-injection`).

## Verification checklist

- Each `@State` property is private and local; it is not duplicated in a sibling or parent.
- `ForEach` uses a stable `Identifiable.id` or a unique key, not array indices.
- Children that mutate parent state receive a `@Binding`, not a copy.
- `@Observable` classes are owned via `@State` at the view that creates them; consumers use `let` or `@Bindable`.
- No expensive work (sorting, filtering, network calls) happens directly inside `body`.
- Async loads use `.task(id:)` keyed to their input; side-effect-free bootstraps use `.onAppear { Task { … } }` for iOS 16 compatibility (see note below).
- `LazyVStack` / `LazyVGrid` is used for lists with more than ~50 items.
- View hierarchy is decomposed so each subview reads only the properties it needs.

> **iOS 16 / `.task` note**: on iOS 16 with some Xcode 26 toolchains, `.task` lowering in arm64 device Release builds produces a linker error. Use `.onAppear { Task { … } }` for one-shot bootstraps on those targets.

## Related skills

- `swiftui-interaction-footguns` — the **bug/footgun checklist** companion to this skill: tap-target shrink, blank `fullScreenCover`, Dynamic Type modal failures, `.task` re-fire traps, and `NSHostingView` environment pitfalls. Run that checklist on every SwiftUI View review.
- `swift-dependency-injection` — how to inject services into view-models via constructor or `@Environment`, and why god-view-models are an anti-pattern.
- `swift6-concurrency` — `Sendable` requirements for models shared across actors; `@MainActor` isolation for view-models.
