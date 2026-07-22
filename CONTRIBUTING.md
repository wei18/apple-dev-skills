# Contributing

This repo is a [Claude Code](https://code.claude.com) marketplace hosting two first-party
plugins (`apple-dev-skills`, `collaboration-skills`) plus aggregated externals. `README.md`
is the single source of truth.

## Setup

```bash
mise install && lefthook install
```

## Tasks (always via mise — never call the scripts directly)

- `mise run check` — SSOT consistency gate (run before every PR; CI runs the same).
- `mise run readme-zh` — regenerate `README.zh-Hant.md` from `README.md` (needs `claude`
  on PATH; auto-fires in pre-commit when `README.md` changes).

### zh-Hant mirror: hand-mirror small diffs, regenerate large ones

Full regeneration is non-deterministic — even for a 2-line content fix it rewrites
~40 lines of synonym churn, burying the real change in review. So:

- **≤ 5 changed content lines in `README.md`**: hand-mirror the same lines into
  `README.zh-Hant.md`, re-stamp its freshness marker, and commit with the regen
  hook excluded (it would otherwise clobber the hand-mirror with a full regen):

  ```bash
  sed -i '' "s/src-sha: [0-9a-f]*/src-sha: $(git hash-object README.md)/" README.zh-Hant.md
  git add README.md README.zh-Hant.md
  LEFTHOOK_EXCLUDE=readme-zh git commit -m "..."   # `check` still runs and verifies freshness
  ```
- **Larger / structural changes**: run `mise run readme-zh` for a full regeneration.

## Ways to contribute

### 1. Aggregate an external plugin (preferred when a good one exists)

**Aggregate, don't appropriate.** List good external plugins **by reference** in
`marketplace.json` (they install from the author's repo, credited) — never copy or
re-implement. Open an [aggregation issue](.github/ISSUE_TEMPLATE/aggregate-a-plugin.yml).
Requirements: MIT-compatible license; a real `.claude-plugin/plugin.json` (root → `source: github`,
subdir → `git-subdir`); no overlap with an existing skill.

### 2. Add a first-party skill (only for genuine gaps)

Pick the plugin: Apple/Swift → `apple-dev-skills/skills/`, generic agent process →
`collaboration-skills/skills/`. One dir per skill with a `SKILL.md` whose frontmatter
`name:` equals the dir. Then update `README.md`'s Catalog table + the group `(N)` count and
the plugin's `plugin.json` description count, and run `mise run check`.

### 3. Report a field note (skill vs reality)

Hit a real-world incident where a skill's guidance was wrong, incomplete, or missing —
or a situation no skill covered? Open a [field note](.github/ISSUE_TEMPLATE/field-note.yml).
Incidents are how this catalog's Sightings and known-trap entries grow.
