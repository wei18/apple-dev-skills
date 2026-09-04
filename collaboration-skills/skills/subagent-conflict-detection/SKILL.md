---
name: subagent-conflict-detection
description: 'Use before dispatching a subagent with `isolation:"worktree"`, or while another subagent is in flight, to avoid three dispatch hazards — file-scope overlap with an in-flight subagent, a stale dispatch base, and collisions with another live agent/session editing the same checkout or git-submodule path. Invoke when about to call the Agent tool with `isolation:"worktree"`; when another subagent is running; right after a merge or branch switch (verify the dispatch base first); or when another Claude session is editing a shared repo/submodule path.'
---

# Subagent Conflict Detection

## When to invoke

Before dispatching a new subagent via the Agent tool — especially with `isolation: "worktree"` — if ANY other subagent is currently running or has an active worktree.

Trigger phrases / situations:
- "派 subagent" / "dispatch a subagent" / "再派一個" while a prior subagent is in flight
- About to call `Agent` tool when `git worktree list` shows non-main worktrees
- Multiple `[in_progress]` tasks in TaskList that involve subagent work

Skip when: dispatching the first subagent in a session, or all prior subagents have completed AND their worktrees are cleaned/merged.

## The pattern (3-step pre-dispatch check)

### Step 1 — inventory in-flight subagents

```bash
git worktree list | grep -v "\[main\]" | awk '{print $1}'
```

For each worktree path, capture:
- Branch checked out
- Dirty files: `git -C <path> status --short`
- Most recent commit subject: `git -C <path> log -1 --format=%s`

### Step 2 — enumerate the NEW dispatch's likely file scope

Read the planned subagent's task prompt. Extract:
- Explicit file paths it'll edit (usually under "Mission" / "Required reads to edit" sections)
- Likely-touched files via the task domain (e.g. "Settings redesign" → `Sources/.../Settings/`)
- Test files it'll add or modify

### Step 3 — compute intersection

