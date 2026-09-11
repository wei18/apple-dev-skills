---
name: telemetry-facade-pattern
description: Design the app-side event pipeline that fans one `telemetry.observe(event)` call out to logging, tracking, MetricKit and Game Center sinks. Use when deciding whether Logger and analytics tracking share one interface; when adding a `TelemetrySink` / `MetricKitSink` / `GameCenterSink`; when a wired-looking sink never fires (score not submitted, achievement not unlocked, `GKLeaderboard.submitScore` unreached); when sink order or UI-blocking sink I/O matters. Does NOT choose the Logger API (oslog-logger-defaults) or which analytics sources to use (apple-three-piece-analytics).
---

# Telemetry Facade Pattern

## When to invoke

- Starting a new project and designing the logger / tracker / metrics interface.
- About to introduce OSLog and any tracking / analytics at the same time.
- Wanting to preserve flexibility for "swap the tracking provider later".
- User asks "should Logger and Tracking be separate", "how should the event interface look".

## Default decisions

### A single `Telemetry` target

- Create one `Telemetry` target inside the SwiftPM Package.
- It contains:
  - `TelemetryEvent` value type (enum / struct, `Sendable`)
  - `TelemetrySink` protocol:
    ```swift
    public protocol TelemetrySink: Sendable {
        func receive(_ event: TelemetryEvent) async
    }
    ```
  - The main facade — choose the type per the table below. The facade fans out to multiple sinks.

    | Facade type | Use when | Cost |
    |---|---|---|
    | `actor Telemetry` (default) | any sink holds subscription identity (e.g. `MXMetricManagerSubscriber`) or does async I/O | `observe` is `async` |
    | `struct Telemetry: Sendable` | every sink is fully synchronous and stateless | no lifecycle owner for stateful sinks |
  - Default sinks (see below)

### Call sites describe only "what happened"

```swift
telemetry.observe(.sessionCompleted(id: sessionId, durationMs: 12_345))
```

- The call site **doesn't know** who will consume the event.
- Swapping providers / adding sinks only requires replacing a sink; call sites change nothing.

### Default sink set

