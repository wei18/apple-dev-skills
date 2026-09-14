Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Create custom subagents | https://code.claude.com/docs/en/sub-agents | Native mechanism quote ("own context window with a custom system prompt, specific tool access, and independent permissions") |
| Create custom subagents | https://code.claude.com/docs/en/sub-agents#preload-skills-into-subagents | Element 3: the `skills:` field preloads full skill content at startup |
| Create custom subagents | https://code.claude.com/docs/en/sub-agents#available-tools | Element 5 caveat: a `disallowedTools` entry such as `Bash(git push *)` removes the whole Bash tool, so the layered CLI ban can't be expressed there |
| Configure permissions | https://code.claude.com/docs/en/permissions#bash | Element 5: to keep read-only `git log` / `git show` but block build/run probes, use Bash deny rules, which "apply to the main conversation and to subagents" |
