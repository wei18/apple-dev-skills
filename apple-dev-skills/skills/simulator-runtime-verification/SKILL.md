---
name: simulator-runtime-verification
description: >
  Verify on an iOS Simulator the runtime behaviour unit tests cannot reach, and avoid the
  traps that fake a result: APNs device tokens and pushes (`simctl push`), Universal Links and
  custom-scheme sign-in returns (`simctl openurl`), Keychain writes, seeded `UserDefaults`, ATT
  and permission resets, and an old-build-to-new-build upgrade install. Use when a check must prove push registration,
  deep-link or sign-in return handling, or persisted state surviving an app update; when
  probing a framework API such as `UNNotificationAttachment` without a device; when a Simulator
  Keychain write fails with -34018 (`errSecMissingEntitlement`); or when a Simulator result
  looks like a regression. The idb UX audit loop → interactive-simulator-ux-audit; scripted UI
  tests → host-driven-xcuitest-e2e.
---

# Simulator Runtime Verification

Recipes for proving app behaviour that only exists at runtime (push registration, link
handling, Keychain and `UserDefaults` state, permission prompts, upgrade installs) on an iOS
Simulator, run from the main session with `xcrun simctl`, `lldb`, host `defaults`, `strings`
and a local HTTP server. Most of the traps below do not fail loudly. They produce a wrong
verdict: a regression that is not there, or a pass that proves nothing.

Version stamps give the Simulator runtime and date each behaviour was observed on. "Observed
once" means one sighting; re-check it on your runtime before you rely on it.

## When to invoke

- A change touches push registration, notification presentation, or a Notification Service
  Extension, and the PR claims it was verified.
- A change touches Universal Link, custom URL scheme, or sign-in redirect handling.
- A change touches stored state (`UserDefaults`, Keychain) and must keep working when a user
  updates from the previous release.
- A Simulator Keychain call returns `-34018`, or sign-in succeeds on the server but the app
  stays signed out.
- A Simulator result looks like a regression and you need to rule out the environment first.
- You need to know how a framework API behaves for a given input, and a device round trip is
  too slow.

## Scope

Owns: runtime verification recipes on a booted Simulator and the false-result traps around
them. Does **not** own:
- Driving the UI to audit a UX flow (taps, accessibility tree, screenshots, Dynamic Type) →
  `interactive-simulator-ux-audit`. That skill runs as a fork restricted to `idb`,
  `xcrun simctl` and Read, so it cannot run the `lldb`, `defaults`, `strings` or HTTP-server
  steps here.
- Pinning a verified behaviour as a CI regression test → `host-driven-xcuitest-e2e`.
- Creating, addressing and deleting the simulator, DerivedData per worktree, and build gates
  when other agent sessions share the Mac → `parallel-agent-xcode-hygiene`.
- Plain build, install and launch commands → `xcode-build-skill:xcode-build`.

Placeholders used throughout: `<UDID>` (a simulator you created for this check), `<bundle-id>`
(for example `com.example.app`), `<App>` (the product name).

## False-result traps: check these before you report

| Symptom | Real cause | Check or fix |
|---|---|---|
| Foreground push banner never appears; presentation looks broken | The process was started with `simctl launch --wait-for-debugger` (`-w`), or `lldb` attached and detached. Observed in one session, 4 of 4 attempts (2026-11-05, iOS 27.0 runtime). | `xcrun simctl terminate`, then `xcrun simctl launch` without `-w`. Judge presentation only on a normally launched process. |
| A value seeded for the upgrade test is ignored by the new build | `xcrun simctl spawn <UDID> defaults write <bundle-id> …` writes the Simulator's own preferences domain, not the app's data container. | Write the container plist path (see "Seed and read `UserDefaults`"). |
| Keychain write fails with `-34018`; sign-in succeeds on the server but the app stays signed out | The build ran with `CODE_SIGNING_ALLOWED=NO` or `CODE_SIGN_IDENTITY=""`, which leaves the binary without its entitlements. | Rebuild signed (default or ad hoc), then confirm with `strings` (see "Keychain"). |
| `codesign -d --entitlements :- <App>.app` prints no entitlements for a Simulator build | A Simulator build does not report its entitlements this way. Apple's `errSecMissingEntitlement` page also says to inspect a build for a hardware target with `codesign`, not a Simulator build. | Do not treat the empty output as proof either way. Use the `strings` check. |
| No device token, or the ATT prompt appears before the notification prompt | First launch on a freshly created simulator. The base-branch build behaved the same (observed once, 2026-11-04, iOS 27.0 runtime). | Reinstall on the booted simulator (see "Push"), and compare against the base build before you call it a regression. |
| A Universal Link opens Safari, not the app | `simctl openurl https://…` is unreliable on a fresh simulator, or the system has not fetched the `apple-app-site-association` file yet. | Use the tap path from a web page, and reboot the simulator if links never open the app. |
| A preference read right after `simctl terminate` shows the old value | The app's last write had not reached the plist yet. | Wait a few seconds and read again. |

