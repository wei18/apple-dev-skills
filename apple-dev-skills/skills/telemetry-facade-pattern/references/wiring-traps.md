# Wiring Traps

#### Wiring traps (hard-won — real project lessons)

A sink that *exists as a type* is worth **zero** until it is in the **live** sinks
array. Six traps, in the order they bit:

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
6. **`MetricKitSink`'s base class depends on the OS version.** On OS 26 and
   earlier, `MXMetricManagerSubscriber` inherits `NSObjectProtocol`, so
   `MetricKitSink` must inherit `NSObject`, not be a struct — subscribe via
   `MXMetricManager.shared.add(self)`; on receiving `MXMetricPayload`, broadcast
   to other sinks. On OS 27+ (iOS, iPadOS, macOS, visionOS, Mac Catalyst),
   `MXMetricManager` / `MXMetricManagerSubscriber` are deprecated — hold a
   single `MetricManager()` instance instead and `for await report in
   manager.metricReports` (don't create more than one instance; two concurrent
   iterators only split the sequence). First choice for mutable subscription
   state on either OS: `actor MetricKitSink: NSObject` with a `nonisolated func
   didReceive` (matches the default `actor Telemetry` facade). A `final class`
   `NSObject` subclass *can* conform to a `Sendable` sink protocol, but only
   while every stored property is immutable — a `var` there fails with "stored
   property … is mutable"; hold that state behind `@MainActor` or a `Mutex`, or
   mark the class `@unchecked Sendable` and synchronise it yourself.
