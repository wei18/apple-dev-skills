---
name: parallel-agent-xcode-hygiene
description: >
  Keep AI-agent sessions that build Apple apps on one shared Mac from corrupting each other's
  results or filling the disk. Each session owns a simulator addressed by UDID, a per-worktree
  `-derivedDataPath`, `tuist generate --no-open`, load and free-disk gates before `xcodebuild`,
  and cleanup proved with `df`. Use when about to run `xcodebuild`, or create, boot or pick a
  simulator, in a git worktree or beside other agents; when deciding whether to build locally
  or leave it to CI; when `xcodebuild test` reports mass `XCTWaiter` crashes or one session's
  result contradicts another's; or when the disk fills (No space left on device, System Data
  growing). Checking app behaviour on the simulator → simulator-runtime-verification.
---

# Parallel-Agent Xcode Hygiene

Rules for an agent that builds, tests or runs an Apple app on a Mac where other agent sessions
do the same at the same time. Each rule removes one way that sessions collide: a shared
simulator, a shared build folder, an unbounded build, or disk that nobody frees. The rules are
written for git worktrees, one per session, but apply to any shared checkout.

These rules stop the agent's own default actions (build here, use the booted simulator,
open the project), so no user request names them. Copy the lines in "Adopt in your project"
into the project's always-loaded instructions file so they hold even when this skill is not
loaded.

Thresholds are parameters. The worked examples come from one 8-core Mac with a 228 GB disk;
set your own numbers.

## When to invoke

- You are about to run `xcodebuild build` or `xcodebuild test`, or `tuist generate`, in a git
  worktree or on a Mac where other agent sessions run.
- You are about to create, boot, erase or pick a simulator.
- You must decide whether to build or test locally or leave it to CI.
- `xcodebuild test` reports hundreds of `Crash: <App> at XCTWaiter` failures, or a test result
  disagrees with the same test in another session.
- The disk is nearly full, a build fails with `No space left on device`, or macOS shows
  System Data growing.
- You are about to delete DerivedData, a worktree, or a simulator.

## Scope

Owns: resource ownership between sessions on one Mac (simulators, DerivedData, worktrees,
processes), the gates before a heavy build, the local-versus-CI build decision, and verified
cleanup. Does **not** own:
- What to check on a booted simulator, and the false-result traps there →
  `simulator-runtime-verification`.
- Driving the UI with `idb`, and how many simulators fit in RAM →
  `interactive-simulator-ux-audit` (its Preflight section and fleet-sizing reference).
- CI pipeline design → `xcode-cloud-single-track-ci`.
- Plain `xcodebuild` and `simctl` command syntax → `xcode-build-skill:xcode-build`.

Placeholders: `<UDID>` (a simulator this session created), `<session>` (a name unique to this
session), `<bundle-id>`, `<App>`.

## Adopt in your project

Rules that live only in this skill fire only when the skill loads. Put these lines in the
project's always-loaded instructions file (`CLAUDE.md`, `AGENTS.md`, or your agent's
equivalent), with your own numbers:

```markdown
- Simulators: create your own (`xcrun simctl create`), address it by UDID everywhere, never by name or `booted`, and delete it when done.
- Builds: pass `-derivedDataPath "$PWD/DerivedData"` from the worktree root. Never touch another session's DerivedData, worktree, or simulator.
- Before a heavy build: skip it and report if the 1-minute load average is above 2 × `sysctl -n hw.ncpu` or free disk is below <N> GB.
- Never open Xcode: `tuist generate --no-open`, no `open *.xcworkspace`, no `xed`. Details: the `parallel-agent-xcode-hygiene` skill.
```

## Ownership rules

| Resource | Rule |
|---|---|
| Simulator | Create one per session and use its UDID in every command. Never `name=<device>`, never `booted`, never a simulator you did not create. |
| DerivedData | One folder per worktree, inside the worktree. Never the default location, a scratch path, or another worktree's folder. |
| Worktree | Delete only worktrees this session created. |
| Processes | Kill only processes you started, matched by your UDID or path. |
| Machine-wide commands | Never `xcrun simctl shutdown all`, `erase all` or `delete all`, and never wipe the shared DerivedData folder. These belong to the user. |

When something that is not yours blocks you (a full disk, a stuck simulator), report it and
let the user decide. Do not delete it.

## Simulators: create, use by UDID, delete

1. Pick a runtime and device type that exist on this Mac:
   `xcrun simctl list runtimes` and `xcrun simctl list devicetypes`.
2. Create the simulator. `create` prints the new UDID:
   `UDID=$(xcrun simctl create "<session>" "<device type>" <runtime>)`.
3. Use the UDID everywhere:
   - `xcodebuild … -destination "platform=iOS Simulator,id=$UDID"`
   - `xcrun simctl <subcommand> "$UDID" …`
   - `idb … --udid "$UDID"`
