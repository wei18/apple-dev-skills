---
name: pr-diff-verification
description: Use before pushing a branch or opening a PR to verify `git show --stat HEAD` matches what the commit message claims. Prevents the "commit log wrote but code didn't make it" class of accidents where the commit message describes changes that aren't in the diff (e.g. amend overwrote the previous commit's content, force-push lost commits, worktree wipe lost staged work). Invoke whenever Leader is about to `git push` a feature branch OR open a PR.
---

# PR Diff Verification

## When to invoke

Before:
- `git push` of a feature branch (especially after subagent return)
- `gh pr create`
- `gh pr merge` (final sanity)
- Force-push (`--force-with-lease`) of a rebased branch

Skip when: pushing a single trivial commit you authored line-by-line in the current session and didn't amend.

## The pattern (3-step verify)

### Step 1 — read the commit message claims

For the HEAD commit (or all commits on the branch since base), extract concrete claims:
- "modifies X" → look for X in the diff
- "adds Y" → look for `create mode 100644 Y/` in stat
- "deletes Z" → look for `delete mode 100644 Z` in stat
- "renames A → B" → look for `rename A => B` in stat
- "fixes N+M lines" → diff total should be in that ballpark

### Step 2 — compare against actual diff

```bash
git show --stat HEAD                    # for single commit
git diff --stat origin/main..HEAD       # for branch cumulative
git log --oneline origin/main..HEAD     # for commit count
```

For each concrete claim, grep the stat output. If the claim mentions a path that doesn't appear in the stat, that's a discrepancy — investigate before push.

### Step 3 — surface discrepancies

If found:
- Did `git amend` or rebase squash the wrong content?
- Did a worktree wipe lose commits before push?
- Did a force-push from another branch overwrite this branch's commits (the "push wrong ref" footgun)?
- Did the subagent return claim work that never got committed?

Discrepancy resolution options:
- Restore commits from reflog (`git reflog | grep <SHA>`)
- Cherry-pick the missing commits from a sibling branch
- Re-apply the lost edits manually
- Re-dispatch the subagent with explicit recovery instructions

## When the rule fired in this project

**"Commit log claims work, diff doesn't show it" (general pattern)**: this class of mistake recurs when (a) `git amend` after partial revert loses hunks but keeps the original message, (b) force-push from a stale branch overwrites newer commits, (c) subagent returns a structured "I committed X" report but the commits never made it to the branch ref due to worktree wipe before push. Each failure mode is caught by the same single check: `git show --stat HEAD` vs. the commit body.

**Real-world example — wrong ref pushed**: a subagent reported "1 commit a547d70 with all the changes"; Leader pushed `worktree-agent-XXX:feat/feature-phase1` and discovered post-push that the wrong ref was pushed (the worktree-agent ref was at main SHA; the actual feature commits were on a different local branch). Required force-push recovery from reflog.

## Anti-pattern this prevents

- **Lying commit log + invisible diff**: code review reads the message and assumes the code matches. Trust is misplaced; defects ship.
- **Force-push wrong ref**: `git push origin worktree-agent-X:feat/Y` pushes worktree-agent-X's HEAD to remote feat/Y. If worktree-agent-X doesn't have the commits (because they were committed to a different local branch by the subagent), remote feat/Y gets reset to whatever worktree-agent-X is at — usually main SHA.

## Integration with methodology

`docs/methodology.md §派發契約 §10` requires commit-early discipline. This skill is the POST-commit verification step — confirms the commits that survived actually contain what the message claims.

## Heuristics for "what to check"

Cheap signals:
- Total LOC: stat says +50 / -3; message says "1-line fix" → discrepancy
- File count: stat says 0 files changed; message says "refactored X module" → loud bug
- Specific filenames: message says "edit `Foo.swift:42`"; stat doesn't list `Foo.swift` → loud bug
- Squash sanity: `git log --oneline` should show 1 commit (post-squash) OR the chain you intended

Don't deep-read diffs as part of this skill — that's Code Reviewer's job. Just confirm the SHAPE matches the claims.

## Example application

```
Subagent returns: "3 commits, 11 files, +265/-272 LOC, all 7 wiring tests pass"

Leader runs:
  git log --oneline origin/main..HEAD   # should show 3 commits
  git diff --stat origin/main..HEAD     # should show ~11 files, ±540 line tags

If git log shows 1 commit (subagent squashed without saying) → OK if intentional
If git log shows 0 commits (commits lost to worktree wipe) → STOP, recover, re-push
If git diff --stat shows different file count → investigate
```
