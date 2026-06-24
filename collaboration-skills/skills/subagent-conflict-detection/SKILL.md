---
name: subagent-conflict-detection
description: Use before dispatching a new subagent to check that its target file set does not overlap with any in-flight subagent's working tree. Prevents the parallel-dispatch race where two subagents edit the same file via different worktrees and one's commit gets force-pushed over the other. Invoke when about to call Agent tool with isolation:"worktree" if any other subagent is currently running.
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

This skill operationalizes `docs/methodology.md §派發契約` item 9 (Leader pre-flight). The pre-flight checklist explicitly lists "kill orphan procs" + "rebase WIP onto main" + "mise trust" — this skill adds the conflict-detection step before those.

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
