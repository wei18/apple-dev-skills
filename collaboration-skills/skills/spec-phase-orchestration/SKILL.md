---
name: spec-phase-orchestration
description: The pre-implementation document pipeline — 5 files + `meetings/` directory (README.md + docs/design.md + docs/foundations.md + docs/plan.md + docs/methodology.md + meetings/), section-by-section approval (§What before §How), prerequisite checklist with Unconfirmed / Resolved gates, "no implementation code before design.md and plan.md approved" rule. Invoke when starting a new project that needs spec-first development, deciding doc structure, or when asked "which documents go in the spec phase".
---

# Spec Phase Orchestration

## When to invoke

- Starting a new project and deciding which documents the spec phase produces.
- Multiple documents / sections are in flight and you need to decide the order of progress.
- User asks "design or foundations first", "can we proceed with prerequisites unresolved".

## Default decisions

### 5 files + `meetings/` directory

```
<project>-spec/
├── README.md                  # Project entry point
├── docs/
│   ├── foundations.md         # Engineering substrate (language version, modules, CI, L10n, secrets)
│   ├── design.md              # Product spec §What + technical design §How (unified)
│   ├── plan.md                # TDD-ordered checklist
│   └── methodology.md         # Claude agent application practices (living doc)
└── meetings/
    └── {YYYY-MM-DD}_{topic}.md
```

Don't split further:
- No separate spec.md / rfc.md / tasks.md (folded into design.md / plan.md)
- No `adr/` directory; major decisions land directly in design.md or foundations.md (open one only if real need arises)

### Progression order

```
foundations.md §1..§N (one section at a time) →
design.md §What (product spec) →
design.md §How (technical design) →
plan.md (TDD-ordered) →
implementation phase begins
```

**Rule**: don't write §How before design.md §What passes; don't write implementation code before plan.md passes.

### Section-by-section approval

- The Leader advances one section at a time, waiting for user / review approval before moving on.
- Multiple sub-agent rounds may happen within a single section (see `subagent-review-cycles`).
- Section order is non-skippable: §What before §How, §1 before §2.

### Prerequisite checklist (Unconfirmed / Resolved gates)

Any proposal depending on external tools / APIs / third-party packages **must** include a prerequisite checklist:

```markdown
**Prerequisites**:
- [ ] Behaviour of Apple `XYZAPI.foo()` is consistent across iOS 26 and 25 — **Unconfirmed** (verified in plan.md step N)
- [x] ~~Xcode Cloud hook naming~~ — **Resolved** (Code Review round N, date): adopt `ci_post_clone.sh`
```

- Unconfirmed items **block Leader approval** — the section stays DRAFT until each item is Resolved.
- Resolved items are checked off with their decision basis + date.

### No implementation code before design + plan approved

- Before design.md §What + §How pass and plan.md is written and approved, **no implementation Swift code is written**.
- Exception: a pure exploratory spike — must be logged under `meetings/` as a spike; its output doesn't land on main.

### Backlog sections

Every living doc carries a §Backlog. Stray ideas are routed by topic: "product → design", "tooling → foundations", "implementation step → plan", "collaboration → methodology", "unclassifiable → meeting log" (see `backlog-routing-by-topic`).

## Rationale

- 5 docs + meetings dir is the "enough to record, not redundant" sweet spot for solo / small teams; 8 files is over-structured, 4 lacks room for foundations / methodology.
- Section-by-section avoids the high cost of "send the whole doc back".
- Prerequisite gates force "assumptions" to become "items to verify"; CLI trial-and-error is not the default answer.
- Spec-first: "no spec, no code" is a fundamental premise of AI agent collaboration (otherwise prompts are vague and output diverges).

## Deviation considerations

- **Tiny utility / 1-day project**: keep only README.md + meeting log; inline the design in the README.
- **Adding a feature to an existing codebase**: skip foundations.md; lean on the existing conventions.
- **Multi-person collaboration**: plan.md may split into `plan/<feature>.md`, but keep a master plan listing the dependencies.
- **Full outsourcing / contractor**: use an RFC + tasks split instead; this skill is a solo / small-team default.

## Verification checklist

- 5 docs + meetings dir structure in place (README + 4 docs + meetings dir).
- design.md contains §What and §How; §How is only filled after §What passes.
- foundations.md sections carry Status (DRAFT / FINAL / OBSOLETE) + Open items (if any).
- plan.md steps are TDD-ordered (test step precedes implementation step).
- Every prerequisite item is explicitly marked Unconfirmed / Resolved.

## Related skills

- `backlog-routing-by-topic`: rules for placing stray ideas.
- `subagent-review-cycles`: round structure inside spec sections.
- `leader-developer-handoff-contract`: dispatch contract when handing sections to a sub-agent.
- `session-to-meeting-log`: persisting each spec session.
