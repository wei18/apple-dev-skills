---
name: ios-performance-engineering
description: Measure and fix iOS/macOS performance — Instruments (Time Profiler, Allocations, SwiftUI instrument, Hangs), os_signpost, MetricKit field telemetry, XCTMetric baselines, launch-time optimisation, memory footprint, binary size. Invoke when diagnosing slowness/hitches/high memory, setting up CI perf baselines, wiring MetricKit, or asking "why is my app slow / using too much memory / large".
---

# iOS Performance Engineering

## When to invoke

- Diagnosing UI slowness, scroll hitches, or app hangs.
- Investigating high memory usage, leaks, or large binary size.
- Wiring MetricKit to receive field performance data from real devices.
- Setting up `XCTMetric` / `measure {}` baselines in CI.
- Deciding whether to move work off `@MainActor` and how to do it safely.
- Evaluating launch time before a release.

## Instruments — the primary measurement tool

Never guess at a performance problem; profile first. Instruments ships with Xcode. Key templates:

**Time Profiler** — samples the call stack at ~1 kHz. Reveals which functions consume CPU time. After recording, invert the call tree and hide system libraries to surface your own hot paths. A function taking >5 ms on the main thread in an interactive path is a candidate for offloading.

**Allocations** — tracks every heap allocation. Use the "Generation" feature: take a snapshot before an action, perform the action repeatedly, take another snapshot, and diff. Any allocation that grew unboundedly across generations is a leak or an accumulation bug. The "Leaks" instrument detects reference cycles automatically but misses logical leaks (objects kept alive longer than needed).

**SwiftUI instrument** — records View body invocation counts, `@State` change propagation, and diffing cost. Available from Xcode 15+. A body that fires more than expected usually means a dependency is too coarse (e.g. observing the whole model when only one field is needed). The instrument shows which property change triggered each body re-render.

**Hangs instrument** (Xcode 14+) — captures main-thread spins longer than a configurable threshold (default 250 ms). Apple classifies blocks 250–500 ms as micro-hangs and ≥500 ms as full hangs. Pairs with the **App Launch** template for pre-first-frame blocking. The system also generates `MXHangDiagnostic` on-device (see MetricKit below).

**Hitches** — a hitch occurs when a frame takes longer than one vsync interval to deliver, causing a visual stutter. On 60 Hz displays the budget is ~16.67 ms; on ProMotion (120 Hz) it halves to ~8.33 ms. Use the **Core Animation** instrument to see committed frames and dropped frames. The `hitch rate` (ms of hitch per second of scrolling) is the standard metric: <5 ms/s is good; 5–10 ms/s is concerning (user notices interruptions); >10 ms/s is critical (greatly impacts UX) — per WWDC 2020 session 10077.

### `os_signpost` — annotate your own intervals

```swift
import os

let log = OSLog(subsystem: "com.example.MyApp", category: .pointsOfInterest)
let id = OSSignpostID(log: log)

os_signpost(.begin, log: log, name: "ImageDecode", signpostID: id)
let image = decodeImage(data)
os_signpost(.end, log: log, name: "ImageDecode", signpostID: id)
```

Signpost intervals appear in the Instruments timeline as coloured spans. Use `.event` for instantaneous markers (user taps, cache misses). Prefer `OSSignposter` (iOS 15+/macOS 12+, introduced WWDC 2021; Swift-only wrapper over C `os_signpost`) from the `os` framework — it supports structured metadata:

```swift
let signposter = OSSignposter(subsystem: "com.example.MyApp", category: "Render")
let state = signposter.beginInterval("TileRender", id: signposter.makeSignpostID())
// ... work ...
signposter.endInterval("TileRender", state)
```

### `xctrace` — Instruments from CI

```bash
xctrace record \
  --template "Time Profiler" \
  --launch -- /path/to/MyApp.app \
  --output trace.xctrace \
  --time-limit 30s
```

`xctrace` can drive any built-in or custom Instruments template headlessly and export the trace as a `.xctrace` bundle. Post-process with `xctrace export` to pull out human-readable XML. Wire this into a CI step on a dedicated Mac runner to catch regressions before they reach users.

## Hangs and hitches

The system classifies a main-thread block of **250 ms or more** as a hang and surfaces it in the Organizer → Hang Reports (Xcode 14+) and via MetricKit's `MXHangDiagnosticPayload`. The scroll hitch budget depends on display refresh rate (see above).

**Moving work off `@MainActor`:**

```swift
// Wrong — blocks the main thread
func loadData() {
    let json = try! Data(contentsOf: remoteURL)   // network I/O on main thread
    items = try! JSONDecoder().decode([Item].self, from: json)
}

// Right — async, main actor only for the final UI update
func loadData() async throws {
    let json = try await URLSession.shared.data(from: remoteURL).0
    let decoded = try JSONDecoder().decode([Item].self, from: json)
    await MainActor.run { items = decoded }
}
```