4. Boot it only when a step needs a running simulator (install, launch, UI driving, tests).
   A build with no runtime check still passes `id=$UDID` and leaves the simulator shut down.
5. Delete it as soon as the session no longer needs it. See "Cleanup with proof".

`name=<device>` matches any simulator with that name, including one another session is
driving. The special `booted` value is worse. `xcrun simctl help` says that when several
devices are booted, simctl "will choose one of them" (Xcode 27.2).

Device types and runtimes differ by Mac and Xcode version. As one machine's observation
(Xcode 27.2, 2026-11-13): the iOS 27.0 runtime offered the regular iPhone device types; the
iOS 27.1 runtime offered only a foldable device type whose screen stayed dark under `idb`; iOS
17.0 installed for old-OS checks; iOS 15 and 16 runtimes would not install on that macOS.
Check your own list before you choose.

### Test isolation

- Run unit tests on a clean simulator that no manual check has used. A simulator that some
  other flow signed in to keeps that state, and signed-out tests then fail every time.
- Never run two `xcodebuild test` runs against one simulator. Both install the same host app
  under the same bundle ID and overwrite each other, which produces hundreds of false
  `Crash: <App> at XCTWaiter` failures. Test branches one after another, or give each run its
  own simulator.
- After a manual check, `xcrun simctl erase "$UDID"` before you run tests on that simulator.
- When you stream logs, scope any `pkill` to your simulator:
  `pkill -f "simctl spawn $UDID log stream"`. A bare `pkill -f "log stream"` ends every
  session's streams.

## DerivedData per worktree

- Pass `-derivedDataPath "$PWD/DerivedData"` from the worktree root on every `xcodebuild`
  call. Add `DerivedData/` to `.gitignore` and to the exclude lists of SwiftLint and
  SwiftFormat, or the linters scan the checked-out package sources inside it.
- The folder then goes away with the worktree. The default
  `~/Library/Developer/Xcode/DerivedData` keeps one folder per checkout path forever, and a
  folder under an agent scratch directory is invisible to whoever cleans up worktrees.
- Two builds that share one DerivedData folder fight over its build database. Xcode reports
  that the build database is locked and that there may be "two concurrent builds running in
  the same filesystem location".
- Delete your own `DerivedData` folder when the task is done or when you stop building for a
  while.
- **Stale build description after a binary dependency bump.** If a build reports
  `There is no XCFramework found at <path>` while the folder exists, the cached build
  description still holds the state from before the artifacts were present. Delete
  `DerivedData/<project>/Build/Intermediates.noindex/XCBuildData` and
  `DerivedData/<project>/SourcePackages/artifacts/extract`, then build again. You do not need
  to download the packages again (observed once, Xcode 27).

## Gates before a heavy build

A heavy build is a full `xcodebuild build` or `test`, or an archive. Run the gates before each
one, and run at most one heavy build per session at a time.

| Gate | Check | Threshold (parameter) | Worked example | When it fails |
|---|---|---|---|---|
| CPU load | `uptime`, 1-minute average | above 2 × `sysctl -n hw.ncpu` | 8 cores → do not start above 16 | Wait about 5 minutes and check again. After 3 failed checks, report instead of building. |
| Free disk | `df -h /System/Volumes/Data`, `Avail` column | below a floor that fits one clean build plus margin | 15 GB on a 228 GB disk | Do not start. Delete your own leftovers, then report. |

Measure used space as `df -k /` size minus available. Do not trust the APFS "Used" column.
To find where the space went, read `references/disk-hotspots.md`.

## Build locally or leave it to CI

When CI builds and tests every pushed branch, the default is to push and read the result
(`gh pr checks`, `gh run view --log-failed`). Local builds cost the shared CPU and disk that
other sessions need. Build locally only when one of these applies, and name the reason in your
report:

| Reason | Local action |
|---|---|
| The change edits project generation, build settings or xcconfig files, or adds a target or module | Debug build |
| CI failed twice in a row on a compile error | Debug build to iterate |
| The change touches release-only code (`#if !DEBUG`, a Release-only setting) | Release build with `-destination generic/platform=iOS` |
| The build regenerates a file you must commit, such as a String Catalog | Debug build once, commit the result → `ai-translated-localization` |
| The branch gets no CI (for example a pull request stacked on another branch) | Build locally. Leave tests until CI runs. |
| A change needs a runtime check on a simulator | Build, install, check → `simulator-runtime-verification` |

Do not run the full `xcodebuild test` locally when CI runs it. To reproduce one crash or flaky
test, run only that test with `-only-testing:<Target>/<Class>/<test>` and say why. Lint and
format checks (`swiftlint`, `swiftformat --lint`) are cheap and stay local.

## Never open Xcode from an agent