For each in-flight subagent's dirty-file set vs the new dispatch's likely scope:
- **Direct overlap** (same file path): BLOCK dispatch, surface to user. Options: serialize (wait for in-flight to merge) OR carve scopes (rewrite new dispatch's prompt to exclude overlapping files).
- **Module overlap** (same target directory but different files): WARN but allow with `isolation: "worktree"`. Note in dispatch prompt: "in-flight subagent X is editing target Y; do not touch files Z."
- **No overlap**: dispatch safely.

### Non-file exclusive resources also conflict

The intersection check above only reasons about file paths, but a **booted Simulator** is
just as exclusive a resource as a file: pre-assign a UDID per subagent in the dispatch prompt
rather than letting each agent boot/pick one implicitly. Some `simctl` settings are **device-global**,
not per-app — `xcrun simctl ui <udid> appearance|content_size` changes the whole device's state,
so agent A switching to dark mode or Dynamic Type contaminates agent B's screenshots if they
share a simulator (see `interactive-simulator-ux-audit` for the driving pattern this protects).

## Pre-dispatch base correctness (verify the worktree base before you dispatch)

`isolation: "worktree"` does **not** always branch from your current local HEAD. The base is
decided by `worktree.baseRef`:

- **`"fresh"` (the default)** — branches from the repository's **default branch on the
  remote** (typically `origin/main`), not your local HEAD. Any commit you haven't pushed yet
  is invisible to the worktree. If the dispatched work depends on your in-progress local
  branch, push first, or set `worktree.baseRef: "head"` in settings.
- **`"head"`** — branches from your local HEAD, dirty state included. Dispatching right after
  a merge without syncing HEAD first branches from the pre-merge base (see the incident
  below). Confirm with `git log --oneline -3` before dispatching.

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

If the work depends on a just-merged PR, sync first (`git checkout main && git fetch && git reset --hard origin/main` — `reset --hard` discards uncommitted local changes, so stash them first) THEN dispatch. `<dep-sha>` above is the commit your work depends on (e.g. the merged PR's commit on `main`). State the expected base SHA in the dispatch prompt and tell the agent to verify it (`git log --oneline -5`; confirm a key file/symbol exists) before coding.

> Real incident (pre-v2.1.208 / local-HEAD-fallback behavior): a DEBUG test-hook subagent was dispatched right after a fix merged to `main`, but the dispatching HEAD was a pre-merge commit. The worktree branched from the stale base, so the new code referenced an `init` parameter and a file that only existed post-merge → 2 compile errors that the agent's own package build hadn't surfaced. Cost a full cherry-pick-onto-correct-base + rebuild cycle.

## Two traps specific to resuming an agent

- **A resumed agent isn't necessarily still where you think it is.** Don't trust that a
  resumed subagent is on the directory/branch it started on — verify `pwd` + `git rev-parse
  --abbrev-ref HEAD` before trusting its next commit.
- **A worktree's index can hold ghost entries pointing at pruned objects.** This surfaces as
  `invalid object … Error building trees` on commit. Recover with `git read-tree origin/main`.

## Coexisting with another live agent / session on the same repo

When ANOTHER Claude session (or human) is actively editing the same working checkout — or a **git submodule** vendored into your repo (e.g. a shared `.claude/skills/<plugin>` submodule) — do NOT edit that shared checkout in place. Two writers on one working tree clobber each other's uncommitted edits, fight over branch HEAD, and produce confusing diffs.

Instead, collaborate through isolation + PR:

1. Add your own worktree of THAT repo, branched from its `origin/main` (not the shared checkout's possibly-dirty local state):
   `git -C <shared-repo-or-submodule-path> fetch origin && git -C <…> worktree add /tmp/<name> -b <branch> origin/main`
2. Make your edits in the isolated worktree.
3. Commit, push the branch, open a PR on that repo. Let the normal review/merge flow integrate it.
4. For a submodule: after the upstream PR merges (and is tagged, if the consumer pins tags), bump the submodule pointer in the consuming repo via a SEPARATE PR — never hand-edit the submodule's checked-out files from the parent repo.

This is the cross-session mirror of the within-session conflict check: same goal (no two writers on one tree), different scope (independent sessions / submodules rather than your own in-flight subagents). When unsure whether another agent is on a path, treat it as occupied and use the worktree+PR path — it's cheap insurance.

## Output format

When overlap detected, present to user:

```
⚠️ Conflict detected between new dispatch and in-flight subagent:

In-flight: <subagent-id> editing:
  - <file 1>
  - <file 2>

New dispatch would touch:
  - <file 1>  ← OVERLAP
  - <file 3>

Options:
1. Serialize — wait for in-flight to merge, then dispatch
2. Carve — rewrite new dispatch prompt to exclude overlapping files
3. Proceed anyway — risk: subagent commits compete on push
```

## Anti-patterns this prevents

- **Parallel-dispatch race** (methodology.md §Anti-patterns): Two subagents on isolated worktrees edit the same file. `--force-with-lease` does NOT silently overwrite — it rejects the push when the remote ref has moved since the client last fetched. The real footgun is a different one: worktree B rebases onto a stale base (e.g. the main SHA from before worktree A pushed), producing a divergent history; resolving it then requires a force-push that can drop worktree A's commits. Prevent this by serializing or carving scopes before dispatch.
- **Lost-work on worktree wipe**: Subagent A's worktree wipes without commit; subagent B's dispatch reuses the path or branch name; A's work is unrecoverable.
- **Code Reviewer confusion**: CR sees a PR whose diff includes changes from a parallel subagent that's not yet merged; verdict is on wrong baseline.

## Integration with methodology.md

This skill operationalizes `docs/methodology.md §派發契約` item 9 (Leader pre-flight). The pre-flight checklist explicitly lists "kill orphan procs" + "rebase WIP onto main" + "mise trust" — this skill adds the conflict-detection step before those. For why `mise trust` is required before `mise install`/`mise exec` take effect in a fresh worktree or CI checkout, see `mise-tool-management`.

## False-positive handling

If `git worktree list` shows stale entries (worktree dir gone but git registration alive), they are NOT a conflict source — they just need `git worktree prune`. Don't block dispatch on stale registrations; check `ls <worktree-path>` to confirm the directory actually exists before computing dirty-file intersection.

## Example application

```
Leader is about to dispatch: "Senior Developer for error funnel refactor — files: AppComposition/Live.swift, AppUI/Root/RootViewModel.swift, Tests/RootViewModelTests.swift"

`git worktree list` shows in-flight subagent `agent-abc123` editing:
  M Sources/AppUI/Components/MonetizationStateController.swift

Intersection: NONE (different AppUI subdir).

Verdict: dispatch safely. Note in prompt: "in-flight subagent on MonetizationStateController — do not touch that file."
```

## Related skills

- `github-contribution-workflow` — routes worktree/submodule collision questions here; that skill owns PR/branch mechanics, this one owns pre-dispatch and cross-session conflict checks.
