---
name: apple-public-repo-security
description: Security baseline for public iOS / macOS repos — secret classification (CloudKit PEM, ASC API Key, APNs key, signing cert, provisioning profiles), `.gitignore` baseline, mise-managed gitleaks + lefthook pre-commit hooks, Xcode Cloud `ci_post_clone.sh` as second line, GitHub Secret Scanning Alerts as passive third line, leak SOP (rotate-first, `git filter-repo`, accept fork persistence), Apple upstream telemetry disclosure (MetricKit / Game Center / sysdiagnose). Invoke when a repo will go public from day 1, when an existing private repo plans to open-source, when secrets enter a build pipeline, or when asked "how to prevent secret leaks in a public repo". This is the repo-hygiene baseline (gitignore / gitleaks / leak SOP); for the ship-in-binary build-time identifier pattern (AdMob app ID via xcconfig `$()` injection) see build-time-secret-injection.
---

# Apple Public Repo Security

## When to invoke

- The repo will be public from day 1.
- An existing private repo is planning to open-source.
- A new secret is being introduced (CloudKit server-to-server key, APNs key, ASC API key).
- User asks "how do I prevent secret leaks in a public repo", "how do I configure Xcode Cloud secrets", "what to do after a leak".

## Default decisions

### Public commitment from day 1

- No "private first, public later" transition — there's no escape hatch to "clean history later".
- No commit in the repo's history may contain secret values, PII, or identifiable player data.
- A violation, once it happens, is treated as **already leaked** and the secret is rotated.

### Secret classification

| Secret | Purpose | Storage |
|---|---|---|
| CloudKit server-to-server key (Key ID + PEM) | Backend API | Xcode Cloud Env Vars (Secret); locally in `~/.config/<project>/` (chmod 600) or Keychain |
| App Store Connect API Key (`.p8` + Key ID + Issuer ID) | TestFlight / submission automation | Xcode Cloud Env Vars (Secret) |
| APNs Auth Key (`.p8` + Key ID + Team ID) | Push notifications | Xcode Cloud Env Vars (Secret) |
| Signing certificate + private key (`.p12`) | Code signing | Xcode Cloud automatic signing, hosted by Apple |
| Provisioning profiles | Code signing | Xcode Cloud Apple-managed |
| Player identification data | Runtime debug | OSLog `.private` interpolation; **never** committed to git |

### Things that must not enter git

- The actual content of the secrets above (including base64-encoded forms)
- Real player aliases / displayNames / playerIDs (except after hashing)
- Apple Developer Team ID / DUNS / address (if they appear in entitlements / profile metadata)
- Build logs containing secrets (redact before viewing)
- Developers' local `.config/<project>/` real files
- Personal notes / drafts (like `NOTES.md.private`)

### Starter `.gitignore`

```
# Secrets / credentials
*.pem
*.p8
*.p12
*.mobileprovision
*.cer
.env
.env.*
!.env.example
secrets/

# Xcode / build
DerivedData/
build/
xcuserdata/
*.xcuserstate
.swiftpm/

# macOS
.DS_Store

# Personal notes
*.private.md
NOTES.md.private

# Local development secrets directory (chmod 600 PEMs / API keys live here)
.config/
!.config/example/         # If a public example directory exists, allow listing it
```

### Three lines of defence

| Line | Tool | Scope |
|---|---|---|
| 1. Local pre-commit | `lefthook` + `gitleaks` (via `mise`) | Catches staged diffs; can be bypassed with `--no-verify` |
| 2. CI post-clone | Xcode Cloud `ci_post_clone.sh` runs `gitleaks` | Catches at PR time; fails the build; earliest stage is cheapest |
| 3. GitHub Secret Scanning Alerts | GitHub platform (free on public repos) | Passive detection; Apple-issued secret patterns auto-revoke via partner program |

`lefthook.yml` example:

```yaml
pre-commit:
  parallel: true
  commands:
    gitleaks:
      run: mise exec gitleaks -- git --pre-commit --staged --redact --verbose
```

`ci_post_clone.sh` example:

