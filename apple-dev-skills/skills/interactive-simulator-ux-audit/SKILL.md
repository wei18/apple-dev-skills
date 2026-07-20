---
name: interactive-simulator-ux-audit
description: Use when auditing an iOS/iPadOS app's live behavior in the Simulator — navigation, modals, back-stack, completion flows, safe-area/Dynamic-Island clipping, offline or signed-out states — bugs a fixed-size snapshot render structurally cannot show. Covers installing `idb` without Homebrew (direct GitHub release + an exec wrapper that preserves rpath), the describe-all → tap → screenshot drive loop, device-point vs screenshot-pixel coordinate spaces, and the "stale build" / "worktree launch crash" false-negative traps. Use when asked to "test the UI", "find UX problems", "drive the simulator", or verify an interactive flow end-to-end.
---

# Interactive Simulator UX Audit (idb-driven)

Snapshot tests render a view in a fixed-size `NSHostingView` — they model neither
navigation, taps, the device safe area, nor the Dynamic Island. A whole class of bugs
only shows when something actually drives the app: a screen that never appears after
a selection, a flow that's unplayable when the user is signed out of a cloud account,
completion content clipped by the Dynamic Island. This skill is the audit loop that
catches those, using `idb` (Facebook's iOS Simulator automation tool) to tap, read the
accessibility tree, and capture screenshots against a **booted** Simulator.

## When to invoke

- Asked to "test the UI", "find UX problems", or "drive the simulator".
- Verifying a navigation, modal, or completion flow actually renders end-to-end after a code change.
- Auditing safe-area / Dynamic-Island layout, or an offline / signed-out flow, that snapshot tests can't model.
- Debugging a report that only reproduces "in the app," not in any test.

## Scope

Owns: live Simulator driving via `idb`, the audit loop, and the coordinate/build gotchas
below. Does **not** own: scripted, CI-run UI tests that launch and assert without a human
watching → `host-driven-xcuitest-e2e`; static pixel-diff regression gates → `swift-testing-baseline`.
Use this skill first to *find* a bug interactively; write a host-driven XCUITest afterward
to *pin* the fix.

## Prereq: install `idb` (one-time, not via Homebrew)

If your project's policy forbids Homebrew, a direct GitHub release download is a distinct,
usually-allowed path — confirm against your own policy, then:

1. **`idb_companion`**: download `idb-companion.universal.tar.gz` from
   https://github.com/facebook/idb/releases → extract to e.g.
   `~/idb-tools/companion/idb-companion.universal/` (binary lives in `bin/`, with a sibling
   `Frameworks/` directory the binary loads via `@executable_path`). An objc
   duplicate-class warning for `FBProcess` at launch is non-fatal.
2. **`idb` CLI**: `pip3 install --user fb-idb`.
3. Put both on `PATH`. Symlink `idb` directly. For the companion, use a **wrapper script**
   that `exec`s the real binary's *absolute path* — a bare symlink breaks the
   `@executable_path/../Frameworks` rpath and the companion fails to load its frameworks.
4. Verify: `idb list-targets`, then against a booted simulator's UDID,
   `idb ui describe-all --udid <udid>` returns the accessibility tree (element frames +
   labels) in **device-point** space (e.g. an iPhone 17 Pro reports 402×874 pt).

## Build + install the app under test

- **Check the installed build version first**, in the app's own Settings/About screen if it
  has one. A stale install silently invalidates every finding in the session — confirm you're
  testing the build you think you are before reporting anything as a bug.
- Typical build: `xcodebuild -workspace <App>.xcworkspace -scheme <Scheme> -sdk iphonesimulator
  -configuration Debug -destination 'platform=iOS Simulator,name=<device>' -derivedDataPath
  build/sim build`, then `xcrun simctl install <udid> <App.app>`.
- **Build from a normal checkout, not an ephemeral agent worktree**, if your project keeps
  gitignored build secrets (API keys, provisioning config) outside version control. A worktree
  missing those files can make a Debug build crash at launch on a startup assertion — that's
  an environment artifact of the worktree, not a code bug; don't chase it as one.

## The drive loop

```
idb ui describe-all --udid <udid>            # element frames + accessibility labels
idb ui tap --udid <udid> <x> <y>              # tap at device-point coordinates
xcrun simctl io <udid> screenshot <path.png>  # capture, then read the PNG and look at it
```

- **Get tap coordinates from `describe-all`**, not from eyeballing a screenshot — a
  screenshot is rendered at the device's pixel scale (commonly 3×), not point space. Tap the
  center of an element's reported `frame`.
- **Look at every screenshot.** The accessibility tree tells you *what* elements exist; only
  the rendered image shows clipping, overlap, empty space, unreadable glyphs, or wrong z-order.
- After each tap, `describe-all` again before the next action — a tap can miss, dismiss an
  unrelated system alert, or navigate further than expected, and you need to know where you
  actually landed.

## Gotchas

- **Shells that don't word-split an unquoted variable** (zsh, by default) will pass
  `"$xy"` as one argument and fail with `invalid int value` if you built a coordinate string
  like `xy="201 488"`. Pass literal integers, or force splitting (`${=xy}` in zsh).
- **`idb` must be on `PATH`** for any MCP or wrapper tool that shells out to it — without it,
  taps fail with `spawn idb ENOENT` even though a plain screenshot still works (screenshot can
  go through `simctl` alone; tapping cannot).
- **One booted simulator serializes all driving.** Don't run two agents or two audit
  sessions against the same simulator concurrently — their taps collide.
- **Stress layout deliberately**: `xcrun simctl ui <udid> content_size
  accessibility-extra-extra-extra-large` then relaunch to test Dynamic Type; reset with
  `content_size large`. `appearance dark|light` for color scheme. System alerts (permission
  prompts, sign-in sheets) persist across an app relaunch — dismiss them before reading the
  app underneath.
- **Reaching a hard-to-blind-tap end state** (a puzzle win, a multi-step checkout): if the app
  has a debug-only launch argument or hook that seeds a near-terminal state, use it rather than
  trying to solve the app's own logic via taps — that's testing your tapping, not the UX.

## What to probe (this is what snapshots miss)

- **Negative / offline paths**: airplane mode mid-flow, cloud account signed out, retry after
  a failed network call, a purchase-restore with nothing to restore. Core functionality should
  rarely hard-gate on an optional cloud/account state — verify it doesn't.
- **"Online but signed out" is not the same as "offline" — test both.** For any
  cloud-backed screen, these diverge: offline, network calls fail fast (they throw
  immediately, no connection to wait on); online-but-signed-out, the same calls can **hang**
  (a real network round-trip stalls waiting on an unauthenticated container that never
  resolves). A pass under airplane mode can mask a hang that only reproduces online.
- **Account-gated features need a real signed-in test account** in the simulator — a
  cloud-save resume affordance or a leaderboard, for instance, may by design show nothing when
  signed out, which is correct behavior, not a bug; don't flag graceful degradation as broken
  without first confirming the same flow works signed in.
- **Navigation / modals**: does the destination screen actually appear after a selection; does
  a close/leave action show its confirmation; back-stack behavior after several pushes.
- **Safe area / Dynamic Island**: overlay or completion content clipped or overlapping system
  chrome on a notch/island device — invisible to a fixed-frame snapshot.
- **End-to-end completion**: a full success and a full failure path, including any step that
  submits to an external service that might be unavailable.

File each finding with its screenshot as evidence and a repro; label it environmental (stale
build, wrong account state) versus a genuine bug, and re-verify on a fresh, correctly-built
install before reporting it as real.

## Rationale

A snapshot test proves a view renders correctly *given* a state; it says nothing about
whether the app ever reaches that state through real interaction, or how it behaves at the
literal edges of a physical device (notch, Dynamic Island) that a fixed test harness frame
doesn't model. Driving the actual Simulator is the only check that covers the seam between
"the view is correct" and "the user can get there."

## Deviation considerations

- **No Simulator access (Linux CI, headless-only environment)**: this skill doesn't apply;
  rely on `host-driven-xcuitest-e2e` for automated coverage and snapshot tests for pixel
  regressions instead.
- **A pure macOS (AppKit/SwiftUI-Mac) app**: `idb` targets iOS/iPadOS/tvOS simulators only;
  drive a Mac app with `host-driven-xcuitest-e2e`'s window-frame-click pattern instead.

## Common Mistakes

1. **Tapping from screenshot pixel coordinates** instead of `describe-all` point coordinates
   — taps land at the wrong spot on any non-1× device.
2. **Reporting a bug from a stale installed build** — always confirm the running version first.
3. **Treating "online + signed out" and "offline" as one case** — they exercise different code
   paths (fail-fast vs. hang) and must both be driven separately.
4. **Running two sim-driving sessions against one booted simulator** — taps interleave and
   corrupt both audits' results.
5. **Chasing a worktree-only launch crash as a code bug** when the project keeps build secrets
   outside version control — rule out the environment first.

## Review Checklist

- [ ] `idb list-targets` confirms the target simulator is booted before driving starts.
- [ ] Installed build version checked and matches the intended commit/build.
- [ ] Every tap coordinate came from a fresh `describe-all`, not a screenshot pixel estimate.
- [ ] Every screenshot was actually viewed, not just captured.
- [ ] Both offline and online-signed-out variants driven for any cloud-backed screen.
- [ ] Safe-area / Dynamic-Island framing checked on a notch/island-class device.
- [ ] Each reported finding has a screenshot + repro steps and is labeled bug vs. environmental.

## Related skills

- `host-driven-xcuitest-e2e` — turn a finding from this audit into an automated, CI-runnable regression test.
- `swift-testing-baseline` — the static snapshot-testing layer this skill complements, not replaces.
- `ios-accessibility-engineering` — Dynamic Type / VoiceOver checks that pair naturally with this audit loop.
