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
- `mise run readme-zh` — regenerate `README.zh-Hant.md` (Catalog heading `## 目錄`) from
  `README.md` (needs `claude` on PATH; auto-fires in pre-commit when `README.md` changes).
- `mise run readme-zh-hans` — same, for `README.zh-Hans.md` (Catalog heading `## 目录`).
  Every mirror listed in `scripts/mirrors.py` has its own task and its own pre-commit
  trigger; add both when a mirror is added.

### README mirrors: hand-mirror by default, regenerate only as fallback

Full regeneration is non-deterministic — even for a 2-line content fix it rewrites
~40 lines of synonym churn (and has previously flipped full-width punctuation to
half-width), burying the real change in review. So hand-mirroring is the default:

- **Default — any content change**: hand-mirror the same lines into each mirror in
  `scripts/mirrors.py` (currently `README.zh-Hant.md`, `## 目錄`; `README.zh-Hans.md`,
  `## 目录`), re-stamp each one's freshness marker, and commit with the regen hooks
  excluded (they would otherwise clobber the hand-mirror with a full regen):

  ```bash
  for f in README.zh-Hant.md README.zh-Hans.md; do
    sed -i '' "s/src-sha: [0-9a-f]*/src-sha: $(git hash-object README.md)/" "$f"
  done
  git add README.md README.zh-Hant.md README.zh-Hans.md
  LEFTHOOK_EXCLUDE=readme-zh,readme-zh-hans git commit -m "..."   # `check` still runs and verifies freshness
  ```
- **Fallback — large / structural changes**: run `mise run readme-zh` for a full
  regeneration, then manually re-check punctuation (full-width vs half-width) and
  wording before committing — regeneration is not a substitute for review.

## Ways to contribute

### 1. Aggregate an external plugin (preferred when a good one exists)

**Aggregate, don't appropriate.** List good external plugins **by reference** in
`marketplace.json` (they install from the author's repo, credited) — never copy or
re-implement. Open an [aggregation issue](.github/ISSUE_TEMPLATE/aggregate-a-plugin.yml).
Requirements: MIT-compatible license; a real `.claude-plugin/plugin.json` (root → `source: github`,
subdir → `git-subdir`); no overlap with an existing skill.

`git-subdir` only works when the upstream repo ships a `.claude-plugin/plugin.json`
*inside that subdirectory itself* — e.g. `swiftui-pro/.claude-plugin/plugin.json` in
`twostraws/SwiftUI-Agent-Skill` — so a subdir source can point at it. Aggregating just
one skill folder out of a repo whose only manifest sits at the repo root (e.g.
`caveman`, which has no `skills/<name>/.claude-plugin/plugin.json`) isn't possible
without upstream adding one; it's all-or-nothing via `source: github` there.

That MIT/no-overlap check happens once, at listing time — not on every upstream
commit — so an already-listed external's license, archive status, or skill count
can drift afterward. Run `mise run check-externals` to re-verify every listed
external still meets the aggregation requirements above; after a deliberate,
reviewed change (including right after adding a new one), accept the new baseline
with `mise run check-externals -- --update` and commit the updated snapshot.

### 2. Add a first-party skill (only for genuine gaps)

Pick the plugin: Apple/Swift → `apple-dev-skills/skills/`, generic agent process →
`collaboration-skills/skills/`. One dir per skill with a `SKILL.md` whose frontmatter
`name:` equals the dir. Then update `README.md`'s Catalog table + the group `(N)` count and
the plugin's `plugin.json` description count, and run `mise run check`.

Two gate rules `mise run check` enforces on the frontmatter `description`:
- Max 800 characters.
- If it contains `": "`, quote the whole value — an unquoted `": "` breaks strict YAML
  parsers (see #42).

### 3. Report a field note (skill vs reality)

Hit a real-world incident where a skill's guidance was wrong, incomplete, or missing —
or a situation no skill covered? Open a [field note](.github/ISSUE_TEMPLATE/field-note.yml).
Incidents are how this catalog's Sightings and known-trap entries grow — see
[`swiftui-interaction-footguns`'s Sightings section](apple-dev-skills/skills/swiftui-interaction-footguns/SKILL.md#sightings-real-bugs-that-shipped-past-review)
for what a grown-out one looks like.