```bash
mise install
mise exec gitleaks -- git --pre-commit --staged --redact
if [ $? -ne 0 ]; then
  echo "gitleaks detected potential secrets — failing build"
  exit 1
fi
```

### Leak SOP (rotate before cleaning history)

1. **Rotate first** (rotation is the real stop-bleed; after a force push, GitHub reflog / forks may still reach the secret for up to 90 days, and **any fork retains it forever**):
   - CloudKit Dashboard: rotate the server-to-server key
   - Rotate the ASC API key
   - Rotate the APNs key
   - Signing cert leak: revoke + reissue in Apple Developer Center
2. Use [`git filter-repo`](https://github.com/newren/git-filter-repo) to clean history + force push (**`git filter-branch` is deprecated, do not use**)
3. Notify GitHub support to purge forks / caches — **acknowledge that fork removal is not guaranteed**
4. Open an incident log + lessons learned under `meetings/`
5. **Do not** continue other development until the four steps above are done

### Setup templates (shipped in the repo)

- `.env.example`: list all env var keys with placeholder values
- `.config/<project>/example/README.md`: explain the local PEM directory layout (**do not include a `.pem.example` real file** — gitleaks's built-in `private-key` rule fires on the header alone; if you must include a real example, explicitly allowlist it in `.gitleaks.toml`)
- `docs/setup.md`: first-clone steps for new developers

### Public commitment on Apple upstream channels

The App's commitment to users (aligned with `PrivacyInfo.xcprivacy`):

- **No PII collection**
- **No third-party tracking SDK**
- **The App does not upload events to "our" servers** (CloudKit / Game Center are provided by Apple)

Legitimate Apple upstream channels (users can disable in Settings):
- MetricKit `MXMetricPayload` → ASC Power & Performance (*Settings → Privacy → Analytics & Improvements*)
- Game Center scores / achievements (*Settings → Game Center*)
- ASC crash reports / TestFlight beta crashes (when the user enables Share Analytics)
- sysdiagnose (when the user actively shares via Feedback Assistant; OSLog `.private` is redacted here)

### Extra responsibilities for code reviewers

Every PR review additionally checks:
- No new secret pattern slipped through
- No secret values mentioned in docs / comments / commit messages / PR descriptions
- No identifiable info in screenshots / assets
- If privacy claims change → `PrivacyInfo.xcprivacy` + App Store metadata are updated in sync
- Any "temporarily log PII for debug" helper is removed before merging

## Rationale

- Three lines of defence are standard defence-in-depth, with complementary interception stages.
- The rotate-first SOP reflects the reality that "git history is permanently reachable in forks" — cleaning history is **not** stopping the bleed.
- Apple-issued secrets go through GitHub's partner program for auto-revocation; the third line is a free, must-enable layer.

## Deviation considerations

- **Private repo planning to go public later**: start with this skill, but allow some templates (e.g. `.pem.example`) to hold real files temporarily; clean up before going public.
- **No CI (pure local development)**: the first line of defence (local pre-commit hook) can be bypassed by `git commit --no-verify` — this cannot be technically blocked client-side. Educate contributors, and rely on the second line (CI gitleaks in `ci_post_clone.sh`) as the actual hard gate. Without CI, the second line is missing entirely; mitigations are social (code review, contributor education) rather than technical.
- **Internal corporate repo**: the third line (GitHub platform) can be skipped, but the first and second still apply.

## Verification checklist

- `.gitignore` covers the secret file extensions listed above.
- `.mise.toml` includes gitleaks + lefthook.
- `lefthook.yml` runs gitleaks pre-commit.
- `ci_post_clone.sh` runs gitleaks with fail-on-detect.
- GitHub Settings → Code security → Secret scanning alerts is enabled.
- `docs/setup.md` instructs `lefthook install` to activate hooks.
- `PrivacyInfo.xcprivacy` is consistent with the public commitments.

## Related skills

- `mise-tool-management`: gitleaks + lefthook installed via mise.
- `xcode-cloud-single-track-ci`: `ci_post_clone.sh` is where the second line lives.
- `oslog-logger-defaults`: `.private` interpolation matches the sysdiagnose redaction semantics.
- `apple-three-piece-analytics`: "no third-party SDK" is one of the public commitments.
