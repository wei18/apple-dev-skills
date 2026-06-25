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
