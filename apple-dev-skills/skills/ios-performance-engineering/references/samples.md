# Samples

## Image downsampling (ImageIO)

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

## MetricKit receiver (MXMetricManagerSubscriber)

`MXMetricManager` / `MXMetricManagerSubscriber` are deprecated from iOS / macOS 27
(replacement: `MetricManager().metricReports`, `for await`); this sample targets the
catalog's iOS 26 floor.

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

## XCTMetric baseline test

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
