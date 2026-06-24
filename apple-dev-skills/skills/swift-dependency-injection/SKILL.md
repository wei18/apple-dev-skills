---
name: swift-dependency-injection
description: Testable seam design via protocol injection, SwiftUI environment, and task-local overrides; Swift 6 Sendable rules for dependencies; mentions pointfreeco/swift-dependencies and Factory as library options. Invoke when designing a new service seam, asking "how do I inject CloudKit/network/clock", setting up a composition root, or making code testable.
---

# Swift Dependency Injection

## When to invoke

- Designing a new service boundary (CloudKit, networking, clock, RNG, notifications).
- Asking "how do I make this testable", "how do I inject X", or "should I use a singleton here".
- Establishing a composition root for a new app target or module.
- Reviewing code that reaches out to global state, `URLSession.shared`, `Date()`, or `UUID()`.
- Choosing between constructor injection and SwiftUI environment injection.

## Core principle: one composition root

All concrete implementations are wired in a single place — typically `makeApp(...)` or a `DependencyContainer` struct built in the `@main` entry point. Every layer below receives its dependencies through initialiser parameters, not by reaching up to a global. This makes the entire wiring visible in one screen of code and means tests can substitute any dependency without touching production paths.

```swift
// App entry point — the only place that knows about live implementations
@main struct MyApp: App {
    let root = makeApp()  // returns a pure value/struct carrying live deps
    var body: some Scene { ... }
}

func makeApp() -> AppRoot {
    AppRoot(
        storage: LiveStorage(),
        clock: ContinuousClock(),
        rng: SystemRandomNumberGenerator()
    )
}
```

No layer below `makeApp` imports `LiveStorage` or any other concrete type.

## Protocol-witness vs protocol-existential

Both are idiomatic Swift; the choice is a matter of callsite ergonomics:

- **Protocol existential (`any ServiceProtocol`)**: clear intent, straightforward generics. Works well for most app-layer seams. Requires the protocol to be `Sendable` if passed across actors.
- **Struct protocol witness (`struct ServiceClient { var fetch: @Sendable () async throws -> [Item] }`)**: eliminates dynamic dispatch, composes without `any`, easier to construct partial fakes. Favoured by pointfreeco/swift-dependencies. Good when a service has a small, stable API surface.

Either is fine. Pick the one that reads naturally; don't mix both styles for the same seam.

## SwiftUI environment injection

SwiftUI's `@Environment` and `EnvironmentValues` let you propagate dependencies down a view tree without threading them through every intermediate View:

```swift
// Define a key
struct StorageKey: EnvironmentKey {
    static let defaultValue: any StorageProtocol = NoopStorage()
}
extension EnvironmentValues {
    var storage: any StorageProtocol {
        get { self[StorageKey.self] }
        set { self[StorageKey.self] = newValue }
    }
}

// Inject at the root
ContentView()
    .environment(\.storage, LiveStorage())

// Consume deep in the tree — no init threading required
struct DetailView: View {
    @Environment(\.storage) var storage
}
```

**Trade-off vs constructor injection**: environment injection reduces boilerplate for deeply nested trees but makes the dependency implicit — a reader of `DetailView` must look up the environment key to understand what it needs. Constructor injection is explicit and compiler-enforced. For logic-heavy types (view-models, service objects), prefer constructor injection; reserve environment for cross-cutting concerns (theme, locale, feature flags, testable clocks).

In tests, inject the test double the same way:

```swift
DetailView()
    .environment(\.storage, FakeStorage())
```

## Test doubles: fakes over mocks

Prefer **fakes** (lightweight in-memory implementations) and **stubs** (hardcoded return values) over mock frameworks. Mocks couple tests to implementation details (call order, argument matching); fakes couple tests only to the contract.

```swift
struct FakeStorage: StorageProtocol {
    var items: [Item] = []
    func save(_ item: Item) async throws { items.append(item) }
    func loadAll() async throws -> [Item] { items }
}
```

**Injecting a controllable clock** eliminates time-dependent flakiness:

```swift
// Production
let clock: any Clock<Duration> = ContinuousClock()

// Test
let clock = TestClock<Duration>()  // advance manually
await clock.advance(by: .seconds(5))
```

**Injecting a seeded RNG** makes random behaviour deterministic:

```swift
// SplitMix64 or any var rng: RandomNumberGenerator
var rng: any RandomNumberGenerator = SystemRandomNumberGenerator()
// In tests:
var rng: any RandomNumberGenerator = SeededGenerator(seed: 42)
```

## `@TaskLocal` overrides

`@TaskLocal` is a lightweight alternative when you need to override a dependency for the duration of an async call tree without restructuring the call sites — useful for request-scoped values like loggers, trace IDs, or feature-flag snapshots:

```swift
enum Current {
    @TaskLocal static var clock: any Clock<Duration> = ContinuousClock()
}

// In test
await Current.$clock.withValue(TestClock()) {
    await systemUnderTest.run()
}
```

Avoid `@TaskLocal` for dependencies that should be visible in the public interface of a type; reserve it for cross-cutting infrastructure that every caller in the task tree shares implicitly.

## Swift 6 concurrency rules for dependencies

- Any type passed across actor boundaries — including a dependency — must conform to `Sendable`.
- Protocol requirements that are called from concurrent contexts must be `async` (or the protocol itself must be `@MainActor`-isolated).
- Closures stored in a struct client must be `@Sendable`:

```swift
struct AnalyticsClient: Sendable {
    var track: @Sendable (Event) async -> Void
}
```

- Avoid global `var` singletons with mutable state; they require either an `actor` wrapper or `@unchecked Sendable` with manual synchronisation. Neither is free.
- For third-party dependencies that predate Swift 6 strict concurrency, use `@preconcurrency import ThirdPartyKit` at the import site to suppress errors during transition; file an issue or switch packages if the lag is long-lived.

## Library options

- **`pointfreeco/swift-dependencies`** (MIT) — implements the struct-witness / environment / `@TaskLocal` pattern described above with a macro-driven `@Dependency` property wrapper. Provides `withDependencies { ... }` for scoped test overrides. Worth adopting when the team wants a shared convention rather than hand-rolling keys.
- **Factory** (MIT, by Michael Long) — registration-based container closer to traditional IoC. Useful when the codebase already organises dependencies as registered services rather than value-type structs.

Both are valid; they solve the same problem with different ergonomics. Evaluate against the existing codebase shape before adding a new dependency.

## Verification checklist

- No layer below the composition root imports a concrete implementation type (`Live*`, `URLSession.shared`, `Date()`, `UUID()`).
- All protocol types (or struct clients) used across actor boundaries declare `Sendable`.
- Async protocol requirements are `async throws`; synchronous fakes return immediately (no `Task.sleep` in a fake).
- Each test constructs its own fake/stub — no shared mutable test state at module level.
- The composition root (`makeApp(...)`) is the only call site that knows about live implementations.
- A controllable clock / seeded RNG is injected wherever production code calls `Date()`, `UUID()`, or `random(in:)`.

## Related skills

- `swiftpm-modularization`: put each seam (protocol + fake) in its own target so test targets can import the fake without importing the live implementation.
- `swift6-concurrency`: `Sendable` requirements, `@preconcurrency`, and actor-isolated types that affect dependency design.
- `swift-testing-baseline`: shared fake targets (`<Module>Testing`), protocol injection for CloudKit / Game Center, and why integration tests never touch real networks.
