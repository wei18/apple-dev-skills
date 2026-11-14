# Isolation traps that compile cleanly

Code in this list builds without a diagnostic under Swift 6 mode and fails at run time.
The general rules (actors, reentrancy, `assumeIsolated`) are in
`apple-skills:guide-swift-concurrency`; these are the narrower cases that show up when
existing code or Objective-C libraries meet strict concurrency.

| Trap | What happens | Fix |
|---|---|---|
| An Objective-C method with a completion block, called from an `async` context | The importer adds an `async` overload (SE-0297), and in an `async` context overload resolution prefers it (SE-0296). If the library calls the block only on a state change (for example "finished refreshing"), the `await` never returns when the object is already in the end state. Observed once with a pull-to-refresh library. | Call the variant without a completion block through a small synchronous wrapper (`extension Control { func endNow() { … } }`) and call the wrapper from tasks. |
| `MainActor.assumeIsolated` inside a `static let shared` initializer, or inside anything a lazy singleton touches first | `assumeIsolated` traps when the caller is not on the main actor. The first access to a lazy singleton can come from a third-party SDK's completion handler on a background thread. Seen twice (an SDK start callback, a network-client delegate bridge). | Touch the singleton on the main actor early in launch, or read the value from a non-isolated store instead of asserting isolation. |
| A manager whose calls must run in order (`onLogin` then `onLogout`) written as an `actor` | Callers wrap each call in `Task { await manager.onLogin() }`. Each task hops to the actor separately, so arrival order is not guaranteed, and a method that awaits lets the next call interleave (reentrancy). | Make it a `@MainActor final class` and chain the work: keep the previous `Task` and `await` it at the start of the next one. |

Check for these in review: a Swift 6 build that passes says nothing about any row above.
