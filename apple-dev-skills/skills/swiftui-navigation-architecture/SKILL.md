---
name: swiftui-navigation-architecture
description: Default navigation shape for SwiftUI Apps (iOS 18 / macOS 15, Swift 6) — value-based `NavigationStack(path:)` over a typed `Route` enum, one `@Observable @MainActor` Router injected via `.environment`, `navigationDestination(for:)` at the stack root (never inside a lazy container), sheets as a separate `Modal` enum, one `.onOpenURL` mapping deep links to `[Route]`, `NavigationSplitView` for iPad/Mac, per-tab paths owned by the router, `Codable` route restoration. Invoke when wiring a new App's navigation, adding deep links or state restoration, migrating off `NavigationView` / `NavigationLink(destination:)`, or asked "router / coordinator pattern in SwiftUI". Owns the architecture; individual interaction bugs → swiftui-interaction-footguns.
---

# SwiftUI Navigation Architecture

The default navigation shape for Apps on this catalog's baseline ([[apple-platform-targets]]: iOS 18 / macOS 15, Swift 6 language mode): navigation state is **data** — a typed route enum in one observable router — so flows are unit-testable (assert on `[Route]`), deep-linkable (URL → routes is a pure function), and restorable (routes are `Codable`).

## When to invoke

- Wiring navigation in a new App target, or adding a second entry point (deep link, widget tap, notification, tab)
- Adding deep links / universal links or state restoration to an existing App
- Migrating off `NavigationView` or view-payload `NavigationLink(destination:)`
- Asked "how do I do a router / coordinator in SwiftUI?"

## Scope

Owns container choice (Stack / SplitView / Tab), route modeling, the router object, deep-link funneling, and restoration. Does NOT own: known interaction bugs in nav components → [[swiftui-interaction-footguns]]; injecting the services destination views need → [[swift-dependency-injection]]; nav-chrome accessibility → [[ios-accessibility-engineering]].

## Pick the container

| App shape | Container |
|---|---|
| Single drill-down flow (iPhone-first) | `NavigationStack(path:)` |
| 2–5 top-level peer sections | `TabView` + one `NavigationStack` per tab, each with its own path |
| Source list → detail (iPad / Mac) | `NavigationSplitView`; sidebar selection is router state, the detail column hosts its own `NavigationStack` |

Never `NavigationView` in new code — deprecated since iOS 16.

## The default shape

```swift
enum Route: Hashable, Codable {
    case board(id: UUID)      // payloads are IDs, not model objects
    case settings
}

enum Modal: String, Identifiable {  // presentation is NOT navigation
    case paywall, onboarding
    var id: String { rawValue }
}

@Observable @MainActor
final class Router {
    var path: [Route] = []
    var modal: Modal?

    // One pure mapping: URL → navigation state. Unit-test without UI.
    func open(_ url: URL) {
        guard url.scheme == "myapp" else { return }
        switch url.host {
        case "board": path = [.board(id: UUID(uuidString: url.lastPathComponent) ?? UUID())]
        case "settings": path = [.settings]
        default: break
        }
    }
}

@main struct MyApp: App {
    @State private var router = Router()

    var body: some Scene {
        WindowGroup {
            NavigationStack(path: $router.path) {
                HomeView()
                    .navigationDestination(for: Route.self) { route in
                        switch route {                 // exhaustive — compiler catches new routes
                        case .board(let id): BoardView(id: id)
                        case .settings: SettingsView()
                        }
                    }
            }
            .environment(router)
            .sheet(item: $router.modal) { ModalHost($0) }
            .onOpenURL { router.open($0) }
        }
    }
}
```

Rules the shape encodes:

- **Push with values** — `NavigationLink(value:)` or `router.path.append(...)`; never `NavigationLink(destination:)` in a path-managed stack (those pushes bypass `path`, desyncing back-stack, deep links, and restoration).
- **`navigationDestination(for:)` on the stack's root content, outside lazy containers.** Apple's docs: "Do not put a navigation destination modifier inside a 'lazy' container, like `List` or `LazyVStack`. … Add the navigation destination modifier outside these containers so that the navigation stack can always see the destination."
- **Typed `[Route]` over `NavigationPath`** — pattern-matchable, exhaustively switched, `Codable` for free.
- **Modal ≠ push** — sheets / fullScreenCover hang off `router.modal`; a presented flow is never a `Route` case.
- **Router is `@MainActor`** (it is UI state; Swift 6 enforces it), routes are `Hashable + Codable` value types.