| Sink | Receives | Purpose |
|---|---|---|
| `OSLogSink` | All events | Human-readable debug messages |
| `TrackingSink` (default `NoOpTrackingSink`) | Business events | v1 has no third-party tracking but the protocol is reserved; future swaps require zero call-site changes |
| `MetricKitSink` | iOS ≤ 26: subscribes via `MXMetricManager.shared.add(self)`; on receiving `MXMetricPayload`, broadcasts to other sinks. iOS 27+: `MXMetricManagerSubscriber` is deprecated — hold a single `MetricManager()` instance instead and `for await report in manager.metricReports` (don't create more than one instance; two concurrent iterators only split the sequence) | Performance / diagnostics persistence — on iOS ≤ 26, `MXMetricManagerSubscriber` inherits `NSObjectProtocol`, so `MetricKitSink` must be an `NSObject` subclass, not a struct or actor. An `NSObject` subclass *can* conform to a `Sendable` sink protocol, but only while every stored property is immutable — a `var` there fails with "stored property … is mutable". Hold subscription state behind `@MainActor` or a `Mutex`, or mark the class `@unchecked Sendable` and synchronise it yourself |
| `GameCenterSink` (games) | Completion / achievement events | Submit score / unlock achievement |

```swift
public struct NoOpTrackingSink: TelemetrySink {
    public init() {}
    public func receive(_ event: TelemetryEvent) async { /* intentionally empty */ }
}
```

### Composition root wiring

- The App target's DI composition root injects sinks into the facade.
- Sinks are **failure-isolated** (one sink throwing or timing out must not stop the others) but **not order-free**: the facade forwards in array order, and a sink that reads state another sink writes must come after it (see trap 2).

#### Wiring traps (hard-won — real project lessons)

A sink that *exists as a type* is worth **zero** until it is in the **live** sinks
array. Five traps, in the order they bit:

1. **Existing-but-unwired = dead code.** Real-world example: a `GameCenterSink`
   and its achievement-evaluation logic were fully written but never added to
   the live `Telemetry` sinks list (the composition root shipped
   `[OSLogSink, NoOpTrackingSink]` only) → no score, no achievement, silently.
   **Verify the composition root's actual sinks array**, not that the sink type
   compiles. `git log -S "GameCenterSink("` showing only the creation commit is
   the smoking gun.
2. **Sink ordering matters when one sink reads another's write.** The facade
   forwards in array order, so a sink that *writes* state another sink *reads*
   must come first — e.g. a persistence sink writes a counter (a completed-session
   count) **before** `GameCenterSink`'s evaluator reads it; reversed = an
   off-by-one where a count-based achievement fires one completion late. Make
   read/write sink order explicit and test it.
3. **I/O sinks on a gameplay-reachable path must not block.** Completion events
   are reached from the interactive path (e.g. an interactive input handler →
   a completion event → `telemetry.observe`). A sink doing CloudKit reads +
   GameKit network I/O synchronously there **freezes the UI**. Forward to such sinks on a
   **detached, order-preserving Task** (chain each on the previous so events
   still forward in order) and return immediately; keep the fast sinks
   (OSLog / NoOp) synchronous.
4. **Late-binding to break the construction cycle.** When a sink needs deps
   (persistence, GameCenter) that themselves need `Telemetry`, you cannot build
   it at Telemetry-construction time. Wire a `DeferredSink` placeholder into the
   facade at startup, then `setDownstream([real sinks])` once (sync, from the
   `@MainActor` composition root) after all deps are assembled. A `final class
   … : Sendable` (not an actor, and not `@unchecked`) backed by
   `Synchronization.Mutex<[any TelemetrySink]>` (iOS 18+ / macOS 15+) keeps
   `setDownstream` synchronous via `downstream.withLock { $0 = sinks }`;
   `receive` snapshots the sinks under `withLock` before any `await`.
5. **The sink firing ≠ the terminal call working.** Tracing "wire 2 things"
   uncovered a third gap: the GameKit terminal (`submitScore`/`reportAchievement`)
   was a stub that no-op'd / threw. **Trace to the actual platform call**
   (`GKLeaderboard.submitScore`, `GKAchievement.report`), not just to the sink.
   Terminal GameKit/StoreKit calls are device-gated — verify on a real device +
   sandbox, never claim "done" from a green headless suite.

## Rationale

- Decouples call sites from consumers: v1 can use `telemetry.observe(...)` with no external tracking, and a future TelemetryDeck / in-house pipeline only swaps the sink.
- OSLog + Tracking + MetricKit + GameCenter are all "event streams"; one unified interface is easier to maintain than four separate ones.
- Easy to test: inject a fake sink and assert on the event stream.

## Deviation considerations

- **Minimal App, OSLog only**: you can skip the `Telemetry` target and use `Logger` directly. But **if you anticipate adding tracking / metrics later**, building the facade up front pays off.
- **Need *routing* between sinks** (e.g. a MetricKit payload re-emitted into `TrackingSink`): handle routing inside the facade; call sites still unchanged.
- **Cross-platform** (Android / Linux): facade interface stays platform-neutral; sink implementations are per-platform.

## Verification checklist

- The `Telemetry` target is standalone; UI / Engine don't directly depend on anything beyond OSLog.
- `TelemetryEvent` is a value type, `Sendable`.
- A default `NoOpTrackingSink` is provided and wired in the composition root.
- Tests assert on event streams via fake sinks, not by parsing OSLog output.
- **The live composition root's sinks array actually contains every sink you
  intend to fire** (not just that the sink type exists) — the "existing-but-unwired" failure mode.
- Read/write-dependent sinks are ordered so writers precede readers, with a test
  pinning the order.
- I/O sinks on a gameplay-reachable completion path forward non-blocking; the
  interactive path is never frozen by a sink's CloudKit/GameKit work.
- The terminal platform call (GameKit/StoreKit) is reached and device-verified —
  not just the sink.

## Related skills

- `oslog-logger-defaults`: the concrete `OSLogSink` implementation dependency.
- `apple-three-piece-analytics`: each piece corresponds to one sink.
- `swiftpm-modularization`: why `Telemetry` is its own target.
