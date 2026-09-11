# Phase TODO sweep checklist

A separate close-the-loop activity that fires **once per phase** (not once per review round): before the Leader signs off on a phase-completion PR, run a sweep against the phase's diff scope to catch deferred-and-forgotten debt.

**Command** (Leader-run; against the phase's diff scope, not the full repo — `<base>` is
the commit/branch the phase started from, e.g. `main` or the phase's starting SHA):

```
git diff --name-only <base>..HEAD | xargs -r rg -n --no-heading -e 'TODO|FIXME|XXX|HACK|stub|placeholder'
```

If `rg` isn't installed (it isn't pinned in this repo's `.mise.toml`), use the `grep` fallback:

```
git diff --name-only <base>..HEAD | xargs -r grep -rnE 'TODO|FIXME|XXX|HACK|stub|placeholder'
```

Add your own project's phase-marker string to the pattern if it has one (e.g. `|Phase [0-9]+ Part` for a project that labels work-in-progress chunks that way).

Both forms scope to the files the diff actually touched — a file outside the phase's
diff is out of scope for this sweep even if it contains a match.

**Disposition rule** — every match must fall into exactly one bucket; otherwise the phase is not complete:

1. **Resolved this phase** — fixed or implemented before merge.
2. **Moved to §Backlog** — routed to the topic-appropriate document's §Backlog section (product → `design.md`, engineering → `foundations.md`, implementation step → `plan.md`, collaboration → `methodology.md`), and the §Backlog entry **cites the source `file:line`** so the debt is traceable.
3. **Intentionally left** — documented in the phase meeting log as "intentionally left, see <follow-up issue / phase reference>".

**Stub / placeholder code without a literal TODO comment still counts.** Identifier names like `xxxPlaceholder`, `xxxStub`, or scaffolding values that are not real implementations must be flagged in the phase log even if the regex didn't catch them via comment text.

**Ownership**: the Leader runs the sweep. Subagents may flag debt during implementation (in their impl-notes open-questions section — see `agent-impl-notes-log`), but closing the loop before phase merge is non-delegable. A PR reviewer subagent dispatched for the phase-completion PR should also run the sweep against the diff and report findings as MAJOR (unless already documented per the disposition rule above).

**When to invoke**:
- Before declaring a phase complete.
- When dispatching a Code Reviewer subagent on a phase-completion PR — include this command in the review brief's checklist.
- When auditing whether a previously-declared "complete" phase actually was.

**Anti-pattern**: marking a regex match as "obviously fine, ignore" without writing the disposition down. The point of the sweep is the paper trail; an undocumented justification is indistinguishable from forgetting.
