---
name: subagent-review-cycles
description: The Leader / Developer / Code-Reviewer triad pattern — Leader dispatches Developer for proposal → Code Reviewer for adversarial review (with WebSearch, no CLI) → Leader accepts/rejects with specific reasons → iterate up to `limit(N)` rounds. Round-1 cosmetic-grade fixes get inline-applied by Leader instead of consuming a round. Invoke when planning multi-round review on a document, dispatching a Code Reviewer subagent, or when asked "how many review rounds / what skills should the Code Reviewer carry".
---

# Subagent Review Cycles

## When to invoke

- About to dispatch a sub-agent to draft a technical document / design section.
- The first version of a document is ready and a Code Reviewer should audit technical correctness.
- User asks "how many review rounds", "should Code Reviewer run CLI", "what counts as rejection".

## The triad

| Role | Job |
|---|---|
| **Leader** (main agent) | Dispatch, integrate review results, accept / reject, communicate with the user |
| **Developer** (subagent) | Draft / revise document sections; works after Leader replies with rejection. (The Developer role is often dispatched as a Software Architect sub-agent type when the task is architectural in nature, but the role name remains "Developer".) |
| **Code Reviewer** (subagent) | Audits Developer output for technical / API correctness and logic gaps; **CLI forbidden**, WebSearch allowed |

The Leader **never** writes the implementation / drafts a section directly — that's the Developer's job. The Leader **never** does the review either — that's the Code Reviewer's job.

## Round structure

```
round N:
  Leader → Developer: dispatch (scope + skills + inputs + return format + criteria)
  Developer → Leader: draft
  Leader → Code Reviewer: dispatch (review criteria + must use WebSearch, no CLI)
  Code Reviewer → Leader: BLOCKER / MAJOR / MINOR list
  Leader: ACCEPT / REJECT each item with explicit reason
  if accepted_count == total: done
  if N == limit: pause, report to user
  else: round N+1 with feedback
```

`limit(N)` is typically 3–5. **If the limit is reached without convergence**: pause, report to the user, wait for direction.

## The "round-1 cosmetic" pragmatic rule

If a round-1 result has **only spelling / formatting / paragraph order / string typo** cosmetic-grade fixes left:
- **Leader applies inline edits directly** instead of dispatching round 2 to the Developer
- Still record these fixes in the meeting log
- Reasoning: "limit is an upper bound, not a requirement"; burning a whole round just for typos is uneconomical

Criteria: the fix can be completed by the Leader in ≤ 5 minutes and involves **no new decisions**.

## Dispatch contract for Code Reviewer

Every Code Reviewer dispatch prompt must include:

1. **Target file / section scope** (explicit file + section)
2. **Forbidden tools**: CLI / Bash trial-and-error
3. **Allowed tools**: WebSearch / WebFetch (for verifying Apple APIs, library behaviour)
4. **Review criteria** (4 dimensions + domain-specific checklist):
   - Technical correctness (API name, behaviour, version)
   - Logical consistency (internal contradictions, cross-section conflicts)
   - Completeness (missing edge case, error handling, prerequisite)
   - Efficiency (algorithm, CI / build / runtime cost)
5. **Return format**: BLOCKER / MAJOR / MINOR three-level classification; each item with location (file + section) + suggestion

## Accept / Reject reply style

For each review finding the Leader gives:

- **ACCEPT + reason**: accepted; specify who fixes it this round
- **REJECT + reason**: rejected with a technical reason (not just "no")
- **DEFER**: acknowledged but deferred (goes to backlog / open items)

REJECT must cite specific evidence (API doc, prior decision, design constraint); pure preference is not acceptable.

## Anti-patterns

- **Using CLI to probe Apple API behaviour**: forbidden. Use official docs / WebSearch instead.
- **Repeatedly rejecting the same point in the same section**: more than 2 identical rejections counts as a communication failure; pause and clarify with the user.
- **ACCEPT without a reason**: every ACCEPT should still have a one-line note of why it adds value.
- **Leader drafting sections themselves**: violates the role separation; only allowed for cosmetic-grade fixes.

## Verification checklist

- Each round has an explicit dispatch prompt (all 5 elements present).
- Each review finding has an explicit accept / reject label + reason.
- When limit(N) is reached without convergence, pause; don't keep iterating indefinitely.
- Cosmetic fixes are inline-edited by the Leader; don't burn a round on them.
- The round-summary is recorded in the meeting log (not a verbatim copy of review content).

## Phase TODO sweep checklist

A separate close-the-loop activity that fires **once per phase** (not once per review round): before the Leader signs off on a phase-completion PR, run a sweep against the phase's diff scope to catch deferred-and-forgotten debt.

**Command** (Leader-run; against the phase's diff scope, not the full repo):

```
rg -n --no-heading -e 'TODO|FIXME|XXX|HACK|stub|placeholder|Phase [0-9]+ Part' <source-root>/
```

Replace `<source-root>/` with the actual source directory for this project (e.g. `Packages/<target>/Sources/`, `Sources/`, `src/`). The path must match the repo's layout — if it doesn't, the sweep silently finds nothing and the phase incorrectly appears clean.

**Disposition rule** — every match must fall into exactly one bucket; otherwise the phase is not complete:

1. **Resolved this phase** — fixed or implemented before merge.
2. **Moved to §Backlog** — routed to the topic-appropriate document's §Backlog section (product → `design.md`, engineering → `foundations.md`, implementation step → `plan.md`, collaboration → `methodology.md`), and the §Backlog entry **cites the source `file:line`** so the debt is traceable.
3. **Intentionally left** — documented in the phase meeting log as "intentionally left, see <follow-up issue / phase reference>".

**Stub / placeholder code without a literal TODO comment still counts.** Identifier names like `xxxPlaceholder`, `xxxStub`, or scaffolding values that are not real implementations must be flagged in the phase log even if the regex didn't catch them via comment text.

**Ownership**: the Leader runs the sweep. Subagents may flag debt during implementation (in their impl-notes `§未決`), but closing the loop before phase merge is non-delegable. A PR reviewer subagent dispatched for the phase-completion PR should also run the sweep against the diff and report findings as MAJOR (unless already documented per the disposition rule above).

**When to invoke**:
- Before declaring a phase complete.
- When dispatching a Code Reviewer subagent on a phase-completion PR — include this command in the review brief's checklist.
- When auditing whether a previously-declared "complete" phase actually was.

**Anti-pattern**: marking a regex match as "obviously fine, ignore" without writing the disposition down. The point of the sweep is the paper trail; an undocumented justification is indistinguishable from forgetting.

## Related skills

- `leader-developer-handoff-contract`: details the 5 elements of each sub-agent dispatch.
- `spec-phase-orchestration`: review cycles are usually embedded in the spec phase.
- `methodology-pattern-extractor`: "round-1 cosmetic inline edit" is a codifiable pattern.