For CPU-heavy processing (image decoding, compression, sorting large arrays), use `Task.detached(priority: .userInitiated)` or dispatch to a background `Actor`. Never use `DispatchQueue.global().async` in new Swift 6 code — prefer structured concurrency.

One-shot bootstrapping on first appearance belongs in `.task` — the correct Apple-recommended modifier for async work tied to view lifetime. Verify async-lifecycle behavior on your toolchain if you encounter unexpected issues.

## Launch time

Launch time splits into two phases:

**Pre-main (dyld)** — loading and linking dylibs before `main()` runs. Minimise by: keeping the embedded dylib count low (prefer static libraries for non-system frameworks), avoiding `+load` methods, and not registering large numbers of `@objc` classes at startup. The **App Launch** Instruments template shows the pre-main timeline. Target: under 400 ms on a cold launch on the slowest supported device.

**Post-main / first frame** — everything from `application(_:didFinishLaunchingWithOptions:)` through the first committed frame. Defer every initialisation that is not required to display the initial screen. CloudKit containers, network prefetches, and analytics SDKs should be lazy. Measure with the **App Launch** template and the `os_signpost` `.begin`/`.end` around your own startup phases.

Common traps: eager `CKContainer.default()` on the main thread (hangs until entitlement check completes), synchronous keychain reads at app start, and large SQLite `PRAGMA` operations before the first view renders.

## Memory

**Footprint vs leaks**: Instruments Allocations shows the heap; use `vmmap` or the Memory Debugger in Xcode to see the full virtual memory map (dirty pages, compressed pages, mapped files). The OS terminates apps that exceed their footprint budget silently — `JETSAM_REASON_HIGH_WATER_MARK` in the crash log. Reduce by:

- **Image downsampling**: never decode a 4K image to display it at 100 pt. Use `ImageIO` with `kCGImageSourceThumbnailMaxPixelSize` or `UIGraphicsImageRenderer` to decode at display resolution.

```swift
func downsample(imageAt url: URL, to pointSize: CGSize, scale: CGFloat) -> UIImage {
    let options: [CFString: Any] = [
        kCGImageSourceShouldCacheImmediately: false,
        kCGImageSourceShouldCache: false
    ]
    let src = CGImageSourceCreateWithURL(url as CFURL, options as CFDictionary)!
    let maxDim = max(pointSize.width, pointSize.height) * scale
    let thumbOptions: [CFString: Any] = [
        kCGImageSourceCreateThumbnailWithTransform: true,
        kCGImageSourceCreateThumbnailFromImageAlways: true,
        kCGImageSourceThumbnailMaxPixelSize: maxDim
    ]
    let cgImage = CGImageSourceCreateThumbnailAtIndex(src, 0, thumbOptions as CFDictionary)!
    return UIImage(cgImage: cgImage)
}
```

- **`autoreleasepool`** in tight loops that allocate many Objective-C objects (e.g. iterating `NSManagedObject` fetches, calling `UIImage(named:)` in a loop). The pool drains at the end of each `autoreleasepool { }` block rather than at the runloop turn boundary.
- **Retain cycles**: `[weak self]` in closures stored on `self`; `weak var delegate` in delegation patterns. The Leaks instrument and the Memory Graph Debugger (product menu → Debug Memory Graph) visualise the reference graph and highlight cycles in red.

## Binary size

Large binaries increase download time and App Store review scrutiny. Primary levers:

- **Dead code stripping** (`DEAD_CODE_STRIPPING = YES` in Xcode build settings, default on for Release). Removes unreachable functions and data sections.
- **`-Osize`** (`SWIFT_OPTIMIZATION_LEVEL = -Osize`): optimises for binary size rather than speed. Typically 5–15% smaller than `-O` with negligible runtime impact for most app code.
- **Asset catalog / app thinning**: use asset catalog image sets with `@1x`/`@2x`/`@3x` variants and device-specific slices. The App Store strips variants irrelevant to the downloading device. Avoid embedding full-resolution assets in the bundle for cases where a downsampled or streamed version suffices.
- **Link Map + Organizer**: use the **Link Map** (Build Settings: Write Link Map File = YES) and the Xcode Organizer's App Size report to identify which symbols contribute most to the binary. Tools such as Bloaty or the `nm` / `size` commands can post-process the link map to locate unexpectedly large third-party frameworks or generated code.
- Avoid shipping unused localisation bundles from third-party SDKs: set `SWIFT_PACKAGE_RESOURCE_BUNDLE_DEDUPLICATE = YES` and review resource bundle sizes after each SDK update.

