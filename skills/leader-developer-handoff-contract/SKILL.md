---
name: leader-developer-handoff-contract
description: When the main agent dispatches a sub-agent, the prompt MUST include 5 elements — (1) task scope with verifiable target, (2) files / docs the sub-agent should read, (3) explicit skill list to invoke, (4) expected return format (diff / markdown section / decision text), (5) verification criteria. Invoke when about to dispatch a sub-agent (Developer / Designer / Code Reviewer), writing the dispatch prompt, or when asked "what should the sub-agent prompt include".
---

# Leader → Developer Handoff Contract

## When to invoke

- About to dispatch a sub-agent (Developer / Designer / Code Reviewer / drafting agent).
- Writing the dispatch prompt.
- User asks "what should the sub-agent dispatch include / which elements am I missing".

## The 5 required elements

Every dispatch prompt must contain:

### 1. Task scope with verifiable target

- One sentence stating the goal.
- Explicitly name **the output file / section / behaviour**.
- Include a mechanically checkable success / failure condition.

**Good**: "Draft §5 Logger for `docs/foundations.md`; output format: complete markdown section; scope: adopt `os.Logger` defaults, with subsystem / category conventions and privacy default"

**Bad**: "Write something about logger"

### 2. Files / docs the sub-agent should read

- List file names + sections.
- Don't say "read design.md"; say "read `design.md §How.2`, `foundations.md §3-§4`".
- Add grep targets / line ranges when useful to save the sub-agent's exploration tokens.

### 3. Explicit skill list to invoke

- List the skill names the sub-agent should invoke (with plugin prefix).
- Don't assume the sub-agent will guess.
- Example: "invoke `swift6-concurrency`, `swiftpm-modularization`, `swift-testing-baseline`; review-style dispatches also list `subagent-review-cycles`".

### 4. Expected return format

Pick one explicitly (or custom):
- **Code diff** (patch / full-file rewrite)
- **Markdown section** (drop into a specified file's §)
- **Decision text** (structured ACCEPT/REJECT/DEFER list)
- **Finding list** (BLOCKER / MAJOR / MINOR)

**Bad**: "Report results"
**Good**: "Return the complete §5 content as markdown, ready for the Leader to paste into `foundations.md`; no chit-chat"

### 5. Verification criteria

- The conditions under which it counts as done.
- For Developer: which tests must be green, which invariants must hold.
- For Code Reviewer: review dimensions, forbidden tools (CLI), allowed tools (WebSearch).
- For drafting agent: section structure, required subsections, required decisions.

## Template

```
You are a <role> dispatched by the Leader.

## Task scope
<verifiable target, output file/section, success condition>

## Inputs (read these in order)
1. <path> §<section>
2. <path>
<...>

## Skills to invoke
- <skill-name-1>
- <skill-name-2>
<...>

## Return format
<one of: code diff / markdown section / decision text / finding list>
<exact shape>

## Verification criteria
- <criterion 1>
- <criterion 2>
<...>

## Constraints (optional)
- DO NOT <forbidden action>
- DO use <required tool / approach>
```

## Examples drawn from real dispatches

### Developer drafting design.md §How.3 (Game Center)

- **Scope**: draft `design.md §How.3` GC integration section, covering leaderboard / achievement / protocol / auth fallback / friends scope
- **Inputs**: `design.md §What.GC`, `foundations.md §1-§4`
- **Skills**: `swift6-concurrency`, `swiftpm-modularization`, `swift-testing-baseline`
- **Return**: complete markdown section, ready to merge into design.md
- **Verification**: includes 3 leaderboards + 10 achievements, protocol covers friends scope, auth failure has a fallback path

### Code Reviewer round 1 over §How 1–7

- **Scope**: review `design.md §How.1 – §How.7` for technical correctness
- **Inputs**: full design.md, foundations.md
- **Skills**: `subagent-review-cycles`
- **Return**: BLOCKER / MAJOR / MINOR finding list; each item with section location + suggestion
- **Verification**: covers 4 dimensions (correctness / consistency / completeness / efficiency); cites Apple docs instead of CLI experimentation
- **Constraints**: DO NOT run CLI; DO use WebSearch

## Anti-patterns

- **Omitting verification criteria**: the sub-agent self-judges "done", often misaligned with the Leader's expectation.
- **Listing "related skills" instead of "skills to invoke"**: the sub-agent may not actually trigger them.
- **Return format written as "free-form"**: every round looks different and integration cost balloons.
- **Scope too large (multiple sections / files in one round)**: review and revision cost explodes; split fine.

## Verification checklist (for Leader before sending dispatch)

- All 5 elements present (scope / inputs / skills / return format / verification).
- Scope corresponds to "one verifiable target", not "a basket of work".
- Skill names spelled correctly, with plugin prefix.
- Return format is one of the four explicit categories.
- Verification conditions are mechanically checkable.

## Related skills

- `subagent-review-cycles`: handoff is the starting point of each review-cycle round.
- `spec-phase-orchestration`: every sub-agent dispatch in the spec phase follows this contract.
- `session-to-meeting-log`: dispatch + returned-result summary lands in the meeting log.
