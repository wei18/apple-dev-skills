Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Extend Claude with skills | https://code.claude.com/docs/en/skills | Description section: `description` = what + when; `paths:` glob; `when_to_use` |
| Extend Claude with skills | https://code.claude.com/docs/en/skills#how-a-skill-gets-its-command-name | Naming section: a plugin skill's `name` sets the command's last segment; a personal/project skill's `name` is only a display label |
| All settings | https://code.claude.com/docs/en/settings-reference#skilllistingbudgetfraction | references/listing-budget.md: budget key; "drops the descriptions of the least-used skills" |
| Agent Skills | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | listing-budget.md 1,024-char limit; Level 3 resources "None until accessed" (why two-tier `references/`) |
| Skill authoring best practices | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | Two-tier depth: "Keep references one level deep from SKILL.md"; SKILL.md body under 500 lines |
| Specification | https://agentskills.io/specification | `name` "Must match the parent directory name" (backs the name==dir gate); reference files are loaded on demand |
