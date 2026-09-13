Official pages backing this skill's claims; read when verifying or updating a factual or version-sensitive claim.

| Page | URL | Backs |
|---|---|---|
| Removing sensitive data from a repository | https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository | Leak SOP order: rotate first, then `filter-repo`, GC, forks |
| Supported secret scanning patterns | https://docs.github.com/en/code-security/secret-scanning/introduction/supported-secret-scanning-patterns | No Apple-specific provider pattern; `generic_private_key` covers `.p8`/PEM, plus `ec_private_key` |
| About secret scanning | https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning | Public repos get secret scanning automatically for free |
| Enabling secret scanning for generic patterns | https://docs.github.com/en/code-security/how-tos/secure-your-secrets/detect-secret-leaks/enabling-secret-scanning-for-generic-patterns | Generic patterns must be enabled separately (Security & Analysis -> Generic patterns) |
| About secret scanning alerts | https://docs.github.com/en/code-security/concepts/secret-security/about-alerts | Generic-pattern scanning requires opting in first |
| git-filter-branch | https://git-scm.com/docs/git-filter-branch | "its use is not recommended" |
| gitleaks README | https://github.com/gitleaks/gitleaks | `gitleaks git --pre-commit --staged`, `gitleaks dir` |
| Writing custom build scripts | https://developer.apple.com/documentation/xcode/writing-custom-build-scripts | `ci_scripts`; a non-zero exit fails the build |
| Environment variable reference | https://developer.apple.com/documentation/xcode/environment-variable-reference | `CI_PRIMARY_REPOSITORY_PATH` |
