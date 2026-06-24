---
name: apple-three-piece-analytics
description: Default analytics stack for solo / small Apple-platform Apps — App Store Connect Analytics + MetricKit + Game Center (for games), no third-party tracking SDK by default, PrivacyInfo.xcprivacy mandatory. Invoke when starting a new project, deciding analytics SDK (vs Firebase / TelemetryDeck / Amplitude), writing PrivacyInfo, or when asked "should I integrate Firebase / Mixpanel / TelemetryDeck".
---

# Apple Three-Piece Analytics

## When to invoke

- Starting a new App and deciding on an analytics SDK.
- Evaluating Firebase / TelemetryDeck / Mixpanel / Amplitude / Sentry.
- Writing `PrivacyInfo.xcprivacy`.
- User asks "what metrics should I track", "what can I see without a third-party SDK".

## Default decisions

### v1 uses the Apple three-piece set

| Source | What it provides | Where to view |
|---|---|---|
| **App Store Connect Analytics** | Downloads, sessions, active devices, retention, sources, store conversion | App Store Connect web |
| **MetricKit** (`MXMetricPayload`, `MXDiagnosticPayload`) | Performance & diagnostics: crash / hang / launch time / jank / energy / memory | The App receives them → persist to log / optionally upload later |

> **macOS caveat**: MetricKit on macOS yields a reduced payload set compared to iOS (some payload types are iOS-only, e.g. `MXAppLaunchMetric`). For mac-heavy apps, lean more on App Store Connect Analytics + targeted `OSSignposter` traces.
| **Game Center** (if it's a game) | Leaderboards / achievement completion / peer-player comparison | Game Center API / Game Center app |

### Privacy / Manifest

- **`PrivacyInfo.xcprivacy` is a required deliverable** (hard App Store submission requirement).
- Because no third-party SDK, no IDFA, no PII are collected, the manifest content is very minimal.
- **No ATT prompt needed** (no IDFA use case).
- CloudKit / Game Center's user-facing privacy notices are handled at the system layer by Apple; the App only needs to declare data usage in PrivacyInfo.

### What's not covered (explicitly accepted)

- Micro-behaviour streams like "which button was tapped" or "how long was spent on a screen" are **not** covered by the three-piece set.
- Confirm v1 doesn't need to answer these questions; deviate if it does.

## Rationale

- At solo / small-team scale, the three pieces cover most key questions (installs / retention / performance / crashes / player comparisons).
- No third-party SDK → no ATT, no PrivacyInfo additions, small build size, and the privacy claim is verifiable by readers via grep on `import`.
- Positive for a public-repo showcase ("no third-party tracking" is a credible commitment).

## Deviation considerations

### Adopt TelemetryDeck (privacy-friendly first)

- **Trigger**: actually need the micro-behaviour stream of "which button, where do users get stuck".
- **Priority**: TelemetryDeck > Firebase (the latter has heavier privacy burden, needs ATT, and many PrivacyInfo entries).
- **How to integrate**: swap in the `TrackingSink` implementation via `telemetry-facade-pattern`; call sites change nothing.

### Adopt Sentry / Crashlytics

- **Trigger**: MetricKit `MXDiagnosticPayload` persistence still isn't enough for the incident workflow.
- **Cost**: third-party SDK, extra PrivacyInfo entries, build size.

## Verification checklist

- `PrivacyInfo.xcprivacy` exists and passes App Store Connect validation.
- No `import Firebase*` / `import Sentry` / `import Amplitude`, etc.
- MetricKit subscription is wired (`MXMetricManager.shared.add(...)`).
- Game Center entitlement aligns with leaderboard / achievement definitions (for games).

## Related skills

- `telemetry-facade-pattern`: the sink implementations for each piece.
- `oslog-logger-defaults`: MetricKit payloads persist via OSLog.
- `apple-public-repo-security`: "no PII / no third-party SDK" is one of the public-repo commitments.
