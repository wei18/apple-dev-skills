---
name: methodology-pattern-extractor
description: Read accumulated meeting logs and session JSONL files, extract collaboration patterns that have repeated ≥ 3 times, and append them to `docs/methodology.md` §Patterns. Each entry captures trigger / action / outcome / next-time adjustment. Invoke when the user asks "update methodology", "extract patterns from this session", "consolidate recurring collaboration patterns", or after every 5+ meeting logs accumulate.
---

# Methodology Pattern Extractor

## When to invoke

- The user says "update methodology", "extract a pattern", "I feel this flow has happened several times now".
- ≥ 5 meeting logs have accumulated but methodology.md §Patterns is still empty.
- After hitting an important milestone (end of spec phase, v1 release, major refactor close-out).

## Inputs

- All `meetings/*.md`
- Corresponding session JSONL (optional, for filling in details)
- The existing `docs/methodology.md` (to avoid duplicate entries)

## Rule: ≥ 3 sightings or it's not a pattern

**Don't** turn a one-off behaviour into a pattern. Criteria:
- The same triggering situation appears in **≥ 3 different meeting logs**
- The response action each time is consistent or convergent
- There is an observable outcome

Items with fewer than 3 sightings can go into methodology.md §Backlog as "candidate patterns", annotated with the sighting count.

## Output format

One entry per pattern, four lines:

```markdown
### <Pattern name>

- **Trigger**: <what context activates this pattern>
- **Action**: <the observed response action>
- **Outcome**: <the resulting outcome>
- **Next-time adjust**: <what you'd improve next time, may be empty>
- **Sightings**: <meeting log dates ×N, comma-separated>
```

Example:

```markdown
### Section-by-section approval

- **Trigger**: User asks Leader to draft a document section (design.md / foundations.md / plan.md)
- **Action**: Leader advances one section at a time, waits for OK before moving on
- **Outcome**: Avoids the high cost of "whole-doc rejection and rewrite"
- **Next-time adjust**: Before dispatching a sub-agent, confirm all prerequisites for the section are Resolved
- **Sightings**: 2026-05-15 ×3
```

## Procedure

1. Grep meeting logs for frequently appearing verbs / triggers ("dispatch", "review round", "prerequisite", "rejected", ...).
2. For each high-frequency trigger, revisit its context — does the same action recur?
3. Filter to candidates with ≥ 3 sightings.
4. Extract Trigger / Action / Outcome / Next-time / Sightings.
5. **Append** to `methodology.md §Patterns`; never overwrite existing entries.
6. If a candidate has only 1–2 sightings, add it to methodology.md §Backlog as a "candidate pattern".

## Anti-patterns (also worth recording)

The same section may include §Anti-patterns: practices tried but found unsuitable. Bar for entry is lower: **a single significant misstep with a clear lesson** is enough.

## Verification checklist

- Every pattern carries Sightings ≥ 3.
- No duplicates with existing entries (grep `methodology.md` first).
- Original meeting logs are never modified.
- Pattern names use kebab-case or short phrases, no more than 6 words.

## Deviation considerations

- **Solo project, single author**: "recurrence" includes the author's own habits; the ≥ 3 rule still applies.
- **Cross-project**: this skill's default scope is one repo; if extracting across repos, explicitly cite each origin.

## Related skills

- `session-to-meeting-log`: produces this skill's input.
- `backlog-routing-by-topic`: candidate patterns go into methodology.md §Backlog.
- `subagent-review-cycles` / `spec-phase-orchestration` / `leader-developer-handoff-contract`: codified forms of common patterns.
