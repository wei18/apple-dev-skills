---
name: swift-testing-baseline
description: Default testing stack for new Apple-platform Swift projects — swift-testing (no XCTest), pointfreeco/swift-snapshot-testing, protocol-injected fakes for CloudKit / Game Center / network, snapshot images committed to git, CI Xcode version locked to local. Invoke when starting a new project, writing the first test target, choosing a snapshot framework, deciding CloudKit / GameKit test strategy, or when asked "which test framework".
---

# Swift Testing Baseline

## When to invoke

- Starting a new project and choosing a test framework.
- Writing the first test target / first `@Test` case.
- Introducing CloudKit / GameKit / any network service and deciding whether to run integration tests on CI.
- Setting up SwiftUI snapshot testing.
- User asks "XCTest or swift-testing", "how do I do snapshots", "should CI connect to iCloud".

## Default decisions

### Framework

- **`swift-testing`** (Apple's official framework) for unit / integration tests; **do not use XCTest at all**.
- With no legacy code, the switch is zero-cost; swift-testing pairs well with Swift 6 / async.
- Name files by the type under test (`<Type>Tests.swift`) and group related cases with `@Suite`.

### Snapshot testing

- **`pointfreeco/swift-snapshot-testing`**, using its swift-testing-compatible `assertSnapshot`.
- **Snapshot images go into git** (default `__Snapshots__/` next to the test file) so visual diffs show up in PR review.
- Start by covering **the main screens** and expand from there. Each snapshot should cover multiple locales, iPhone / Mac, light / dark, and typical states.

#### Snapshot gate strategy — strict content / tolerant board (a settled design decision, not a global knob)

Tolerance is **per-suite by view type**, not a global knob:

- **Content suites** (Completion / DailyHub / Home / Settings — text, cards,
  badges) use the **default strict `.image`** (precision 1.0). Bit-exact is the
  point: adding any visible element (a new label/badge) changes pixels and
  **fails without a re-record** → the gate catches unintended UI drift. This is
  the only reliable "a new label appeared" gate (see dead end below).
- **AA-heavy board/grid suites** (`*Board*`, terminal overlays) keep a
  **`.tolerantImage`** (≈0.95 precision, defined once in each app's
  `SnapshotConfig.swift` as a project-local extension — `.tolerantImage` is NOT a
  built-in pointfreeco/swift-snapshot-testing strategy; the library ships
  `.image(precision:)` / `.image(perceptualPrecision:)`) — strict false-fails on dozens of antialiased cells.
  Choose strategy at the call site via `as: .image` vs `as: .tolerantImage`;
  **never sprinkle ad-hoc `precision:` overrides** at call sites.
- **Baselines are the source of truth.** A suite failing on PNGs means *behavior
  changed* → STOP and investigate; do **not** re-record to make it pass. Re-record
  only for an intended visual change or a deliberate Xcode-version bump.
- Snapshot suites run **local-Mac only** (`.enabled(if: !SnapshotEnv.isXcodeCloud)`)
  — cross-machine AA drift makes them unreliable on CI runners.

**DEAD END — do not re-spike:** building a *non-pixel* "new label appeared" gate
by extracting rendered SwiftUI text via the **accessibility tree**
(`accessibilityLabel/Value` + `accessibilityChildren`) returns **0 lines
headlessly** on both a bare and a windowed `NSHostingView` — SwiftUI builds the
AX tree lazily, tied to a live AX client that headless `swift test` lacks. Strict
pixels (above) is the only viable content gate.

### Test doubles and CI isolation

- CloudKit / GameKit / any third-party service is consumed **via protocol injection + fake/stub in tests**.
- **Unit tests never touch real networks**; CI does not run CloudKit / GC integration tests.
- Real interactions happen only on the dev machine for manual verification (or a nightly standalone job, explicitly excluded from PR CI).
- Shared fakes are factored into a `<Project>KitTesting` target consumed by multiple test targets.

### The unentitled runner: live-framework landmines

- Constructing a **live CloudKit or Game Center object** inside a SwiftPM test — eager container initialization, or assigning a real auth/handshake handler — blocks the MainActor **synchronously and indefinitely** in the unentitled SwiftPM test runner (near-0% CPU; looks like a hang, not a crash). Both frameworks share this landmine class. Gate any live-framework touch behind a **test-only suppression seam** (a static flag or stub the driver checks before touching the real framework) so tests exercise your own state machine, never the real handshake.
- If a run does stall, kill the stuck test-runner helper process before retrying — stacking concurrent retries just queues them behind the same stuck build lock and multiplies the mess.
- A **parallel** test runner can also hang indefinitely on a package that links a framework like this, independent of any live-object bug. `--no-parallel` on that one package is a legitimate, fast workaround; diagnose with capped per-suite `--filter` runs (background the run, poll, kill-and-record-timeout) rather than stacking retries.

### `swift build` is not `swift test`

- Changing a **shared protocol requirement** only recompiles **sources** under `swift build` — test targets are not rebuilt. A test target's own conformer written against the OLD signature silently breaks and is invisible to `swift build`. **Rule:** after any protocol-requirement change, grep for conformers (`": <Protocol>"`) across every package including `Tests/`, and run `swift test` — not just `swift build` — on each package that has a test-target conformer.
- IDE/SourceKit diagnostics ("no such member", "cannot infer contextual base") on a freshly-added helper are frequently **stale index**, not a real error — the in-editor index lags a beat behind source just written. Treat such diagnostics as a hint, not truth; confirm with a filtered `swift test`, not a re-read of the diagnostic.

### Test pyramid

```
            ┌─────────────────────┐
            │  Snapshot (UI)      │  Few, starting from main screens
            ├─────────────────────┤
            │  Integration        │  With fakes
            │  (with fakes)       │
            ├─────────────────────┤
            │  Unit (logic)       │  Most, fastest
            └─────────────────────┘
```

### CI environment lock

- CI locks the Xcode version to match the local `.mise.toml`.
- When bumping Xcode, open a dedicated PR to refresh snapshot baselines.
- swift-testing parallelism is on by default; shared fakes need the `.serialized` trait to avoid races.

## Rationale

- swift-testing: Apple official, great Swift 6 support, more concise syntax (macros, `#expect`).
- Snapshots in git: PR reviewers see the visual diff directly and baselines are reproducible.
- Protocol fakes: CI runs all tests without an iCloud account or Game Center sign-in, keeping the environment simple.
- One-to-one test targets: clear dependencies; selective testing tools can pinpoint affected targets.

## Deviation considerations

- **A mature library is XCTest-only** (some UI test frameworks still are): scoped mixing is allowed.
- **Large existing XCTest codebase**: migrate in phases; new tests are swift-testing only.
- **Too many / oversized snapshots**: use git LFS, or limit snapshot coverage.

## Verification checklist

- Each production target has a matching `<Module>Tests`.
- `__Snapshots__/` is committed to git and not accidentally excluded by `.gitignore`.
- Content suites use strict `.image`; only AA-heavy board suites use `.tolerantImage` (project-local extension) — no ad-hoc per-call `precision:` overrides.
- A red snapshot suite is investigated as a behavior change, not silenced by re-recording.
- CI runner's macOS / Xcode version matches the local lock.
- No test connects directly to real CloudKit / Game Center.

## Related skills

- `swiftpm-modularization`: one-to-one test target layout and shared `<Project>KitTesting`.
- `xcode-cloud-single-track-ci`: CI Xcode lock and when PR CI runs tests.
- `mise-tool-management`: Xcode version managed by mise.
