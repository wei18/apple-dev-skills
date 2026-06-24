---
name: agent-impl-notes-log
description: Maintain a running `meetings/{date}_{topic}.impl-notes.md` *during* subagent task execution to capture in-flight design decisions, intentional deviations from spec, considered alternatives, and open questions for Leader/User. Distinct from the post-hoc phase meeting log; this file is updated incrementally as decisions are made. Invoke at the start of any non-trivial subagent dispatch, when ambiguity is encountered mid-task, or when about to deviate from spec.
---

# Agent Implementation Notes — Running Log

## Purpose

The phase meeting log (`meetings/{date}_{topic}.md`) is summative — written after work completes. By that point, dozens of micro-decisions made mid-flight are already lost to the commit diff. An impl-notes log fills that gap: a **concurrent record** of decisions, deviations, tradeoffs, and unresolved questions, written as they happen.

The user explicitly asked for this:

> 在你進行工作的同時，維護一個名為 implementation-notes.md 的持續更新檔案，記錄任何我應該知道的，關於實作如何偏離或詮釋規格的事項。

## When to invoke

Subagent MUST invoke this skill at the start of any dispatch matching ANY of:

- Touches more than 3 files in production code.
- Implements behavior whose spec has known ambiguity (e.g., `// UNCONFIRMED` markers, "Unconfirmed ?" prerequisites).
- Introduces a new dependency, target, or module.
- Refactors existing code beyond a one-line fix.
- Any task with a `PROPOSAL_DRAFT` step in the AI Collaboration Mode workflow.

Subagent MAY skip this skill for trivial one-line fixes, pure typo corrections, or documentation copy edits.

## File layout

Path: `meetings/{YYYY-MM-DD}_{topic}.impl-notes.md`

Paired naming with the phase meeting log. If the phase log is `meetings/2026-05-20_phase-11-foo.md`, the impl-notes is `meetings/2026-05-20_phase-11-foo.impl-notes.md`.

If multiple subagents work on the same topic on the same day, append a numeric suffix: `meetings/2026-05-20_topic.impl-notes.2.md`.

## File format

```markdown
# Impl Notes — {topic} ({date})

Status: IN_PROGRESS
Owner: {subagent type, e.g. "Senior Developer"}
Dispatched by: Leader
Started: {ISO timestamp}

## 設計決定 (Design decisions)

_What you chose when the spec was ambiguous. Include the spec reference._

- **{decision name}** — Spec `docs/design.md §X.Y` says "...". Ambiguous on Z. Chose **A** because [reason]. Alternative was B (see §折衷).

## 偏離 (Deviations)

_Intentional deviations from the documented spec. Include the spec reference and the why._

- **{deviation name}** — Spec says X. Implemented as Y because [reason]. Downstream impact: [what changes for callers / tests / docs].

## 折衷 (Tradeoffs)

_Alternatives considered and the reasoning for the current pick._

- **{tradeoff topic}** — Considered: [A, B, C]. Picked **B** because [reason]. Rejected A because [reason]; rejected C because [reason].

## 未決 (Open questions)

_Things you want Leader / User to confirm. Be specific. Block on these before final report if they're load-bearing._

- **{question}** — [specific question]. Default behavior I picked: [X]. Risk if I'm wrong: [impact].
```

## How to update

- **Update incrementally** — write the entry as you make the decision, NOT in a batch at the end. The whole point is to capture context that fades.
- **Keep entries terse but self-contained** — one bullet should be readable months later without re-reading the diff.
- **Cite spec sections** by section number (`§How.4.7`) so Leader can verify against the source.
- **Cross-link related entries** if a 折衷 decision later becomes a 偏離.
- **Don't duplicate the diff** — the file is for context, not code listings.

## Status transitions

- `IN_PROGRESS` — work ongoing; file may be edited any time.
- `COMPLETE` — work finished, ready for Leader review. Set this before reporting back.
- `BLOCKED` — work paused awaiting Leader/User answer to an §未決 item. Required when an open question is load-bearing.

## Subagent dispatch contract (Leader-side)

When Leader dispatches a subagent matching the invoke criteria, the dispatch prompt MUST include:

> Create `meetings/{date}_{topic}.impl-notes.md` at the start of your work using the `agent-impl-notes-log` skill format. Update it incrementally — design decisions, deviations, tradeoffs, open questions. Mark `Status: COMPLETE` before final report. Include the file path in your report.

Subagent's final report MUST link the impl-notes file. Leader reads it before merging the work to verify decisions match Leader's intent.

## Anti-patterns

- **Writing impl-notes at the end as a batch** — defeats the purpose; you've already forgotten the context.
- **Logging every minor edit** — file is for *decisions*, not edit history. Trivial mechanical fixes belong in the commit, not here.
- **Using this file instead of the phase meeting log** — the two coexist. Phase log is summative, impl-notes is concurrent. Phase log gets archived when sealed; impl-notes can be referenced from the phase log.
- **Sealing the file without resolving 未決 items** — open questions must be answered (by Leader/User) or moved to a backlog before status flips to COMPLETE.

## Related skills

- `session-to-meeting-log`: produces the post-hoc phase meeting log; the two artifacts pair.
- `leader-developer-handoff-contract`: defines the dispatch contract; impl-notes is one of its outputs.
- `subagent-review-cycles`: when a subagent's work returns for review, Leader reviews the impl-notes alongside the diff.