Tuist opens the generated workspace in Xcode unless you pass `--no-open` (Tuist 4). Always run
`tuist generate --no-open`, or set `TUIST_GENERATE_OPEN` to turn opening off. The same applies to any
generator or script that opens the result. Never run `open <App>.xcworkspace` or `xed`. Each
Xcode window starts indexing the project, which takes CPU and memory from every session, and
nobody closes it when the agent finishes.

## Cleanup with proof

A command that exits 0 is not proof that space came back. For each simulator you created:

1. Record free space: `df -h /System/Volumes/Data`.
2. `xcrun simctl shutdown "$UDID"`, then `xcrun simctl delete "$UDID"`.
3. Confirm that `~/Library/Developer/CoreSimulator/Devices/$UDID` no longer exists, and that
   `df` shows more free space than in step 1.
4. If either check fails, the simulator is not cleaned up. Report it.

Delete your own `DerivedData` folder and any temporary worktrees the same way, and report
the free space before and after.

## Rationale

Most collisions here produce a wrong answer, not an error. Two test runs on one simulator
look like a crash regression. A signed-in simulator fails tests that pass on a clean one. A
build that picked another session's simulator verifies the wrong install. A full disk stops
every session, not only the one that filled it. Owning resources by UDID and by path, and
proving each deletion, keeps one session's results its own.

The aggregated `apple-skills` plugin reached the same premise on its own: it removed its
`simulator-utils` skill because "it booted and drove simulators directly, which collides with
other sessions on a shared Mac" (`CHANGELOG.md` in
https://github.com/Prisma-Labs-Dev/apple-skills, 2026-09-26 entry).

## Deviation considerations

- **One agent session on its own Mac**: the ownership rules cost little and still apply when
  a human opens Xcode beside the agent. You can relax the load gate.
- **No CI, or CI that does not run tests**: build and test locally, but keep the gates and
  your own simulator. Run one heavy build at a time.
- **CI runner fleets**: a self-hosted runner that runs several jobs on one Mac has the same
  collisions. Give each job its own simulator and DerivedData folder, and delete both when the
  job ends.
- **A Mac with much more disk or cores**: raise the thresholds, but keep them as numbers you
  check, not a feeling.

## Common Mistakes

1. **`-destination 'platform=iOS Simulator,name=<device>'`** on a shared Mac. It can pick
   another session's simulator. Use `id=<UDID>`.
2. **Using `booted` in `simctl` commands** while other sessions have simulators booted.
3. **Two `xcodebuild test` runs on one simulator**, then reading the mass `XCTWaiter` crashes
   as a regression.
4. **Building without `-derivedDataPath`**, or into a scratch folder, so the output outlives
   the worktree and nobody deletes it.
5. **`tuist generate` without `--no-open`**, or `open`/`xed` on the workspace.
6. **Bare `pkill -f "log stream"`**, `simctl shutdown all`, or deleting another session's
   DerivedData to free space.
7. **Reporting a simulator as deleted from the exit code alone**, without the device-folder
   and `df` checks.
8. **Running the full test suite locally** when CI runs it, or building locally without
   naming the reason.

## Review Checklist

- [ ] Every `xcodebuild -destination`, `simctl` and `idb` command uses the UDID of a simulator
      this session created.
- [ ] Every `xcodebuild` call passes `-derivedDataPath "$PWD/DerivedData"` from the worktree
      root, and `DerivedData/` is gitignored and excluded from the linters.
- [ ] The load and free-disk gates ran before each heavy build.
- [ ] Each local build or test names the reason it could not wait for CI.
- [ ] `tuist generate` ran with `--no-open`; no Xcode window was opened.
- [ ] Each simulator this session created was deleted, its device folder is gone, and `df`
      shows the space returned.
- [ ] The report gives free space before and after cleanup.
- [ ] Nothing another session owns was killed, erased or deleted.

## References

- `references/disk-hotspots.md` — where build and simulator data accumulate on macOS, how to
  measure it quickly, and what deleting each one frees.
- `references/official-docs.md` — the sources behind the claims above, and which claims no
  official page states.

## Related skills

- `simulator-runtime-verification` — what to verify on the simulator this skill has you
  create, and the traps that fake a result.
- `interactive-simulator-ux-audit` — the `idb` audit loop and fleet sizing by RAM; pass it the
  UDID of a simulator you created.
- `host-driven-xcuitest-e2e` — scripted UI tests; give each run its own simulator.
- `xcode-cloud-single-track-ci` — the CI this skill hands builds and tests to.
- `mise-tool-management` — tool setup in a fresh git worktree (`mise trust`).
- `collaboration-skills:subagent-conflict-detection` — worktree setup and conflicts between
  parallel agents at the git level.
- `xcode-build-skill:xcode-build` (aggregated external) — plain `xcodebuild` and `simctl`
  syntax. Its examples pick a simulator by name and build into a temporary folder; apply the
  ownership rules above when you follow them on a shared Mac.
