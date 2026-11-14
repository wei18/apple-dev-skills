# Disk hotspots for Apple development on macOS

Where build and simulator data accumulate, and how to measure it fast. macOS counts all of it
as "System Data" in Settings. Sizes are one 228 GB Mac with several agent sessions, measured
2026-11-04; yours will differ.

Scan these paths directly. A full `du ~` took over 10 minutes on that Mac, and macOS has no
`timeout` command to bound it.

| Path | Typical size (example) | How to free it | Notes |
|---|---|---|---|
| `~/Library/Developer/CoreSimulator/Devices` | 30 to 45 GB | `xcrun simctl delete <UDID>` per simulator you own | The largest item when sessions leave simulators behind. |
| `~/Library/Developer/XCTestDevices` | `du` showed 62 GB | Deleting freed almost nothing | Parallel-testing clones. They are APFS clones that share blocks with `Devices`, so `du` counts the shared blocks twice. |
| `~/Library/Developer/Xcode/DerivedData` | 25 to 35 GB | Delete folders for checkouts that no longer exist | One folder per checkout path. Worktrees built without `-derivedDataPath` land here and stay after the worktree is gone. |
| DerivedData under agent scratch directories | 3 to 8 GB per session; 34 GB in total once | Delete with the session | Was the fastest grower on that Mac, often larger than Xcode's own DerivedData. Building into the worktree avoids it. |
| `~/Library/Developer/Xcode/iOS DeviceSupport` | 6.4 GB | Delete old OS versions | Grows again each time a device connects. |
| Simulator runtimes | 14.8 GB for two runtimes | `xcrun simctl runtime list`, then `xcrun simctl runtime delete <id>` | Remove runtimes no project targets. |
| Tool caches with no recent use (`~/.gradle/caches`, `~/.cache/*`) | about 1.5 GB each | Delete; they regenerate | Check for recent activity first. |

Not worth scanning on that Mac: `/private/var/vm`, `~/Documents`,
`~/Library/Application Support`.

## Swap

Swap lives on an APFS VM volume, not in `/private/var/vm`, so `du /private/var/vm` misses most
of it (about 2 GB shown while 17.2 GB was in use, with 7 simulators booted). Check it with:

```bash
sysctl vm.swapusage
diskutil apfs list | grep -A1 '(VM)'
```

Shutting simulators down or rebooting frees it. `xcrun simctl shutdown all` affects every
session, so leave that decision to the user and shut down only your own UDIDs.

## Measuring

- Used space: `df -k /` size minus available. The APFS "Used" column is wrong.
- Free space for a build gate: `df -h /System/Volumes/Data`, `Avail` column.
- After a deletion, compare `df` before and after. `du` on APFS clones overstates what a
  deletion frees.