**Baseline rule.** Before you report a Simulator result as a regression, reproduce it with the
base-branch build on a simulator in the same state. If the base build does the same thing, it
is the environment or an existing bug, not the change.

## Recipes

### Push: device token and notifications

- Simulators register with the APNs **sandbox** and receive real device tokens (Xcode 14 and
  later, iOS 16 or later simulators, macOS 13 or later on Apple silicon or T2 Macs). Each token
  is unique to that simulator and Mac, and Simulator tokens can be longer than device tokens.
  Never hard-code a token length.
- A freshly created simulator's first launch can get no token. `xcrun simctl uninstall <UDID>
  <bundle-id>` and then `xcrun simctl install <UDID> <App>.app` on the already booted simulator
  produced a real token (observed once, 2026-11-05).
- To drive a token branch with a chosen value (empty, malformed, changed), call the delegate
  method from `lldb`. Keep the pause short, because the app's own network requests can time out
  while it is stopped:

  ```
  lldb
  (lldb) process attach --pid <pid>
  (lldb) thread select 1
  (lldb) expr -l objc -- (void)[[[UIApplication sharedApplication] delegate] application:(id)[UIApplication sharedApplication] didRegisterForRemoteNotificationsWithDeviceToken:(id)[[NSData alloc] initWithBase64EncodedString:@"<base64-token>" options:0]]
  (lldb) process detach
  ```

  `xcrun simctl launch` prints `<bundle-id>: <pid>`. The expression targets a UIKit app
  delegate. After detaching, relaunch normally before you judge any presentation (first trap
  above). The injection worked in two sessions (2026-11-04 and 2026-11-05, iOS 27.0 runtime).
- Local pushes: `xcrun simctl push <UDID> <bundle-id> payload.json` (top-level `aps` object, at
  most 4,096 bytes). Locally simulated pushes do **not** run a Notification Service Extension.
  Test the extension with a real push to the APNs sandbox, and test its file handling with an
  API probe (see below).
- A foreground banner is not in the app's accessibility tree. Take a screenshot about 1.5 s
  after the push (`xcrun simctl io <UDID> screenshot <path>.png`) and look at it.

### Universal Links

- The app needs the Associated Domains entitlement and the domain must serve
  `apple-app-site-association`. Since iOS 14 the system fetches that file through Apple's CDN
  when the app is installed. For a development server the CDN cannot reach, use the
  entitlement's alternate mode (`?mode=<alternate mode>` on the `applinks:` entry).
- `xcrun simctl openurl <UDID> https://<your-domain>/<path>` does not always open the app on a
  fresh simulator (observed once, 2026-11-04, iOS 27.0 runtime), and it is not the path a user takes.
- Tap path that worked (observed in two sessions, 2026-11-04 and 2026-11-05): serve a page that
  links to `https://<your-domain>/<path>` with `python3 -m http.server <port>` from a scratch
  directory, open `http://localhost:<port>/` in the simulator's Safari, and tap the link. This
  is a cross-domain tap, which is what a Universal Link requires.
- Path from another app: write a contact `.vcf` with a URL field, run
  `xcrun simctl addmedia <UDID> contact.vcf`, and tap the URL in Contacts (observed once,
  2026-11-05).
