# Wiring Traps

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
