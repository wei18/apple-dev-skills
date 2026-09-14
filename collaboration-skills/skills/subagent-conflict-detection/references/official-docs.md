Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Create custom subagents | https://code.claude.com/docs/en/sub-agents | Native mechanism section |
| Run parallel sessions with worktrees | https://code.claude.com/docs/en/worktrees#choose-the-base-branch | Pre-dispatch base correctness; references/ baseRef table, fallbacks, v2.1.208 |
| Run parallel sessions with worktrees | https://code.claude.com/docs/en/worktrees#copy-gitignored-files-into-worktrees | references/ table "head" row: `.worktreeinclude` |
| Configure permissions | https://code.claude.com/docs/en/permissions#read-only-commands | Step 1 prompt expectations: per-subcommand matching; the `cd` + `git` prompt; the built-in read-only set |
| Claude Code changelog | https://code.claude.com/docs/en/changelog | v2.1.98: false prompts fixed for `cut -d ...` and `awk '{print $1}' file`, so a Step-1 `grep | cut | tail` pipeline is expected to run without a prompt |
| Git - git-worktree Documentation | https://git-scm.com/docs/git-worktree | `list --porcelain` ("The main worktree is listed first"); `prune`; REFS (stash shared across worktrees) |
| Git - git-push Documentation | https://git-scm.com/docs/git-push | Anti-pattern "Parallel-dispatch race": `--force-with-lease` semantics |