- If links never open the app, reboot the simulator so the system fetches the association file
  again (observed once).

### Custom-scheme sign-in return

While the app's sign-in web sheet is open, run
`xcrun simctl openurl <UDID> '<app-scheme>://<callback-path>?code=<any-value>'`. This exercises
the app's return handling without a real provider round trip (observed once, 2026-11-05). It
proves the app-level URL handler only. If the app uses `ASWebAuthenticationSession`, its
completion handler receives the callback from inside the session, so an `openurl` from outside
does not test that path (inferred, not observed).

### Seed and read `UserDefaults`

1. While the simulator is booted, get the path:
   `P="$(xcrun simctl get_app_container <UDID> <bundle-id> data)/Library/Preferences/<bundle-id>"`
   (no `.plist` suffix; host `defaults` adds it).
2. Stop the app: `xcrun simctl terminate <UDID> <bundle-id>`.
3. Write with host `defaults`: `defaults write "$P" <key> <value>`. Read back with
   `defaults read "$P" <key>`.

Observations disagree on step 2. One full upgrade round worked with the app terminated and
the simulator still booted (observed once, 2026-11-02, iOS 27.0 runtime). Another run found the
write took effect only with the simulator **shut down** (observed once, 2026-11-06, runtime
unrecorded). The likely
mechanism is that the simulator's preferences daemon caches the domain and does not see a
host-side write while it runs (inferred, not confirmed). If a terminate-only write does not
show up, take the path in step 1, then `xcrun simctl shutdown <UDID>`, write, and boot again.

### Keychain

- Keychain access on the Simulator needs a signed build. A build with
  `CODE_SIGNING_ALLOWED=NO` or `CODE_SIGN_IDENTITY=""` fails with `-34018`
  (`errSecMissingEntitlement`): "Client has neither application-identifier nor
  keychain-access-groups entitlements" (observed 2026-11-02 and 2026-11-05, iOS 27.0 runtime).
- Build with the project's default signing. Without a team, ad hoc signing worked
  (observed once, 2026-11-05):
  `CODE_SIGN_IDENTITY="-" CODE_SIGN_STYLE=Manual DEVELOPMENT_TEAM="" PROVISIONING_PROFILE_SPECIFIER=""`.
- Check the entitlements in the binary itself. A signed Simulator build embeds them in an
  `__entitlements` section: `strings "<App>.app/<App>" | grep -A3 keychain-access-groups`
  should show your access group (observed 2026-11-02 on two apps, iOS 27.0 runtime).

### ATT and other permission resets

- `xcrun simctl privacy <UDID> reset all <bundle-id>` returned ATT to not-determined as well
  as the listed services (observed once, 2026-11-04, iOS 27.0 runtime; `simctl help privacy` on
  Xcode 27.2 does not name a tracking service). The command terminates the app when a change
  needs it, so relaunch before you check the prompt.
- Do not try to hold the app at "ATT not asked" with `lldb --waitfor` driven from a script. The
  piped session runs synchronously and the app's frameworks are not loaded yet, so breakpoints
  stay pending (observed once).

### Upgrade install (previous build to new build)

1. On a simulator you created for this check, install the base-branch build.
2. Seed state. `UserDefaults`: write the container plist (above). Keychain: sign in with a test
   account in the old build; no manual seeding is needed. Both builds must be signed.
3. Install the new build over it with `xcrun simctl install`. Do not uninstall first.
4. Stream the app's logs while it launches and look for decode or migration failures:
   `xcrun simctl spawn <UDID> log stream --predicate 'subsystem == "<subsystem>"'`.
5. The evidence is the UI showing the persisted account and values, plus a clean log.
6. Erase or delete the simulator afterwards. A signed-in simulator changes the results of later
   test runs.

Worked as one full round (2026-11-02, iOS 27.0 runtime). The common failure is seeding the
wrong `defaults` domain, which looks exactly like "the new build did not read the old value".

### Probe a framework API without a device

