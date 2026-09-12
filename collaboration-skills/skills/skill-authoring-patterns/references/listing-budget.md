# The listing budget is catalog-wide, not per-skill

Claude Code loads a listing of every skill's name + `description` into context on every session so the model knows what's available; the listing's character budget scales at **1% of the model's context window** (raise it with the `skillListingBudgetFraction` setting or the `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var). Each entry's own `description` (+ `when_to_use`, if present — see below) is separately capped at **1,536 characters** regardless of that budget (`skillListingMaxDescChars`). When the total listing overflows the budget, Claude Code truncates descriptions **starting with the skills you invoke least** — your most-used skills keep their full text, your least-used ones lose theirs first. Run `/skill-doctor` (≥ v2.1.252) or `/doctor` to see the actual per-session listing cost measured, rather than estimating it. ([Claude Code docs, Skills](https://code.claude.com/docs/en/skills))

The practical implication for this catalog: the scarce resource is not "can my one `description` fit" — this catalog already runs `DESC_MAX = 800` in `scripts/check-consistency.py`, deliberately tighter than the official 1,536-char cap (and also under the 1,024-char hard limit the platform Agent Skills spec enforces for claude.ai / Skills API uploads), precisely because 38 skills' descriptions compete for one shared budget every session. Every new skill's `description` is a permanent tax on that shared budget, paid on every session regardless of whether the skill ever fires. So before adding a skill, ask **"is this trigger phrase worth permanently occupying part of every session's listing budget?"** — not just "does this description fit under 800 chars".

## Where this catalog stands against that budget

Measured total (an estimate — re-scan before quoting it; `mise run check` also prints each skill's `desc len`):

```
$ python3 - <<'EOF'
import re, glob
tot = 0; n = 0
for f in sorted(glob.glob('*/skills/*/SKILL.md')):
    fm = re.search(r'^---\n(.*?)\n---', open(f).read(), re.S).group(1)
    d = re.search(r'^description:\s*(.*?)(?=^\w[\w-]*:|\Z)', fm, re.S | re.M).group(1).strip()
    if d[0] == d[-1] and d[0] in "'\"": d = d[1:-1]
    tot += len(d); n += 1
print(f"skills={n} total_desc_chars={tot} avg={tot // n}")
EOF
skills=38 total_desc_chars=21953 avg=577
```

So the 38 first-party descriptions alone total ≈ 22k characters (2026-09-12 scan). On a 200k-token model the default 1% budget is ≈ 2,000 tokens ≈ 8,000 characters (4-chars-per-token rule of thumb) — this catalog by itself is close to 3× that before any other plugin's skills are counted, so on such a model the least-used skills here run with a bare name and never auto-route. On a 1M-context model the same 1% (≈ 40k chars) holds the whole catalog. The two truncations differ: budget overflow drops **whole** descriptions, least-used first; the per-entry 1,536-char cap cuts one entry from the end (hence "put the key use case first").

What each side can do about it:

- **Consumer**: raise `skillListingBudgetFraction` (`0.02` = 2%; `0.03` ≈ 24k chars on a 200k model, enough for this catalog) or set `SLASH_COMMAND_TOOL_CHAR_BUDGET` to a fixed character count; disable plugins you don't need via `/plugin`. `skillOverrides: "name-only"` does **not** help for this catalog — "Plugin skills are not affected by `skillOverrides`. Manage those through `/plugin` instead." ([Claude Code docs, Skills](https://code.claude.com/docs/en/skills))
- **Author (this repo)**: put the key use case in the first sentence, and treat every new skill as a permanent charge against the shared budget — see above.

`when_to_use` is a real frontmatter field (appended to `description` in the listing and counted toward the same 1,536-char cap) meant for trigger phrases / example requests. None of this catalog's 38 skills declares `when_to_use` in frontmatter (`grep -l '^when_to_use:' **/SKILL.md` → 0 hits; a plain `grep -rl when_to_use` also matches this paragraph's own mention of the field name, so target the frontmatter line specifically) — this catalog folds trigger phrasing directly into `description` instead (see the router form in `SKILL.md`). That's a deliberate, not accidental, choice: keeping trigger wording in one field is simpler to audit against `DESC_MAX` than splitting it across two fields that share a cap.
