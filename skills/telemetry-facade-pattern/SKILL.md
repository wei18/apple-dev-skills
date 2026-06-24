---
name: telemetry-facade-pattern
description: Single `Telemetry` SwiftPM target with a fan-out facade — callers say "what happened" (`telemetry.observe(event)`), facade dispatches to multiple sinks (OSLog / NoOp tracking / MetricKit / Game Center). Invoke when starting a new project that will log + track, deciding logger / tracker coupling, designing telemetry interfaces, or when asked "should Logger and Tracking be one thing".
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
  - `TelemetrySink` protocol
  - The main facade — default to a `Telemetry` **actor**. Sink stateful subscriptions (e.g. `MetricKitSink` holding `MXMetricManagerSubscriber` reference identity) require an actor for clean lifecycle management. A `Sendable` struct facade is acceptable only when every sink is fully synchronous and stateless. The facade fans out to multiple sinks.
  - Default sinks (see below)

### Call sites describe only "what happened"

```swift
telemetry.observe(.puzzleCompleted(id: puzzleId, durationMs: 12_345))
```

- The call site **doesn't know** who will consume the event.
- Swapping providers / adding sinks only requires replacing a sink; call sites change nothing.

### Default sink set

| Sink | Receives | Purpose |
|---|---|---|
| `OSLogSink` | All events | Human-readable debug messages |
| `TrackingSink` (default `NoOpTrackingSink`) | Business events | v1 has no third-party tracking but the protocol is reserved; future swaps require zero call-site changes |
| `MetricKitSink` | Subscribes via `MXMetricManager.shared.add(self)`; on receiving `MXMetricPayload`, broadcasts to other sinks | Performance / diagnostics persistence |
| `GameCenterSink` (games) | Completion / achievement events | Submit score / unlock achievement |

```swift
public struct NoOpTrackingSink: TelemetrySink {
    public init() {}
    public func receive(_ event: TelemetryEvent) { /* intentionally empty */ }
}
```

### Composition root wiring

- The App target's DI composition root injects sinks into the facade.
- Sinks are **independent**; one sink's failure does not affect the others.

#### Wiring traps (hard-won — real project lessons)

A sink that *exists as a type* is worth **zero** until it is in the **live** sinks
array. Four traps, in the order they bit:

1. **Existing-but-unwired = dead code.** Real-world example: a `GameCenterSink`/`AchievementEvaluator`
   were fully written but never added to the live `Telemetry` sinks list
   (the composition root shipped `[OSLogSink, NoOpTrackingSink]` only) → no score, no
   achievement, silently. **Verify the composition root's actual sinks array**,
   not that the sink type compiles. `git log -S "GameCenterSink("` showing only
   the creation commit is the smoking gun.
2. **Sink ordering matters when one sink reads another's write.** The facade
   forwards in array order, so a sink that *writes* state another sink *reads*
   must come first — e.g. `PersonalRecordSink` writes `completedCount` **before**
   `GameCenterSink`'s evaluator reads it; reversed = an off-by-one where the
   count achievement fires one completion late. Make read/write sink order
   explicit and test it.
3. **I/O sinks on a gameplay-reachable path must not block.** Completion events
   are reached from the interactive path (e.g. `placeMove → sessionCompleted →
   telemetry.observe`). A sink doing CloudKit reads + GameKit network I/O
   synchronously there **freezes the UI**. Forward to such sinks on a
   **detached, order-preserving Task** (chain each on the previous so events
   still forward in order) and return immediately; keep the fast sinks
   (OSLog / NoOp) synchronous.
4. **Late-binding to break the construction cycle.** When a sink needs deps
   (persistence, GameCenter) that themselves need `Telemetry`, you cannot build
   it at Telemetry-construction time. Wire a `DeferredSink` placeholder into the
   facade at startup, then `setDownstream([real sinks])` once (sync, from the
   `@MainActor` composition root) after all deps are assembled. `final class
   @unchecked Sendable` + `NSLock` (not an actor) keeps `setDownstream`
   synchronous; `receive` snapshots state under the lock before any `await`.
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
- **Need inter-sink dependencies** (e.g. `MetricKitSink` payloads must go through `TrackingSink` first): handle routing inside the facade; call sites still unchanged.
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
