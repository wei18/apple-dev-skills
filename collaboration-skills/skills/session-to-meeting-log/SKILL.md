---
name: session-to-meeting-log
description: Read a Claude Code session JSONL log and produce a clean timeline-style meeting log at `meetings/{YYYY-MM-DD}_{topic}.md`. Invoke when the user asks "turn this session into a meeting log", "archive today's discussion", "extract a meeting record from jsonl", or when wrapping up a working session before context window rolls.
---

# Session → Meeting Log

## When to invoke

- The user says "turn this session into a meeting log" or "archive today's discussion".
- The session is approaching the context limit and needs a written artifact.
- The user mentions "extract notes from `~/.claude/projects/.../*.jsonl`".
- A long, multi-turn discussion is wrapping up before switching sessions.

## Inputs

### Locating the session file

- Default location: `~/.claude/projects/<encoded-project-path>/<sessionId>.jsonl`
- `<encoded-project-path>`: replace `/` in the absolute path with `-`, e.g. `/Users/alice/GitHub/MyOrg/my-project` → `-Users-alice-GitHub-MyOrg-my-project`.
- `<sessionId>`: a UUID-like string, either supplied by the user or inferred from the most recent mtime in the directory.
- If the user doesn't supply one, list the files in the directory, sort by mtime, and confirm the latest one.

### JSONL structure

One JSON event per line; common `type` fields:

| type | Content |
|---|---|
| `user` | User prompt (incl. system reminders) |
| `assistant` | Assistant response (incl. tool_use blocks) |
| `tool_result` | Tool execution result |
| `summary` | Session summary (if any) |

Key fields: `timestamp`, `message.content`, `message.role`, `uuid`, `parentUuid`.

## Output

Write to `meetings/{YYYY-MM-DD}_{topic}.md`:

```markdown
# {YYYY-MM-DD} — {Topic}

Session id: `<sessionId>`
Mode: <e.g. AI Collaboration Mode (Leader/Developer)>

## Goal
<one-line statement of the session's goal>

## Decisions
1. <decision 1>
2. <decision 2>

## Rejected alternatives
- <rejected option> — reason: <reason>

## Hand-offs
- <sub-agent dispatched / next session expected to ...>

## Open questions
- <open question 1>

## Next session
<one-line statement of the next session's intent>
```

### Extraction rules

1. **No verbatim copying.** Summarise decisions and their reasons; drop exploratory chatter, rhetoric, and repeated clarifications.
2. **Decisions**: only items the user explicitly confirmed or the Leader explicitly ACCEPTed.
3. **Rejected alternatives**: options that were discussed and turned down; include a one-line concrete reason.
4. **Hand-offs**: list sub-agents dispatched in this session, or explicitly state what the next session should pick up.
5. **Open questions**: items that didn't converge this session and need a decision next time.
6. **Don't record tool-call details** (e.g. "Read foo.md / Edit bar.md"); only **why** something was read / changed and the **result**.
7. **Timeline keeps only milestones**: e.g. "§How.3 round 1 accepted", "Code Reviewer dispatch produced 7 BLOCKERs".
8. **Never leak secrets**: if the JSONL contains tokens / PEM / API keys, **delete them, never copy** into the meeting log (even if the file itself is private).

## Verification checklist

- Filename format `YYYY-MM-DD_<topic-kebab>.md`, date in local timezone.
- Contains the five main sections: Goal / Decisions / Rejected alternatives / Hand-offs / Open questions / Next session.
- Entries are summaries, never verbatim copies.
- No secrets / tokens / PII.
- If the session spans multiple days, add a phase tag to the topic (e.g. `kickoff` / `spec-phase` / `cr-round1`).

## Deviation considerations

- **Session is too short (< 5 meaningful turns)**: a standalone log isn't necessarily warranted; append as an addendum to the previous log.
- **Session was highly divergent**: split into multiple topic-specific logs for the same day, named `{date}_{topic-a}.md` / `{date}_{topic-b}.md`.
- **Sub-agent internal exchanges**: usually not included in the meeting log; only record the main agent's dispatch + summary of the returned result.

## Related skills

- `methodology-pattern-extractor`: meeting logs produced here are the input for methodology pattern extraction.
- `backlog-routing-by-topic`: open questions that can be classified can also be routed to the matching file's §Backlog.
