# Crash triage and symbolication

How a crash reaches you, how to make its backtrace readable, how to read it, and how
to decide what to fix first. Every falsifiable claim carries its source in §Sources.
This is the crash half of field diagnostics; hangs and slow launches stay in
`SKILL.md` (§Hangs and hitches, §Launch time) and cross-reference back here.

## Contents

- [Four intake channels](#four-intake-channels)
- [Symbolication](#symbolication)
- [Reading a crash report](#reading-a-crash-report)
- [Exception-type cheat sheet](#exception-type-cheat-sheet)
- [Triage rules](#triage-rules)
- [Checklist](#checklist)
- [Sources](#sources)

## Four intake channels

| Channel | What arrives | Notes |
|---|---|---|
| **Xcode Organizer → Crashes** | Crash reports from App Store and TestFlight users, already symbolicated if you uploaded symbols with the build. "The Crashes organizer presents crash reports from customers who share diagnostic and usage information … TestFlight users of your app automatically share crash reports with you, regardless of the device settings". [S1] | Not available here: "Watchdog events, such as those from slow app launch times", "Invalid code-signature crashes", "Thermal events", "Jetsam events" — those come only from the device. [S1] Select a report → Inspector → **Generate Recommendations** pastes the stack into the coding assistant. [S1] Reports delivered through the Organizer omit thread names for privacy. [S5] |
| **App Store Connect / TestFlight** | ASC Analytics "Crashes" = "The total number of crashes on devices running a minimum of iOS 8, macOS 11, tvOS 9, or visionOS 1. Get detailed crash logs and crash reports in Xcode, such as unique totals for each type of crash and how many users experienced it." Usage totals "are based on App Store users who opt-in to share their data with you." [S2] TestFlight tab → Feedback → **Crashes**: tester-submitted crash feedback with comments; "Crash reports are available for download for 120 days." [S3] | ASC gives counts (dashboard widget "Crashes by App Version"); the per-crash detail and affected-user counts are in the Organizer. [S2] |
| **MetricKit** (in-app) | iOS 26 floor: `MXDiagnosticPayload.crashDiagnostics` → `MXCrashDiagnostic` with `callStackTree`, `exceptionType`, `exceptionCode`, `signal`, `exceptionReason`, `terminationReason`, `virtualMemoryRegionInfo`. Diagnostic payloads "arrive immediately in iOS 15 and later". [S4][S6] iOS / macOS 27: `MXCrashDiagnostic` is deprecated ("Use DiagnosticResult instead") together with `MXMetricManager` / `MXMetricManagerSubscriber` ("Use MetricManager instead"); iterate `MetricManager().diagnosticReports` and switch on `report.result` — `.crash(CrashDiagnostic)` exposes the same fields plus `terminationCategory` (`.watchdog`, `.badAccess`, …). `DiagnosticReport` is `Codable`, so `JSONEncoder` serializes it for your own sink. [S6][S7][S8] "MetricKit does not generate a `DiagnosticReport` for every occurrence of a diagnostic event." [S8] | The `callStackTree` is unsymbolicated addresses plus binary UUIDs — you symbolicate it yourself with the dSYMs (below). Ship it through the `MetricKitSink` described in `SKILL.md`, not straight from `AppDelegate`. |
| **A user's `.ips` file** | On device: Settings → Privacy & Security → Analytics & Improvements → **Analytics Data**; the log is named `<AppBinaryName>_<DateTime>` (crash) or `JetsamEvent_<DateTime>` (memory); Share → Mail. On macOS: Console → Crash Reports → Reveal in Finder. [S1] With the device attached: "click the Reports tab in the Device Hub app, then choose Crashes from the Inspector menu". [S9] | "Crash reports must have the `.crash` or `.ips` file extension. If the file has a different extension or no extension, rename the file before symbolicating." [S9] When debugging in Xcode the debugger swallows the crash — Debug > Detach (or `detach` in the console) to let the OS write the report. [S1] |

## Symbolication

**What a dSYM is.** "Debug builds of an app place the debug symbols inside the
compiled binary file by default, while release builds of an app place the debug
symbols in a companion debug symbol (`dSYM`) file". Each binary (app, framework,
extension) has its own dSYM; "A binary and a `dSYM` file are only compatible with each
other when they have identical build UUIDs." [S10]

**Build setting.** `DEBUG_INFORMATION_FORMAT` = "DWARF with dSYM File"
(`dwarf-with-dsym`) for the configuration you ship. [S10]

**Where the dSYMs go.**
- Local archive: "When archiving your app for distribution, Xcode gathers all binaries
  and `dSYM` files for your app and stores them inside the Xcode archive." Upload
  symbols with the build so the Crashes organizer symbolicates for you; without them
  "you still receive the crash reports through the Crashes organizer, but without the
  symbol names" and Xcode fills them in only if the dSYMs are on your Mac. "You must
  retain the Xcode archive for each build of your app you distribute." [S10]
- Xcode Cloud: the archive action "makes the exported app archive or framework
  bundle and the build logs available as artifacts" [S11] — download that archive
  artifact and keep it in a Spotlight-indexed location; it is the archive that holds
  the dSYMs (the archive rule above applies unchanged). Keep it under a path without
  `.noindex`. [S12]
- MetricKit `callStackTree`: nothing is symbolicated for you; you need the matching
  dSYMs on the machine that post-processes the payloads.

**Match the UUID.** Read the binary's UUID from the crash report's Binary Images
section (or open the report in Xcode → Debug navigator → Control-click → Show Library
Info), then:

```
% mdfind "com_apple_xcode_dsym_uuids == E3EA8743-C9E6-3C68-BF04-8D51363B689D"
% dwarfdump --uuid /path/to/TouchCanvas.app.dSYM
UUID: E3EA8743-C9E6-3C68-BF04-8D51363B689D (arm64) …/Contents/Resources/DWARF/TouchCanvas
```

`mdfind` printing nothing means Spotlight can't see the dSYM (indexing off, `.noindex`
in the path) or the build didn't produce one. [S12]

**Tools, from least to most manual.** [S9]
1. Open the `.ips` in Xcode (choose the project when prompted); Xcode symbolicates
   every thread it can. Missing OS frames → download that OS version's device symbols;
   missing app frames → find the dSYM as above.
2. `xcrun crashlog <path-to-crashReport>` — an LLDB Python module that resolves
   function names, source files and line numbers for every frame (`--help` for
   options).
3. `CrashSymbolicator.py` — "supports JSON-format crash reports and inlined frames when
   run with its default options". It lives inside the Xcode bundle:

   ```
   % xcode-select -p
   /Applications/Xcode.app/Contents/Developer
   % cd /Applications/Xcode.app/Contents/SharedFrameworks/CoreSymbolicationDT.framework/Resources
   % python3 CrashSymbolicator.py <path-to-crashReport> -d <path-to-dSYM> [-o out.ips]
   ```

   Derive the directory from `xcode-select -p` by replacing `Contents/Developer` with
   `Contents/SharedFrameworks/CoreSymbolicationDT.framework/Resources` (verified
   present on Xcode 26.5 at that path). The current Apple page documents only
   Xcode-open, `xcrun crashlog`, this script and `atos`; the old `symbolicatecrash`
   script is not mentioned.
4. `atos` — one frame at a time. Take the architecture and load address from the
   Binary Images section, and point `-o` at the DWARF file *inside* the dSYM, not the
   bundle:

   ```
   % atos -arch arm64 -o TouchCanvas.app.dSYM/Contents/Resources/DWARF/TouchCanvas -l 0x10459c000 -i 0x1045a4610
   ```

   `-i` expands inlined frames; `-dedup` reveals the functions behind a
   `<deduplicated_symbol>` (release builds merge identical machine code by default). [S9]

A report is *fully* symbolicated when every frame shows a function name, *partially*
when only some do (often enough), and *unsymbolicated* when it is all hex — "an
unsymbolicated crash report is rarely useful". [S9]

## Reading a crash report

Read in this order [S5]:

1. **Exception information** — `Exception Type` (Mach exception + BSD signal),
   `Exception Codes` / `Subtype` / `Message`, `Exception Note`, `Termination Reason`,
   `Triggered by Thread`. "This information is important, but is often overlooked."
   - `Exception Note: EXC_CORPSE_NOTIFY` → "the crash didn't originate from a hardware
     trap, either because the process was explicitly quit by the operating system or
     the process called `abort()`".
   - `SIMULATED (this is NOT a crash)` / `NON-FATAL CONDITION (this is NOT a crash)` →
     the process did not actually crash; treat as a diagnostic, not a crash.
   - `Termination Reason` carries OS-side reasons: invalid code signature, missing
     dependent library, "accessing privacy sensitive information without a purpose
     string", watchdog codes.
2. **Diagnostic messages** — `Application Specific Information` (e.g. `BUG IN CLIENT
   OF LIBDISPATCH: dispatch_sync called on queue already owned by current thread`),
   `Termination Description` for watchdog kills, `VM Region Info` for bad memory
   access. Also `Last Exception Backtrace` before Thread 0 when an Objective-C / C++
   exception was thrown.
3. **The crashed thread** (`Thread N Crashed:`), then walk down from frame 0 to the
   **first frame in one of your binaries** — that is where to open the source. For a
   Swift runtime trap frame 0 is usually already yours, with `(File.swift:line)`
   appended once symbolicated. [S13]
4. **Binary Images** — only for the UUID / load address you need to symbolicate.

## Exception-type cheat sheet

Only types Apple documents in the "Diagnosing issues using crash reports" series.

| `Exception Type` | Typical cause | Where to look next |
|---|---|---|
| `EXC_BAD_ACCESS (SIGSEGV)` / `(SIGBUS)` | "accessing an invalid index in an array, dereferencing a pointer to an invalid memory location, or writing to read-only memory"; zombies, use-after-free. `Exception Subtype: KERN_INVALID_ADDRESS at 0x…`. [S14][S15] | Reproduce under Address Sanitizer / Undefined Behavior Sanitizer / Thread Sanitizer; run the static analyzer for ObjC/C/C++; read `VM Region Info`. [S15] |
| `EXC_BREAKPOINT (SIGTRAP)` (ARM) / `EXC_BAD_INSTRUCTION (SIGILL)` (x86_64) | A trace trap: "The Swift runtime uses trace traps for specific types of unrecoverable errors" — force-unwrapping `nil`, failed `as!`, out-of-range index; also `fatalError`, `__builtin_trap()`, and libdispatch misuse (see `Additional Diagnostic Information`). [S16][S13] | Frame 0 of the crashed thread names the file and line once symbolicated; fix the precondition. `Termination Reason: Namespace SIGNAL, Code 0x5`. [S13] |
| `EXC_CRASH (SIGABRT)` | `abort()` — "such as when an app encounters an uncaught Objective-C or C++ language exception"; for app extensions, `Exception Subtype: LAUNCH_HANG` when initialization took too long. [S17] | Read `Last Exception Backtrace` and `Application Specific Information` first; `LAUNCH_HANG` → treat as a launch-time hang (`SKILL.md` §Launch time). |
| `EXC_CRASH (SIGKILL)` | The OS killed the process; `Termination Reason` code says why: `0x8badf00d` watchdog, `0xdead10cc` held a file / SQLite lock during suspension, `0xc00010ff` thermal, `0xbaddd15c` cache purge for disk space, `0x2182bad2/3/4` background task / URL session / fetch overran, `0xd00d2bad` excessive system resources, `0xbaadca11` CallKit/PushKit, `0xc51bad01–03` watchOS background CPU/time. [S18] | Watchdog → below. `0xdead10cc` → `beginBackgroundTask(withName:expirationHandler:)` around the write. [S18] |
| Watchdog (`0x8badf00d`) | "The watchdog terminates apps that block the main thread for a significant time" — synchronous networking, big JSON, synchronous Core Data migration, Vision requests. `Termination Description` shows `scene-create` (first frame never rendered) or `scene-update` (main thread too busy) and "exhausted real (wall clock) time allowance of 19.97 seconds". [S19] | Not in the Organizer — get the `.ips` from the device. [S1] This is the crash form of a hang: `SKILL.md` §Launch time (pre-main / first frame) and §Hangs and hitches (Hangs instrument, `MXHangDiagnostic`). |
| Jetsam (`JetsamEvent_*` log) | Memory pressure: "the system frees memory by terminating applications to reclaim their memory. This is a jetsam event". JSON, "they don't contain the backtraces of any threads"; header `pageSize` and `largestProcess`; only the jettisoned process has a `reason` key. "If the system jettisons your app due to memory pressure while the app is visible, it will look like your app crashed." [S20] | Not in the Organizer. [S1] Multiply pages × `pageSize`; if your app is `largestProcess`, go to `SKILL.md` §Memory (Allocations generations, downsampling, `MXMemoryMetric.peakMemoryUsage`). |
| `EXC_RESOURCE` | Resource limit: `Exception Subtype` `CPU` / `CPU_FATAL`, `MEMORY`, `IO`, `WAKEUPS`; `NON-FATAL CONDITION` means the process was *not* terminated. [S21] | `MEMORY` "may be a precursor to termination for excess memory usage"; `WAKEUPS` → look for tight `dispatch_async` / `perform(_:on:…)` loops across similar background-thread backtraces. [S21] |

## Triage rules

1. **Confirm it is a crash.** `SIMULATED` / `NON-FATAL CONDITION` notes, `EXC_RESOURCE`
   without `_FATAL`, and MetricKit hang diagnostics are not crashes — route them to the
   hang / memory sections instead of the crash queue. [S5][S21]
2. **Rank by users affected on the shipping version.** Apple's own surfaces expose
   "unique totals for each type of crash and how many users experienced it" [S2]; a
   crash with many reports from one device (same `CrashReporter Key` / `Beta
   Identifier`) [S5] ranks below one touching many users. A crash that only appears
   on an old app version with a fix already shipped is closed, not fixed twice.
3. **Split by OS version and hardware before reading code.** `OS Version`,
   `Hardware Model`, `AppVariant` in the header tell you whether it is a new-OS
   regression, a thinning variant, or universal. [S5]
4. **Classify by exception type** (table above) — it decides the tool: sanitizers for
   `EXC_BAD_ACCESS`, source line for `EXC_BREAKPOINT`, exception backtrace for
   `SIGABRT`, termination code for `SIGKILL`.
5. **Hand off non-crashes.** Watchdog and `LAUNCH_HANG` → `SKILL.md` §Launch time and
   §Hangs; Jetsam and `EXC_RESOURCE MEMORY` → §Memory; MetricKit `hangDiagnostics` →
   §Hangs. Conversely, a hang that ends in `0x8badf00d` comes back here as a crash.
6. **Keep the archive.** If the dSYM for the crashing build is gone, the only recovery
   is shipping a new version and retaining its archive. [S12]

## Checklist

- [ ] Release configuration builds with `DEBUG_INFORMATION_FORMAT = dwarf-with-dsym`;
      symbols are uploaded with every App Store / TestFlight build. [S10]
- [ ] Every distributed archive (local or Xcode Cloud artifact) is retained in a
      Spotlight-indexed location without `.noindex`. [S10][S12]
- [ ] `dwarfdump --uuid` of the retained dSYM equals the crash report's Binary Images
      UUID before you trust any symbolicated line. [S12]
- [ ] Crash intake covers all four channels; watchdog / Jetsam / thermal / signature
      crashes are pulled from devices, not expected in the Organizer. [S1]
- [ ] MetricKit crash diagnostics reach the telemetry sink; on the 27 toolchain the
      sink reads `MetricManager().diagnosticReports` and switches on `.crash`. [S6][S8]
- [ ] Each open crash has: exception type, termination reason, crashed thread's first
      app frame, affected-user count, and OS/hardware split recorded before a fix is
      planned.
- [ ] Non-crash diagnostics (hang, `NON-FATAL`, `EXC_RESOURCE` non-fatal) are routed
      to the hang / memory workflow in `SKILL.md`.

## Sources

- [S1] Acquiring crash reports and diagnostic logs — https://developer.apple.com/documentation/xcode/acquiring-crash-reports-and-diagnostic-logs
- [S2] App Store Connect Analytics metric definitions ("Crashes") — https://developer.apple.com/help/app-store-connect-analytics/reference/metrics-definitions
- [S3] App Store Connect Help: View tester feedback — https://developer.apple.com/help/app-store-connect/test-a-beta-version/view-tester-feedback
- [S4] `MXCrashDiagnostic` (deprecated 27.0, "Use DiagnosticResult instead") — https://developer.apple.com/documentation/metrickit/mxcrashdiagnostic
- [S5] Examining the fields in a crash report — https://developer.apple.com/documentation/xcode/examining-the-fields-in-a-crash-report
- [S6] MetricKit framework overview / `MXMetricManager` (deprecated 27.0, "Use MetricManager instead") — https://developer.apple.com/documentation/metrickit and https://developer.apple.com/documentation/metrickit/mxmetricmanager
- [S7] `MetricManager` (iOS 27+) and `CrashDiagnostic` — https://developer.apple.com/documentation/metrickit/metricmanager and https://developer.apple.com/documentation/metrickit/crashdiagnostic
- [S8] `DiagnosticReport` — https://developer.apple.com/documentation/metrickit/diagnosticreport
- [S9] Adding identifiable symbol names to a crash report — https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report
- [S10] Building your app to include debugging information — https://developer.apple.com/documentation/xcode/building-your-app-to-include-debugging-information
- [S11] Configuring your Xcode Cloud workflow's actions (archive action artifacts) — https://developer.apple.com/documentation/xcode/configuring-your-xcode-cloud-workflow-s-actions
- [S12] Locating a missing debug symbol file — https://developer.apple.com/documentation/xcode/locating-a-missing-debug-symbol-file
- [S13] Addressing crashes from Swift runtime errors — https://developer.apple.com/documentation/xcode/addressing-crashes-from-swift-runtime-errors
- [S14] EXC_BAD_ACCESS (SIGSEGV) — https://developer.apple.com/documentation/xcode/sigsegv
- [S15] Investigating memory access crashes — https://developer.apple.com/documentation/xcode/investigating-memory-access-crashes
- [S16] EXC_BREAKPOINT (SIGTRAP) and EXC_BAD_INSTRUCTION (SIGILL) — https://developer.apple.com/documentation/xcode/sigtrap_sigill
- [S17] EXC_CRASH (SIGABRT) — https://developer.apple.com/documentation/xcode/sigabrt
- [S18] EXC_CRASH (SIGKILL) — https://developer.apple.com/documentation/xcode/sigkill
- [S19] Addressing watchdog terminations — https://developer.apple.com/documentation/xcode/addressing-watchdog-terminations
- [S20] Identifying high-memory use with jetsam event reports — https://developer.apple.com/documentation/xcode/identifying-high-memory-use-with-jetsam-event-reports
- [S21] EXC_RESOURCE — https://developer.apple.com/documentation/xcode/exc_resource
- Series index: Diagnosing issues using crash reports and device logs — https://developer.apple.com/documentation/xcode/diagnosing-issues-using-crash-reports-and-device-logs
