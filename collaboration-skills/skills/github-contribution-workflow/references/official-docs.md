Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| GitHub GraphQL public schema (docs.github.com) | https://docs.github.com/public/fpt/schema.docs.graphql | `mergeStateStatus` values: `CLEAN` "Mergeable and passing commit status", `BLOCKED`, `UNSTABLE`, `BEHIND`, `HAS_HOOKS` (GHES pre-receive hooks), `UNKNOWN` |
| gh pr checks | https://cli.github.com/manual/gh_pr_checks | "Check CI before merge"; `--watch` / `--fail-fast`; exit code 8 = checks pending only when run without `--watch` |
| gh pr view | https://cli.github.com/manual/gh_pr_view | `--json mergeStateStatus` is a valid field |
| gh pr merge | https://cli.github.com/manual/gh_pr_merge | `--squash --delete-branch`; `--match-head-commit` |
| gh secret set | https://cli.github.com/manual/gh_secret_set | Conventions Secrets: without `--body` the value is read from standard input |
| REST API endpoints for repository contents | https://docs.github.com/en/rest/repos/contents#create-or-update-file-contents | "Create/Edit a file via GitHub": `content` is Base64; `sha` is "Required if you are updating a file" |
| REST API endpoints for repositories | https://docs.github.com/en/rest/repos/repos#update-a-repository | "Configure merge": `allow_squash_merge`, `delete_branch_on_merge` |
| Git - git-update-index Documentation | https://git-scm.com/docs/git-update-index | Submodule pin bump: `--cacheinfo <mode>,<object>,<path>` |
| Git - git-commit Documentation | https://git-scm.com/docs/git-commit | `--no-verify` bypasses `pre-commit` and `commit-msg` |
