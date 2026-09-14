# Instruments templates in detail

Full walkthrough of each Instruments template referenced from the `## Instruments` table in
SKILL.md. Read this when you need the how-to-drive-the-UI detail, not just the metric to watch.

**Time Profiler** — samples the call stack at ~1 kHz. Reveals which functions consume CPU time. After recording, invert the call tree and hide system libraries to surface your own hot paths. A function taking >5 ms on the main thread in an interactive path is a candidate for offloading.

**Allocations** — tracks every heap allocation. Use the "Generation" feature: take a snapshot before an action, perform the action repeatedly, take another snapshot, and diff. Any allocation that grew unboundedly across generations is a leak or an accumulation bug. The "Leaks" instrument detects reference cycles automatically but misses logical leaks (objects kept alive longer than needed).

**SwiftUI instrument** — records View body invocation counts, `@State` change propagation, and diffing cost. Xcode 26 introduced a next-generation SwiftUI instrument that tracks the causes of each update. A body that fires more than expected usually means a dependency is too coarse (e.g. observing the whole model when only one field is needed). The instrument shows which property change triggered each body re-render.

**Hangs instrument** (Xcode 14+) — captures main-thread spins longer than a configurable threshold (default 250 ms). Apple's tooling reports hangs starting at 250 ms; on-device hang detection can be tuned from 250 ms up to several seconds depending on the diagnostic. Pairs with the **App Launch** template for pre-first-frame blocking. The system also generates `MXHangDiagnostic` on-device (see MetricKit below).

**Hitches** — a hitch occurs when a frame takes longer than one vsync interval to deliver, causing a visual stutter. On 60 Hz displays the budget is ~16.67 ms; on ProMotion (120 Hz) it halves to ~8.33 ms. Use the **Animation Hitches** instrument template (Hitches, Display, and Core Animation Commits tracks — the standalone "Core Animation" template no longer exists) to see committed frames and dropped frames. The `hitch rate` (ms of hitch per second of scrolling) is the standard metric: <5 ms/s is good; 5–10 ms/s is concerning (user notices interruptions); >10 ms/s is critical (greatly impacts UX) — per WWDC 2020 session 10077.