## MetricKit — field performance telemetry

MetricKit delivers on-device aggregated performance metrics to your app once per day (and immediately for diagnostic payloads on device disconnect from Xcode):

```swift
import MetricKit

final class MetricKitReceiver: NSObject, MXMetricManagerSubscriber {
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            // CPU time, memory, disk, network, display — aggregated over 24 h
            let cpuTime = payload.cpuMetrics?.cumulativeCPUTime
            let avgMemory = payload.memoryMetrics?.averageSuspendedMemory
            // Forward to your telemetry sink
        }
    }

    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            // MXHangDiagnostic, MXCrashDiagnostic, MXCPUExceptionDiagnostic
            let hangs = payload.hangDiagnostics    // call trees for hang events
            // Persist or upload for analysis
        }
    }
}

// Register at app start — one call, lives for the app lifetime
MXMetricManager.shared.add(receiver)
```

MetricKit data reflects **real user conditions** (actual device, network, battery state), making it the authoritative source for field performance signals. Key metric classes:

| Class | What it measures |
|---|---|
| `MXCPUMetrics` | Cumulative CPU time (user + system) |
| `MXMemoryMetrics` | Peak and average memory, average suspended memory |
| `MXDisplayMetric` | Average pixel luminance (not hitch rate — use `MXAnimationMetric` — `scrollHitchTimeRatio`: ratio of hitch time while scrolling (field-measured)) |
| `MXDiskIOMetrics` | Cumulative logical write bytes |
| `MXHangDiagnostic` | Call tree for a main-thread hang > 250 ms |
| `MXCrashDiagnostic` | Crash reason + call tree |
| `MXCPUExceptionDiagnostic` | CPU runaway above system threshold |

Wire MetricKit as a **sink** in your telemetry facade (per `telemetry-facade-pattern`) — a `MetricKitSink` that subscribes to `MXMetricManager.shared` and broadcasts payloads as `TelemetryEvent` instances. This keeps MetricKit wiring out of `AppDelegate` and testable via protocol injection. Note that MetricKit complements but does not replace the analytics tracking covered in `apple-three-piece-analytics`: MetricKit is system-generated aggregate performance data, not user behaviour events.

## `XCTMetric` and `measure {}` baselines in CI

```swift
func testScrollPerformance() {
    let app = XCUIApplication()
    app.launch()
    measure(metrics: [XCTOSSignpostMetric.scrollDecelerationMetric,
                      XCTMemoryMetric(application: app),
                      XCTCPUMetric(application: app)]) {
        // simulate the action
        app.swipeUp()
    }
}
```

`measure {}` runs the block 5 times (by default) and records the mean. On first run, set the baseline via the inline editor in Xcode. Subsequent runs fail if the result exceeds `baseline * (1 + maxStandardDeviations)` — configurable per metric. Commit baselines in `.xcbaseline` files alongside the test file.

For server-side CI (where a physical display is unavailable), use `XCTCPUMetric` and `XCTMemoryMetric` in unit tests that exercise logic without UIKit rendering. UI performance metrics require a simulator or device with an active display session.

## Verification checklist

- Profile with Instruments before claiming a fix; never tune by guessing.
- Time Profiler run completed; hot paths on the main thread identified and either offloaded or bounded.
- Allocations generation diff shows no unbounded growth across repeated user actions.
- SwiftUI instrument checked for unexpected body re-render counts on the primary screen.
- `os_signpost` intervals added around any operation expected to take > 16 ms.
- `MXMetricManagerSubscriber` registered in the composition root; payloads forwarded to the telemetry sink.
- `XCTMetric` baseline committed for the primary performance-sensitive test; CI fails on regression.
- No synchronous network or file I/O on the main thread (audited via Thread Sanitizer and code review).
- Image assets decoded at display resolution, not source resolution.
- Binary size measured with `-Osize` before each major release; asset catalog slices verified.

## Related skills

- `telemetry-facade-pattern`: wire `MetricKitSink` as one sink in the fan-out facade; keep `MXMetricManagerSubscriber` registration out of `AppDelegate`.
- `apple-three-piece-analytics`: MetricKit covers system-level performance telemetry; the three-piece stack covers user behaviour and business events — they are complementary, not overlapping.
- `swift6-concurrency`: moving work off `@MainActor` correctly requires understanding actor isolation, `Task.detached`, and `Sendable` constraints — the primary tool for eliminating main-thread hangs.
- `swiftui-expert` (aggregated external): for the **SwiftUI body-re-render** slice specifically, it ships an Instruments `.trace` analysis toolchain — prefer it for that profiling. This skill owns the broader surface (Time Profiler / Allocations / hangs / launch / memory / binary size / MetricKit / XCTMetric).
