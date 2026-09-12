# Worktree base correctness and recovery

## Pre-dispatch base correctness (verify the worktree base before you dispatch)

`isolation: "worktree"` does **not** always branch from your current local HEAD. The base is
decided by `worktree.baseRef`:

| `baseRef` | Branches from | Invisible to the worktree | Pre-dispatch action |
|---|---|---|---|
| `"fresh"` (default) | The repository's **default branch on the remote** (typically `origin/main`) | Any commit you haven't pushed yet | Push first, or set `worktree.baseRef: "head"` in settings |
| `"head"` | Your local HEAD **commit** | Uncommitted working-tree edits (gitignored files can still be copied via `.worktreeinclude`) | Commit first; confirm with `git log --oneline -3` before dispatching, especially right after a merge (see the incident below) |

Two fallbacks worth knowing: with no remote configured, or when `origin/HEAD` isn't cached
locally and can't be fetched, `"fresh"` falls back to your current local HEAD. And **before
v2.1.208**, `"fresh"` used whatever `origin/HEAD` was already cached locally, without fetching
a current one. Official docs:
https://code.claude.com/docs/en/worktrees#choose-the-base-branch

**Before dispatching, confirm the base:**

```bash
git rev-parse --abbrev-ref HEAD          # on the branch you think you are?
git log --oneline -3                     # does it include the commit/PR this work depends on?
git merge-base --is-ancestor <dep-sha> HEAD && echo "base OK" || echo "STALE BASE"
```

If the work depends on a just-merged PR, sync first (`git checkout main && git fetch && git reset --hard origin/main` — `reset --hard` discards uncommitted local changes, so commit them to a WIP commit or `git stash push -u -m <tag>` first — never a bare `git stash`/`pop` in a worktree session, since the stash stack is shared across worktrees) THEN dispatch. To restore a tagged stash afterward: find its current `stash@{n}` by tag with `git stash list --format='%H %gs'`, restore with `git stash apply <sha>` (not `pop`), then `git stash drop <sha>` once you've confirmed the apply succeeded. `<dep-sha>` above is the commit your work depends on (e.g. the merged PR's commit on `main`). State the expected base SHA in the dispatch prompt and tell the agent to verify it (`git log --oneline -5`; confirm a key file/symbol exists) before coding.

> Real incident (pre-v2.1.208 / local-HEAD-fallback behavior): a DEBUG test-hook subagent was dispatched right after a fix merged to `main`, but the dispatching HEAD was a pre-merge commit. The worktree branched from the stale base, so the new code referenced an `init` parameter and a file that only existed post-merge → 2 compile errors that the agent's own package build hadn't surfaced. Cost a full cherry-pick-onto-correct-base + rebuild cycle.

## Two traps specific to resuming an agent

- **A resumed agent isn't necessarily still where you think it is.** Don't trust that a
  resumed subagent is on the directory/branch it started on — verify `pwd` + `git rev-parse
  --abbrev-ref HEAD` before trusting its next commit.
- **A worktree's index can hold ghost entries pointing at pruned objects.** This surfaces as
  `invalid object … Error building trees` on commit. Recover with `git read-tree origin/main`.
