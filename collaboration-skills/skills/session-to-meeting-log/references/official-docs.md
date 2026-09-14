Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Extend Claude with skills | https://code.claude.com/docs/en/skills#run-skills-in-a-subagent | `context: fork` + `agent`: no conversation history, so instructions must stand alone |
| Extend Claude with skills | https://code.claude.com/docs/en/skills#available-string-substitutions | Arguments section: `$0` / `$1` (an unfilled index stays literal); `${CLAUDE_SESSION_ID}` |
| Environment variables | https://code.claude.com/docs/en/env-vars | `CLAUDE_CODE_SESSION_ID` is set in Bash tool subprocesses (caveat: may be the startup ID after `--continue` / `--resume` without an ID; observed to equal the parent id inside a subagent) |
| Create custom subagents | https://code.claude.com/docs/en/sub-agents | Subagent transcripts live at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl` |
