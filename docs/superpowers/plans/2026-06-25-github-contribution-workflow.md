# github-contribution-workflow Skill — Implementation Plan

> Status: Implemented — historical archive, superseded by the shipped repo.
> Version targets below are as-written (1.2.0 → 1.3.0); current versions live
> in the SSOT [`README.md`](../../../README.md) and the manifests.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first-party `github-contribution-workflow` skill (12th collaboration skill) and wire it through the SSOT/consistency gate.

**Architecture:** Author one `SKILL.md` under `collaboration-skills/skills/`, then update the four SSOT surfaces (README Catalog, the plugin's `plugin.json`, the root `marketplace.json`, the regenerated zh-Hant mirror). The consistency gate (`mise run check`) is the test harness — it must end green; the `skill-authoring-patterns` Review Checklist is the qualitative gate.

**Tech Stack:** Markdown SKILL.md; JSON manifests; `mise run check` (Python gate); `mise run readme-zh` (`claude`-backed zh-Hant generator).

## Global Constraints

- Skill lives in `collaboration-skills/` (tool-agnostic process), NOT `apple-dev-skills/`.
- `name` frontmatter MUST equal the directory `github-contribution-workflow` (gate-enforced).
- Single skill — no split (user-confirmed).
- Compose, don't duplicate: a scope-boundary routes to `pr-diff-verification`, `apple-public-repo-security`, `subagent-conflict-detection`, `claude-skill-plugin-packaging`.
- Count goes 11 → 12; collaboration-skills + marketplace version `1.2.0 → 1.3.0`.
- README.md is SSOT; zh-Hant is regenerated, never hand-edited; `mise run check` must pass.

---

### Task 1: Author the SKILL.md

**Files:**
- Create: `collaboration-skills/skills/github-contribution-workflow/SKILL.md`

**Interfaces:**
- Produces: a depth-1 skill `collaboration-skills/skills/github-contribution-workflow/SKILL.md` whose frontmatter `name: github-contribution-workflow`.

- [ ] **Step 1: Write the file** with exactly this content:

````markdown
---
name: github-contribution-workflow
description: Author GitHub contributions with the gh CLI — open/merge PRs, open issues, create or edit files on GitHub, set repo secrets, and configure contribution-flow repo settings. Use when running `gh pr create` / `gh pr merge` / `gh pr checks` / `gh issue create` / `gh secret set` / `gh api`, checking CI before merging, or bumping a submodule pin. Covers branch + Conventional-Commits PR-title conventions, the Co-Authored-By trailer + 🤖 footer, squash+delete merge, CLEAN-before-merge, `gh secret set` without --body, submodule bumps via `git update-index`, and the --no-verify rule. Does NOT cover pure local git, diff-vs-commit verification (→ pr-diff-verification), security repo settings (→ apple-public-repo-security), worktree conflict detection (→ subagent-conflict-detection), or plugin distribution (→ claude-skill-plugin-packaging).
---

# GitHub Contribution Workflow

The `gh`-CLI contribution loop for an agent acting on a GitHub repo: branch →
commit → PR → CI → merge, plus issues, GitHub-side file ops, repo secrets, and
contribution-flow repo settings. Encodes conventions that keep an agent's
contributions reviewable and consistent. Tool-agnostic in spirit; concrete
commands are `gh` + `git`.

## When to invoke

- Opening or merging a PR; opening or commenting on an issue.
- Creating or editing a file *through GitHub* (API / web flow) rather than a local clone.
- Setting a repo secret or configuring contribution-flow repo settings.
- Checking CI status before a merge; bumping a submodule pin.
- User says "open a PR / issue", "merge this", "set the secret", "configure the repo".

## Scope — what this does NOT own (route to sibling)

- **Verifying the diff matches the commit's claims** before push/PR → `pr-diff-verification`.
- **Security repo settings** (Secret Scanning, push protection, gitleaks, `.gitignore` baseline) → `apple-public-repo-security`.
- **Parallel-session / submodule worktree conflicts** → `subagent-conflict-detection`.
- **Distributing or installing skill plugins** (marketplace, depth-1 rule) → `claude-skill-plugin-packaging`.
- **Pure local git** with no GitHub surface → out of scope.

## Intent → command

| Intent | Command |
|---|---|
| Open a PR | `gh pr create --title "<conventional title>" --body "<body + 🤖 footer>"` |
| Check CI before merge | `gh pr checks <n> --repo <o/r>` ; `gh pr view <n> --json mergeStateStatus` |
| Merge a PR | `gh pr merge <n> --squash --delete-branch` (only when status is `CLEAN`) |
| Open an issue | `gh issue create --title "<title>" --body "<body>"` |
| Comment on an issue | `gh issue comment <n> --body "<text>"` |
| Create/edit a file via GitHub | `gh api -X PUT repos/<o/r>/contents/<path> -f message=… -f content=$(base64) …` (no local clone needed) |
| Set a repo secret | `gh secret set <NAME> --repo <o/r>` (interactive paste; see Conventions) |
| List secrets | `gh secret list --repo <o/r>` (names only; values are write-only) |
| Configure merge / branch protection | `gh api -X PATCH repos/<o/r> -F allow_squash_merge=true -F delete_branch_on_merge=true` ; `gh api -X PUT repos/<o/r>/branches/<b>/protection …` |

## Conventions

- **Branch names** use Conventional prefixes: `feat/ fix/ chore/ docs/ ci/ refactor/ test/`.
- **PR titles** follow Conventional Commits (some repos enforce this with a CI gate — e.g. a "Validate PR title" check; a non-conforming title fails the PR).
- **Commit trailer**: end commit messages with the agreed `Co-Authored-By:` trailer. **PR body**: end with the 🤖 footer.
- **Merge**: `--squash --delete-branch`. **Never merge unless `gh pr checks` / `mergeStateStatus` is `CLEAN`.** `BLOCKED` is usually just *pending required checks*, not a failure — poll until they finish, don't force-merge.
- **Secrets**: `gh secret set <NAME>` **without `--body`** — the interactive prompt keeps the value out of shell history. Never `gh secret set X --body "$TOKEN"`. Verify presence (not value) with `gh secret list`.
- **Submodule pin bump**: set the gitlink surgically with
  `git update-index --cacheinfo 160000,<commit-sha>,<submodule-path>` — no submodule checkout needed (works in a fresh worktree). Confirm the target SHA is pushed/tag-reachable on the submodule's remote first (`git ls-remote --tags <url> <tag>`).
- **`--no-verify`**: allowed ONLY for a commit with **no code and no secrets** (a submodule-pin bump, a `.gitmodules`/config-only change) when the repo's pre-commit gate is heavy and times out. Never for code or content commits — those must pass the hooks.
- **Shared repo / submodule**: edit via an isolated worktree branched from `origin/main` + PR, never in place — see `subagent-conflict-detection`.

## Repo settings (contribution-flow only)

This skill owns the *contribution-flow* repo config: merge-button policy
(`allow_squash_merge`, `delete_branch_on_merge`), branch protection requiring CI,
required status checks, and labels. **Security settings (Secret Scanning, push
protection) are owned by `apple-public-repo-security`** — set them there, not here.

## Common Mistakes

1. **Merging on a non-CLEAN status** — treating `BLOCKED` (pending checks) as a failure, or force-merging past a real red check. Poll; merge only on `CLEAN`.
2. **`gh secret set --body "$TOKEN"`** — leaks the token into shell history. Use the interactive prompt.
3. **Non-Conventional PR title** — fails a repo's title-lint gate; the PR can't merge.
4. **Editing a shared repo / submodule in place** — two writers clobber each other; use a worktree + PR.
5. **`--no-verify` on a code/content commit** — bypasses the gate that protects the repo. Reserve it for no-code/no-secret commits only.
6. **Hand-editing a submodule's checked-out files from the parent repo** — bump the pin instead (`git update-index --cacheinfo`), and land the submodule's own change via its own PR.
7. **Duplicating a sibling's job** — re-doing diff verification, security settings, or worktree conflict checks here instead of routing to the owning skill.

## Review Checklist

- [ ] Branch name uses a Conventional prefix; PR title is Conventional Commits.
- [ ] Commit carries the `Co-Authored-By:` trailer; PR body ends with the 🤖 footer.
- [ ] `gh pr checks` is `CLEAN` before merge; merged with `--squash --delete-branch`.
- [ ] Any secret was set via interactive `gh secret set` (no `--body`); verified with `gh secret list`.
- [ ] A submodule bump used `git update-index --cacheinfo` against a remote-reachable SHA.
- [ ] `--no-verify` used only on a no-code/no-secret commit, with the reason stated.
- [ ] Shared-repo/submodule edits went through a worktree + PR.
- [ ] Nothing here duplicates a sibling skill's scope.

## Related skills

- `pr-diff-verification` — verify `git show --stat HEAD` matches the commit's claims before push/PR.
- `apple-public-repo-security` — security repo settings + secret-leak prevention.
- `subagent-conflict-detection` — worktree + PR flow for parallel sessions / submodules.
- `claude-skill-plugin-packaging` — distributing/installing skill plugins.
````

- [ ] **Step 2: Verify name == dir**

Run: `grep '^name:' collaboration-skills/skills/github-contribution-workflow/SKILL.md`
Expected: `name: github-contribution-workflow`

- [ ] **Step 3: Commit**

```bash
git add collaboration-skills/skills/github-contribution-workflow/SKILL.md
git commit -m "feat(skills): add github-contribution-workflow (collaboration 12)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Wire SSOT — README + manifests (counts/versions)

**Files:**
- Modify: `README.md` (Catalog: add row, `(11)` → `(12)`)
- Modify: `collaboration-skills/.claude-plugin/plugin.json` (description "11" → "12"; version `1.2.0` → `1.3.0`)
- Modify: `.claude-plugin/marketplace.json` (collaboration-skills description "11" → "12", version `1.2.0` → `1.3.0`; `metadata.version` `1.2.0` → `1.3.0`)

**Interfaces:**
- Consumes: the skill dir from Task 1.
- Produces: README Catalog + counts + manifests consistent for the gate.

- [ ] **Step 1: Add the README Catalog row** under the collaboration-skills table (after `claude-skill-plugin-packaging`), and change the header `### collaboration-skills (11)` → `(12)`:

```markdown
| `github-contribution-workflow` | gh-CLI contribution loop — PRs, issues, GitHub file ops, secrets, contribution-flow repo settings; conventions + CLEAN-before-merge |
```

- [ ] **Step 2: Edit `collaboration-skills/.claude-plugin/plugin.json`** — change `"version": "1.2.0"` → `"1.3.0"`; in `description`, `"11 first-party"` → `"12 first-party"` and append `, and GitHub contribution workflow` to the skill list before the closing sentence.

- [ ] **Step 3: Edit `.claude-plugin/marketplace.json`** — `metadata.version` `1.2.0` → `1.3.0`; the `collaboration-skills` plugin entry `version` `1.2.0` → `1.3.0` and its `description` `"11 first-party"` → `"12 first-party"`.

- [ ] **Step 4: Commit**

```bash
git add README.md collaboration-skills/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "docs: wire github-contribution-workflow into Catalog + bump collaboration-skills 1.3.0

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Regenerate zh-Hant + green gate + skill review

**Files:**
- Modify (generated): `README.zh-Hant.md`

**Interfaces:**
- Consumes: README.md from Task 2.
- Produces: fresh zh-Hant `src-sha`; `mise run check` exit 0.

- [ ] **Step 1: Regenerate zh-Hant**

Run: `mise run readme-zh`
Expected: `README.zh-Hant.md` rewritten with a new trailing `<!-- src-sha: … -->`. (If `claude` is unavailable, translate the new Catalog row + count by hand and re-stamp with `printf '\n<!-- src-sha: %s -->\n' "$(git hash-object README.md)" >> README.zh-Hant.md`.)

- [ ] **Step 2: Run the gate**

Run: `mise run check; echo "exit=$?"`
Expected: `OK — 2 plugins (20/12), catalog + counts + zh-Hant consistent.` and `exit=0`.

> Note: the gate's `PLUGINS` map hardcodes `{"collaboration-skills": 11}`. Update it to `12` in `scripts/check-consistency.py` (line ~19) as part of this step — it is the gate's own count expectation, not a derived value. Commit it with this task.

- [ ] **Step 3: Self-review against `skill-authoring-patterns` Review Checklist** — confirm: router description with embedded `gh` commands + negative boundary ✓; scope-boundary routes to all four siblings ✓; decisions in a table ✓; Common Mistakes concrete + anti-pattern-named ✓; no project-specific workaround dressed as general guidance ✓.

- [ ] **Step 4: Commit**

```bash
git add README.zh-Hant.md scripts/check-consistency.py
git commit -m "chore: regenerate zh-Hant + gate count 12 for github-contribution-workflow

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: PR linking the issue

**Files:** none (release).

- [ ] **Step 1: Push + PR (closes the tracking issue)**

```bash
git push -u origin feat/github-contribution-workflow-skill
gh pr create --repo wei18/apple-dev-skills \
  --title "feat(skills): add github-contribution-workflow (collaboration 12)" \
  --body "Adds the 12th collaboration skill — the gh-CLI contribution loop (PRs, issues, GitHub file ops, secrets, contribution-flow repo settings) with this catalog's conventions. Composes with pr-diff-verification / apple-public-repo-security / subagent-conflict-detection / claude-skill-plugin-packaging via a scope boundary. Bumps collaboration-skills to 1.3.0.

Spec: docs/superpowers/specs/2026-06-25-github-contribution-workflow-design.md
Plan: docs/superpowers/plans/2026-06-25-github-contribution-workflow.md

Closes #8

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

- [ ] **Step 2: Verify CI CLEAN, then merge**

Run: poll `gh pr checks <n> --repo wei18/apple-dev-skills` until no `pending`; confirm `mergeStateStatus` `CLEAN`; then `gh pr merge <n> --squash --delete-branch`.

---

## Self-Review

**1. Spec coverage:** single skill in collaboration-skills ✓ (T1); router description + conventions + repo-settings-contribution-only ✓ (T1); scope boundary to 4 siblings ✓ (T1); gate impact README/plugin.json/marketplace/zh-Hant/count ✓ (T2–T3); issue/PR tracking ✓ (T4, Closes #8). No gaps.

**2. Placeholder scan:** none — full SKILL.md content is in T1 Step 1; manifest edits name exact fields/values.

**3. Type/name consistency:** `github-contribution-workflow` identical across SKILL.md `name`, dir, README row, and (implicitly) the gate's skill-set discovery. Count `12` consistent across README header, both manifests, and the gate's `PLUGINS` map (T3 Step 2). Version `1.3.0` consistent across plugin.json + marketplace plugin entry + marketplace metadata.
