---
name: backlog-routing-by-topic
description: Route mid-discussion stray ideas to the matching file's §Backlog section by topic — product → design.md; tooling → foundations.md; implementation step → plan.md; collaboration → methodology.md; unclassifiable → today's meeting log §Open questions. Invoke when a stray idea pops up during focused work, when reviewing a meeting log for parking lot items, or when asked "where does this idea go".
---

# Backlog Routing by Topic

## When to invoke

- A "don't handle now but don't forget" idea comes up mid-discussion.
- Tidying a meeting log and re-homing parking-lot items.
- User asks "where does this idea go", "should backlog be split by file".

## Routing rules

| Topic | Destination |
|---|---|
| **Product / gameplay / UX / feature proposal** | `docs/design.md §Backlog` |
| **Tooling / packages / language features / CI / Secrets / L10n** | `docs/foundations.md §Backlog` |
| **Implementation step / refactor / test coverage expansion** | `docs/plan.md §Backlog` |
| **Collaboration mode / agent skill setup / review flow** | `docs/methodology.md §Backlog` |
| **Unclassifiable / highly divergent** | Today's `meetings/{date}_*.md` §Open questions |

## Entry format

One line each; if context is needed, attach the meeting log date as a sub-bullet:

```markdown
- Adopt `XcodeSelectiveTesting` to only run impacted test targets in CI (2026-05-15)
- Developers can reproduce GitHub Actions workflows locally via `nektos/act`
  - Note: act has limited macOS runner support; reconsider when designing §4 CI (2026-05-15)
```

- One line preferred; only add a sub-bullet when context is essential.
- Date goes in parentheses at the end so you can trace back to the originating meeting log.

## Procedure

1. Identify the idea's **topic category** (using the table above).
2. **Don't** expand the discussion on the spot — write one line, continue the current task.
3. If ambiguous (product + tooling mixed), pick the file at the **bigger decision point**; e.g. "new feature needs a particular tool" lands in design.md, with a cross-ref line in foundations.md.
4. If totally unclassifiable, log it under today's meeting log §Open questions and re-classify next discussion.

## Anti-patterns

- **Keeping it in chat without writing it down**: forgotten within 3 turns.
- **Writing a paragraph per backlog item**: suppresses recording cadence; counter-productive.
- **Recording the same item twice**: grep the relevant §Backlog before adding.
- **Mistaking a current decision for a backlog item**: things to do now belong in the body of `plan.md`, not the backlog.

## Verification checklist

- Every living doc has a §Backlog section (even if empty).
- Entries follow "one line + optional sub-bullet + date".
- No obvious misrouting (e.g. gameplay idea in foundations.md).
- The same idea doesn't appear in multiple files' §Backlogs.

## Related skills

- `spec-phase-orchestration`: §Backlog on every living doc is part of the structure.
- `methodology-pattern-extractor`: methodology.md §Backlog can include "candidate patterns" (sightings < 3).
- `session-to-meeting-log`: the open questions section is the routing fallback.