## Deep links & restoration

- Every URL entry point (`onOpenURL`, universal links, `NSUserActivity`, notification taps) funnels into `router.open(_:)` at the scene root — one handler, one mapping function, unit tests assert `URL → [Route]` directly.
- Restoration: on `scenePhase == .background`, `JSONEncoder` the `[Route]` into `@SceneStorage`(a `String` slot); on launch, decode and assign. Routes that reference store objects carry IDs — resolve at display time and drop routes that no longer resolve instead of crashing.

## Multi-column & tabs

- `NavigationSplitView`: sidebar selection lives in the router; only the detail column hosts a `NavigationStack`. Don't nest stacks in the sidebar.
- `TabView`: the router owns `selectedTab` *and* one path per tab — paths kept in per-view `@State` reset whenever tab identity churns. Selecting the already-active tab popping to root becomes a 2-line router method.
- iPad / Mac footguns in these containers (sizeClass on Mac, inert sidebar Labels) → [[swiftui-interaction-footguns]].

## Rationale

- **Navigation state as data**: view-payload links hide "where is the user" inside the view tree; a typed path makes it assertable, loggable, and reproducible from a URL or a saved session.
- **One router in `.environment`**: a single owner instead of bindings threaded through N view layers; `@Observable` keeps invalidation scoped to views that actually read `path`.
- **Typed enum over `NavigationPath`**: exhaustive `switch` in `navigationDestination` means the compiler flags every unhandled route; `NavigationPath` trades that away for type erasure most single-module apps don't need.

## Deviation considerations

- **Heterogeneous route types across feature packages** that genuinely can't share one enum → `NavigationPath` + its `CodableRepresentation` for restoration; you give up exhaustive matching.
- **A 2-screen utility** → a bare `NavigationStack` without router or path is fine; adopt the shape when the second entry point appears, not speculatively.
- **UIKit-hosted hybrids** (heavy `UIViewController` interop) → keep coordination at the UIKit layer; don't force a SwiftUI router across the hosting bridge.
- **iOS 17 floor** → the shape works unchanged (`@Observable`, `NavigationStack` both available); below that, `ObservableObject` replaces `@Observable`.

## Common Mistakes

1. **`NavigationView` in new code** — deprecated since iOS 16, unpredictable column behavior. Use `NavigationStack` / `NavigationSplitView`.
2. **`navigationDestination(for:)` inside `List` / `LazyVStack`** — the lazy container may not have created the registering view yet, so pushes silently fail (runtime console warning). Register at the stack root.
3. **Mixing `NavigationLink(destination:)` into a path-based stack** — pushes invisible to `path`; back-stack count, deep links, and restoration all desync.
4. **Sheets modeled as pushed routes** — back-button vs dismiss semantics conflict; keep a separate `Modal` enum.
5. **Per-tab paths in view `@State`** — switching tabs (or any identity churn) resets the stack; paths belong to the router.
6. **`onOpenURL` sprinkled across views** — multiple competing handlers; one scene-root handler feeding one mapping function.
7. **Router not `@MainActor`** — Swift 6 isolation errors the first time a `Task` mutates `path`; annotate the class, not call sites.
8. **Model objects as route payloads** — bloats `Hashable`/`Codable`, goes stale after edits; carry IDs and resolve at display.

## Review Checklist

- [ ] No `NavigationView`; no `NavigationLink(destination:)` inside path-managed stacks
- [ ] One `Route` enum, `Hashable + Codable`; payloads are IDs, not model objects
- [ ] `navigationDestination(for:)` registered at the stack root, outside lazy containers
- [ ] Single `@Observable @MainActor` router in `.environment`; all paths (incl. per-tab) live on it
- [ ] Sheets / covers driven by a `Modal` enum, never a `Route` case
- [ ] One `.onOpenURL` at the scene root; `URL → [Route]` mapping has unit tests
- [ ] Restoration decodes saved routes and drops unresolvable IDs gracefully
- [ ] SplitView: sidebar selection in router, stack only in detail; footguns checklist run

## Related skills

- [[swiftui-interaction-footguns]] — known bugs in the nav components this skill wires together
- [[swift-dependency-injection]] — how destination views get their services
- [[apple-platform-targets]] — the iOS 18 / macOS 15 baseline this shape assumes
- [[ios-accessibility-engineering]] — accessibility of the navigation chrome
