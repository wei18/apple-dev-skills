# github-contribution-workflow — first-party skill (design spec)

Date: 2026-06-25
Status: Implemented — historical archive, superseded by the shipped repo (SSOT:
[`README.md`](../../../README.md))

## Context

The catalog has process discipline *around* git/PR (`pr-diff-verification`,
`subagent-conflict-detection`) and the security slice of repo config
(`apple-public-repo-security`), but **no skill for the GitHub contribution loop
itself** — opening PRs and issues, creating/editing files via GitHub, setting
repo secrets, configuring contribution-flow repo settings, and merging. An
externals survey (2026-06-25) found the only well-licensed, maintained options
(`anthropics/claude-plugins-official` `github` via MCP; `ccplugins/awesome-claude-code-plugins`
via `gh` CLI, Apache-2.0, ~8 mo stale) but the user chose to write a focused
first-party skill that encodes *this owner's* conventions and composes with the
existing siblings rather than duplicating them.

This skill is **tool-agnostic agent process**, so it lives in
`collaboration-skills/` (not `apple-dev-skills/`). It is the catalog's 12th
collaboration skill.

## Goals

- A single skill (`github-contribution-workflow`) covering the `gh`-CLI
  contribution loop: PRs, issues, GitHub file ops, repo secrets, contribution-flow
  repo settings, and merge hygiene.
- Encode the owner's observed conventions (branch naming, Conventional-Commits PR
  titles, `Co-Authored-By` trailer, 🤖 PR footer, squash+delete merge,
  CLEAN-before-merge, `gh secret set` without `--body`, submodule-pin bump via
  `git update-index --cacheinfo`, `--no-verify` only for no-code/no-secret commits,
  worktree+PR for shared repos).
- Route, not duplicate: a scope-boundary that hands off to the four siblings.

## Non-goals / scope boundaries (route to sibling, do NOT re-cover)

- push/PR diff-vs-commit-claim integrity → `pr-diff-verification`
- security repo settings (Secret Scanning, push protection, gitleaks, `.gitignore`
  baseline) → `apple-public-repo-security`
- parallel-session / submodule worktree conflicts → `subagent-conflict-detection`
- distributing/installing skill plugins (marketplace, depth-1) → `claude-skill-plugin-packaging`
- pure local git operations with no GitHub surface → out of scope entirely

## Granularity decision

**One skill**, not split into PR / issue / repo-settings. Rationale: the three
share one toolchain (`gh` + git) and one set of conventions; splitting would force
heavy cross-references and violate the catalog's "one surface area, don't
over-split" rule. (User-confirmed.)

## Skill design

**`name`**: `github-contribution-workflow` (kebab == dir; gate-enforced).

**`description`** (precision router): verb-anchored to the GitHub contribution
loop; embeds the triggering commands so an agent routes here on intent —
`gh pr create` / `gh pr merge` / `gh pr checks` / `gh issue create` / `gh secret set` /
`gh api` / `git submodule` bump; chains trigger scenarios (open a PR, open an
issue, create/edit a file on GitHub, set a repo secret, configure repo settings,
check CI before merge); negative boundary (pure local git → not here; diff
verification → `pr-diff-verification`).

**Body structure** (scannable; decisions in tables):

1. **When to invoke / Scope** — trigger list + the scope-boundary block routing to
   the four siblings above.
2. **Decision table: intent → `gh` command** — rows for open PR / open issue /
   create-or-edit file via GitHub / set secret / configure repo settings / merge.
3. **Conventions** (the core value; sourced from the owner's repos + this session):
   - Branch naming: Conventional prefixes (`feat/ fix/ chore/ docs/ ci/`).
   - PR title: Conventional Commits (Sudoku enforces this via a CI gate).
   - Commit ends with `Co-Authored-By:` trailer; PR body ends with the 🤖 footer.
   - Merge with `--squash --delete-branch`; **`gh pr checks` must be CLEAN before
     merge** — never merge on a non-CLEAN / BLOCKED status; BLOCKED is usually
     just pending required checks → poll, don't force.
   - Secrets: `gh secret set <NAME>` **without `--body`** (interactive paste keeps
     the value out of shell history); verify with `gh secret list` (values are
     write-only).
   - Submodule pin bump: `git update-index --cacheinfo 160000,<sha>,<path>`
     (surgical gitlink set; no submodule checkout needed in a worktree).
   - `--no-verify`: allowed **only** for commits with no code and no secrets (e.g.
     a submodule-pin bump or config-only change) when a repo's pre-commit gate is
     heavy/slow; never for code/content commits. State the judgment rule.
   - Shared repo / submodule: edit via an isolated worktree + PR, never in place
     (cross-ref `subagent-conflict-detection`).
4. **Repo settings (contribution-flow only)** — merge-button config (squash-only,
   auto-delete head branch), branch protection requiring CI, required status
   checks, labels. Security settings (secret scanning, push protection) are
   explicitly deferred to `apple-public-repo-security`.
5. **Common Mistakes** + **Review Checklist** (the catalog's bookend convention).
6. **Related skills** — the four siblings by name.

## Consistency-gate impact

- `README.md` Catalog: add a `github-contribution-workflow` row under
  collaboration-skills; bump the group header `(11)` → `(12)`.
- `collaboration-skills/.claude-plugin/plugin.json`: description "11 first-party" →
  "12 first-party"; version bump `1.2.0` → `1.3.0`.
- `.claude-plugin/marketplace.json`: collaboration-skills `description` "11" → "12";
  version `1.2.0` → `1.3.0`; marketplace `metadata.version` bump.
- Regenerate `README.zh-Hant.md` (`mise run readme-zh`).
- `mise run check` green.

## Success criteria

- `mise run check` passes; the new skill's `name` matches its dir.
- `description` is router-form with the `gh` commands embedded and a negative
  boundary.
- A scope-boundary line routes each non-owned concern to the correct sibling; no
  content duplicates a sibling.
- README Catalog + counts + plugin.json + zh-Hant all consistent.

## Issue / PR tracking (user-requested workflow)

- This spec is recorded in a GitHub issue on `wei18/apple-dev-skills`.
- The implementation plan (writing-plans output) is appended to that issue.
- The implementation PR links and closes the issue.