To learn how a framework API treats a given input (which files it accepts, which error it
returns), compile a small command-line program for the Simulator and run it there with
`xcrun simctl spawn`. Pass `-target`: without it, `xcrun -sdk iphonesimulator swiftc` targets
the host macOS triple (checked with `-print-target-info`, Swift 6.4.2, Xcode 27.2), so the probe
would test macOS instead. For the commands, the limits of a spawned process, and a worked
`UNNotificationAttachment` example, read `references/api-probes.md`.

## Rationale

These checks exist because the Simulator gives plausible-looking wrong answers. A missing
banner from a debugger-launched process, a seed written to the wrong domain and an unsigned
build that silently drops Keychain writes each produce a confident verdict that is false. A
verification report built on one of them is worse than no report, because reviewers stop
looking. Each recipe here names the check that separates the real result from the artifact.
The Simulator is still the right first tool: it is fast, scriptable, resettable, and receives
real sandbox device tokens.

## Deviation considerations

- **Behaviour the Simulator cannot show**: APNs production environment delivery, real network
  timing, and system prompt order on a real device. Verify these on a device and say in the
  report which items were device-checked.
- **A deployment floor below what the host can simulate**: older runtimes may not install on a
  current macOS and Xcode. Checks for that floor are device-only.
- **No Simulator in CI**: run these as manual pre-merge or pre-release checks, and move the
  ones that can be automated into `host-driven-xcuitest-e2e`.

## Common Mistakes

1. **Judging presentation on a debugger-launched process.** Relaunch without `-w` first.
2. **Seeding `UserDefaults` with `simctl spawn … defaults write <bundle-id>`.** It writes the
   Simulator's domain; the app never reads it.
3. **Building with `CODE_SIGNING_ALLOWED=NO` and then testing Keychain or sign-in.** The
   result is `-34018` and a sign-in that cannot stick.
4. **Trusting empty `codesign -d --entitlements` output for a Simulator build.** Check the
   binary with `strings`.
5. **Calling fresh-simulator first-launch behaviour a regression** without running the base
   build on the same fresh simulator.
6. **Testing a Notification Service Extension with `simctl push`.** Local pushes skip the
   extension.
7. **Building an API probe without `-target …-simulator`.** It runs as a macOS binary.
8. **Reusing the upgrade-test simulator for unit tests** while it is still signed in.

## Review Checklist

- [ ] Every presentation verdict comes from a process launched without `--wait-for-debugger`
      and with no `lldb` attached.
- [ ] Any suspected regression was reproduced with the base-branch build on the same simulator
      state.
- [ ] Builds used for Keychain or sign-in checks are signed, and `strings` shows
      `keychain-access-groups` in the binary.
- [ ] `UserDefaults` seeds were written to the container plist path and read back before the
      new build launched.
- [ ] Universal Links were opened by a tap (Safari page or Contacts), not only by
      `simctl openurl`.
- [ ] Notification Service Extension behaviour was not claimed from a `simctl push` test.
- [ ] Each observation in the report names the Simulator runtime, and device-only items are
      marked as such.
- [ ] The simulator used for upgrade or sign-in checks was erased or deleted afterwards.

## References

- `references/api-probes.md` — building and running a Simulator API probe, with the
  `UNNotificationAttachment` file-type example.
- `references/official-docs.md` — the official pages behind the claims above, and which claims
  no official page states.

## Related skills

- `interactive-simulator-ux-audit` — the idb-driven UX audit loop. Use it to find layout and
  flow bugs; use this skill when the question is whether runtime state or a system integration
  works.
- `host-driven-xcuitest-e2e` — turn a verified behaviour into a CI regression test.
- `parallel-agent-xcode-hygiene` — create the `<UDID>` simulator these recipes use, keep it
  to this session, and delete it with proof that the space came back.
- `oslog-logger-defaults` — the `Logger` subsystem the upgrade check's `log stream` filters on.
- `app-store-review-rejections` — the App Review side of ATT; its fresh-install ATT prompt
  check pairs with the permission reset above.
- `xcode-build-skill:xcode-build` (aggregated external) — plain build, install and launch
  commands.
