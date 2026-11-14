Sources backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Source | URL | Backs |
|---|---|---|
| `xcrun simctl help` (Xcode 27.2) | local tool help | A `<device>` argument takes a UDID or `booted`; with several devices booted, `booted` "will choose one of them"; `create <name> <device type id> [<runtime id>]`; `delete <device> \| unavailable \| all` |
| `xcrun simctl help create` (Xcode 27.2) | local tool help | Without a runtime, the newest runtime compatible with the device type is chosen |
| Tuist CLI, `tuist generate run` | https://tuist.dev/en/docs/cli/generate/run | The `--no-open` flag ("Don't open the project after generating it") and the `TUIST_GENERATE_OPEN` environment variable. The page does not state the default; opening by default is observed behaviour (Tuist 4) |
| `apple-skills` changelog, 2026-09-26 entry | https://github.com/Prisma-Labs-Dev/apple-skills (`CHANGELOG.md`) | Removal of `simulator-utils` because driving simulators directly "collides with other sessions on a shared Mac" |

Claims no official page states (practice observations, stamped in the skill body):

- Two `xcodebuild test` runs on one simulator producing mass `Crash: <App> at XCTWaiter` failures.
- A signed-in simulator failing signed-out unit tests.
- The build-database "database is locked" error when two builds share one DerivedData folder.
- Stale `XCBuildData` causing `There is no XCFramework found at <path>` after a binary dependency bump.
- The load-average and free-disk thresholds. They are one machine's working values, not measured limits.
- The disk sizes, the APFS clone double-count under `XCTestDevices`, and the swap volume in `references/disk-hotspots.md`.
- The runtime and device-type availability noted for Xcode 27.2.
