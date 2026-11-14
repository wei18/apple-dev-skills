# Fresh-context acceptance check

A fresh subagent verifies another agent's claim that a change is done. Never dispatch it to the agent that produced the change. The producer's report is the claim under test, not evidence.

## Dispatch

Give the checker:

- The producer's report, verbatim. If the report is a file path, the checker reads the file first.
- The commit SHA under test, and the PR number when there is one.
- Each acceptance condition, with how to gather its evidence: read the result back, run the tests, run the affected flow, or compare `git show --stat` with the claimed files and sizes.

## Before running anything

1. **Check the head.** With a PR, run `gh pr view <n> --json headRefOid`. If it differs from the SHA in the dispatch, report the mismatch and give no verdict. A reading applies only to the tree it ran on, and so does a verdict.
2. **Isolate the commit.** Other sessions may switch branches or write files in the same checkout. Run `git worktree add --detach <scratch-path> <sha>`, check there, then `git worktree remove <scratch-path>`. Do not copy the working directory.

## Writing acceptance conditions

- **State an invariant and how to derive it, not a count.** "Every public type in the module has a doc comment" survives correct new work. "39 types have doc comments" fails the moment correct work adds a 40th type.
- **Put the condition where the quantity can change.** If the quantity cannot change at that layer, the condition produces a vacuous assertion or a fixture that fakes the change. Move it to a layer where the quantity varies.
- **Give every count its command and its blind spot.** Name the command that produced the number and what the number cannot detect. If a test runner's total includes skipped tests, an unchanged total proves only that no test disappeared, not that any ran. Add "list the skipped tests by name; none of the tests this change adds is on the list".
- **A gate needs a negative test.** For a config, CI, or gate change, break one checked item on purpose, confirm the gate goes red, then revert. A gate never seen failing has not been shown to check anything.
- Check that every path and link the report cites exists, and spot-check falsifiable claims (versions, API behaviour) against their source.
- Run the diff-scope TODO sweep from `phase-todo-sweep.md` and match each hit against the report.

## Report

Per condition, one of:

- `PASS`, with the evidence.
- `FAIL`, with the evidence and the location.
- `CANNOT VERIFY`, with what is missing.

Keep three run states apart and never merge them into "green": **ran and passed**, **ran but could not fail** (for example a gate with no negative test, or an assertion the input cannot violate), and **not run**.

End with `ACCEPT` or `REJECT`. A REJECT is specific enough that the producer can fix the change from it directly.
