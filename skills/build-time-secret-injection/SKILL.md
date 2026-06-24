---
name: build-time-secret-injection
description: Use when introducing an AdMob production ID (`GADApplicationIdentifier` / `GADBannerUnitID`), ASC API `.p8` key, or any "ships in binary but must stay out of public-repo PR diffs" identifier into an Apple-platform build. Codifies the xcconfig + Info.plist `$()` substitution + Bundle.main read pattern for build-time values, paired with `secrets/.env` for CLI tooling. Mirrors `Tuist/Signing.xcconfig` precedent. Includes multi-app `CI_PRODUCT` dispatch + built-bundle smoke-test guidance.
---

# Build-time Secret Injection (Apple-platform)

## Known testing gap

**This skill shipped without a TDD baseline test** (see `superpowers:writing-skills` Iron Law). The loophole list below is best-effort, captured retroactively from one incident (a production AdMob App ID leaked into an Info.plist comment in a PR) and one Architect review. Treat the rationalizations table as incomplete; revise on next leak incident.

## When to invoke

Any task that introduces or wires values which are:
- Technically **app-public** once the app ships (embedded in `Info.plist`, visible in shipped binary, observable in network traffic), AND
- **Pre-launch sensitive** (committed to public repo before ship = ad-fraud reconnaissance window, convention violation among collaborators, or fingerprinting of unreleased product)

Examples:
- AdMob App ID + Banner / Interstitial / Rewarded Unit IDs
- ASC API `.p8` key, key-id, issuer ID, ASC numeric app-id
- Any third-party SDK app key (Firebase, RevenueCat, etc.) where the convention is "hold until ship"

Do NOT invoke for:
- True per-deploy secrets (signing certs, CloudKit production API keys, push notification keys) — those have stricter patterns (see [[apple-public-repo-security]])
- Values genuinely public from day 1 (bundle IDs, CKContainer IDs, IAP product IDs, marketing URLs)

## The pattern (locked 2026-06-03)

### Two storage layers, one mechanism per layer

**Layer 1 — Build-time secrets (consumed by Xcode build process)**

```
Tuist/
  ├── <Domain>.xcconfig             # gitignored, real values
  ├── <Domain>.xcconfig.example     # committed, sandbox values + structure
  ├── Signing.xcconfig              # existing precedent (gitignored)
  └── Signing.xcconfig.example      # existing precedent (committed)
```

- xcconfig holds `KEY = VALUE` pairs
- `Project.swift` declares per-target `settings(configurations: [.debug(name:, xcconfig:), .release(name:, xcconfig:)])` pointing at the file
- Info.plist uses `$(KEY)` substitution to embed values at compile time
- App code reads via `Bundle.main.object(forInfoDictionaryKey: "...")` — guarded against nil / empty / unresolved `$()` token
- **CI side** (`ci_scripts/ci_post_clone.sh`): reads XCC env vars (stored as Secrets in ASC → Xcode Cloud → Workflow → Environment Variables) and generates the xcconfig file before `tuist generate` runs

**Layer 2 — CLI tooling secrets (consumed by `swift run <CLI>` etc.)**

```
secrets/
  ├── .env                          # gitignored, real values
  ├── .env.example                  # committed, structure + docstring
  ├── <Domain>AuthKey_*.p8          # gitignored binary cert
  └── .gitignore                    # deny-by-default: */!*.example/!README.md
```

- `.env` is `KEY=VALUE` shell-style
- Dev pattern: `source secrets/.env && swift run <CLI> --flag-using-$KEY ...`
- CLI itself does NOT need code changes to read env automatically

### Project.swift wiring (Tuist)

```swift
let sudokuTarget = Target.target(
    // ...
    settings: .settings(
        base: ["SWIFT_VERSION": "6"],
        configurations: [
            .debug(name: "Debug", xcconfig: "Tuist/Config-Debug.xcconfig"),
            .release(name: "Release", xcconfig: "Tuist/Config-Release.xcconfig"),
        ]
    )
)
```

Wrap multiple xcconfigs via a `Config-{Debug,Release}.xcconfig` that `#include?` both Signing + AdMob (Tuist's `xcconfig:` arg takes a single path).

### Multi-app dispatch in `ci_post_clone.sh`

When one repo ships multiple app schemes (e.g. AppA + AppB), XCC sets `$CI_PRODUCT` and `$CI_XCODE_SCHEME` per workflow. Case-switch on the scheme to pick the right env-var prefix:

```bash
case "${CI_XCODE_SCHEME:-${CI_PRODUCT:-}}" in
  AppA)
    APP_ID="${APPA_ADMOB_APP_ID:?missing APPA_ADMOB_APP_ID}"
    BANNER_UNIT_ID="${APPA_ADMOB_BANNER_UNIT_ID:?missing APPA_ADMOB_BANNER_UNIT_ID}"
    ;;
  AppB)
    APP_ID="${APPB_ADMOB_APP_ID:?missing APPB_ADMOB_APP_ID}"
    BANNER_UNIT_ID="${APPB_ADMOB_BANNER_UNIT_ID:?missing APPB_ADMOB_BANNER_UNIT_ID}"
    ;;
  *)
    echo "Unknown CI_XCODE_SCHEME: ${CI_XCODE_SCHEME:-}" >&2
    exit 1
    ;;
esac
cat > Tuist/AdMob.xcconfig <<EOF
ADMOB_APP_ID = ${APP_ID}
ADMOB_BANNER_UNIT_ID = ${BANNER_UNIT_ID}
EOF
```

Run **before** `tuist generate` so the per-target xcconfig reference resolves.

### Non-Tuist projects

If the project uses a hand-edited `.xcodeproj`, the equivalent storage is `Config/*.xcconfig` referenced via target → Build Settings → Base Configuration. Pattern is otherwise unchanged. Tuist regen / clobbering concerns don't apply; manual sync remains your responsibility.

### Smoke test scope (CRITICAL)

The substitution-resolution check must run against the **built bundle's** Info.plist, not the source-tree Info.plist:

```swift
// ❌ WRONG — reads source plist, gets literal "$(GADBannerUnitID)" — passes falsely
let plist = try PropertyListSerialization.propertyList(from: sourceData, ...)
#expect((plist["GADBannerUnitID"] as? String)?.isEmpty == false)  // passes for "$(...)" string

// ✅ RIGHT — combine source-plist key-presence test + runtime guard in code
// Source test catches "someone deleted the key"; runtime guard catches "substitution failed"
guard
    let bannerID = Bundle.main.object(forInfoDictionaryKey: "GADBannerUnitID") as? String,
    !bannerID.isEmpty,
    !bannerID.hasPrefix("$(")
else { preconditionFailure("...") }
```

A future PR should add a build-phase script that asserts no `$()` literals survived substitution into the built `.app/Info.plist`. Until then, the runtime guard is the catch.

## Anti-patterns to refuse

1. **Production IDs in code comments, docstrings, PR descriptions, commit messages, or `Info.plist <!-- -->` blocks.** Even when the value field uses a sandbox stand-in, the surrounding prose leaks production via git history. **Including the literal ID anywhere in tracked text — even prefixed by TODO / FIXME / "will-replace" — IS the leak.** Reference a project-memory or secrets file by name; never paste the value inline.

2. **Hardcoded production IDs in `Live.swift` with intent to "swap before release"** without an enforcement mechanism. The interim `fatalError("REPLACE_IN_v2.5.3:...")` pattern is acceptable as a TRANSITIONAL guard paired with xcconfig migration (see Migration §3), but is forbidden as a long-term standalone solution. Once xcconfig is in place, replace with: Info.plist `$()` + runtime guard verifying `Bundle.main.object(forInfoDictionaryKey:)` returns non-empty AND non-`$(...)`.

3. **Conflating GitHub Secrets with XCC env vars.** Apple's XCC does not read GH Secrets — they're separate storage. If CI builds on XCC, secrets must live in XCC's Environment Variables UI, not GH.

4. **Most common mistake**: ❗ **Shell env vars do NOT feed xcconfig `$(VAR)` interpolation.** xcconfig variable resolution reads from the build settings table, not process env. `source admob.env && xcodebuild archive` does NOT populate `$(SUDOKU_ADMOB_APP_ID)`. Only positional `xcodebuild VAR=value` or `-xcconfig override.xcconfig` actually injects, OR a CI script writes the xcconfig file before build. Architect review §A documents this fatal assumption.

5. **`Bundle.main.object(forInfoDictionaryKey:) as! String`** — force cast bypasses SwiftLint AND crashes hard if CI generation skipped + xcconfig missing. Use `as? String` + `guard let ... else { preconditionFailure }` with the unresolved-`$()` check.

6. **`Bundle.main` from inside a SwiftPM package** is fine for app-target composition root reads but flaky for #Preview / test host / unit-test contexts. Wrap reads in a smoke test that asserts the key exists in source plist; runtime guard compensates for missing-substitution case.

7. **`secrets/` or `Tuist/<Domain>.xcconfig` committed by accident.** Use an inner `secrets/.gitignore` deny-list (`* / !*.example / !README.md`) PLUS root `.gitignore` rules `Tuist/*.xcconfig` + `!Tuist/*.xcconfig.example` so neither slips through default-add operations.

8. **Tuist `tuist generate` silently clobbering unmanaged xcconfigs.** If `Tuist/<Domain>.xcconfig` exists but is NOT referenced in `Project.swift`'s `.settings(configurations:)`, Tuist regen drops it from the project. Verify Project.swift wiring before assuming xcconfig is active.

## Rationalizations table

| Rationalization | Counter |
|---|---|
| "But this is just a TODO comment, not the actual value" | Including the literal ID anywhere in tracked text IS the leak. Reference memory/secrets files by name, never paste the value. |
| "But the prod ID ships in the binary anyway" | Two adversary models: (a) pre-launch reconnaissance / ad-fraud preparation against the still-empty unit, (b) leak-through-co-authors. Both warrant pre-launch holdback. |
| "But our project doesn't use Tuist" | Pattern still applies; replace `Tuist/<Domain>.xcconfig` with `Config/<Domain>.xcconfig` referenced via target Base Configuration. |
| "But our app is private repo, who cares" | Applies when (a) repo may go public later (see [[apple-public-repo-security]]) or (b) collaborator set is broader than production-credential trust set. |
| "It's a 1-time integration; the skill is overkill" | No threshold. The FIRST secret is the one that establishes the leak channel. |
| "`fatalError("REPLACE_IN_...")` is fine for now; I'll migrate later" | fatalError-only is forbidden going forward. xcconfig + transitional fatalError IS the allowed combined state during one release cycle. |

## Checklist when adding a new secret value

1. Decide layer:
   - Consumed by Xcode build / Info.plist / Bundle.main read → Layer 1 xcconfig
   - Consumed by `swift run` / CLI scripts / shell → Layer 2 `.env`
2. Add KEY to appropriate `.example` file with sandbox/test default value
3. Add inline comment in `.example` describing purpose + where to find the real one (cite project memory file by name, NEVER the literal value)
4. If Layer 1: add `$(KEY)` substitution to `Info.plist`; add reading code via `Bundle.main` with guard (cover nil / empty / `$(...)` literal); add smoke test for key presence in source plist
5. If Layer 1 CI path: extend `ci_post_clone.sh` to write the new KEY from XCC env var with `${VAR:?missing message}` fail-fast; if multi-app, branch on `$CI_XCODE_SCHEME`
6. Run `grep -r "<real-prod-value>" .` (excluding gitignored dirs) — must return zero hits
7. Update memory `<domain>-credentials.md` to record real values + reference this skill by name

## Verification checklist (audit existing implementations)

- [ ] Root `.gitignore` has `Tuist/*.xcconfig` + `!Tuist/*.xcconfig.example`
- [ ] `secrets/.gitignore` inner deny-list present (`* / !*.example / !README.md`)
- [ ] `Project.swift` per-target `.settings(configurations:)` references the xcconfig
- [ ] `Info.plist` uses `$(KEY)` substitution for each secret
- [ ] App code reads via `Bundle.main.object(forInfoDictionaryKey:)` with guard (NOT `as!`)
- [ ] Runtime guard rejects `nil`, empty, and `$(...)` literal
- [ ] Smoke test reads source plist for key-presence assertion
- [ ] `ci_post_clone.sh` writes xcconfig BEFORE `tuist generate`
- [ ] Multi-app: `case` on `$CI_XCODE_SCHEME` selects per-app env vars
- [ ] XCC Workflow Environment Variables UI lists each KEY (per scheme if multi-app), marked Secret
- [ ] `grep -r "<real-prod-value>" .` returns zero hits across all tracked files

## Adjacent skills + memory

- **REQUIRED background**: [[apple-public-repo-security]] — broader secret-leak prevention (gitleaks, lefthook, GitHub Secret Scanning)
- **SIBLING**: [[monetization-sdk-integration]] — invoke together when wiring AdMob; this skill is the secret-handling layer
- **SIBLING**: your ASC submission-ops workflow (who may push what) — ASC API key handling more broadly
- Project memory file documenting the secret-scrubbing incident — the incident that triggered this skill pattern
- Project memory files for each credential set — real values held outside repo (cite by memory-file name, never paste inline)

## Migration playbook

**Disclosure**: In a real project, the initial AdMob secret-injection migration compressed the Architect's recommended 7-stage plan into a single PR. The sequence below reflects that compressed landing pattern, NOT the gold-standard staging. An Architect review session produced a 7-PR staged plan; save that detail in your own meeting log.

| PR | Scope | Notes |
|---|---|---|
| 1 | Scaffolding + Info.plist substitution + Live.swift Bundle.main + smoke tests + ci_post_clone.sh extension + secrets/.env.example (all in one) | Compressed shape. Architect would split into 3 PRs. |
| 2 | Build-phase substitution-resolution check (asserts no `$()` literals in built bundle) | Strictly stronger safety net than runtime guard alone. |
| 3 | gitleaks rule for `ca-app-pub-[0-9]{16}~[0-9]+` excluding Google universal test prefix | Closes the comment-leak class. |
| 4 | After two successful production releases via XCC env vars, remove transitional `fatalError` gates (if any remain) | Belt-and-suspenders graduation. |
| 5 | ADR + `docs/foundations.md` update | Locks the decision history. |

## AdMob env keys pattern

`secrets/.env` carries per-app production pairs (e.g. `APPA_ADMOB_APP_ID` /
`APPA_ADMOB_BANNER_UNIT_ID` and `APPB_*` twins). Two consumers render
`Tuist/AdMob.xcconfig` from them: XCC `ci_post_clone.sh` (from workflow
Secret env vars) and your TestFlight upload task (from `secrets/.env`).
Values live in secrets/.env (primary) + the XCC workflow config + the
project-memory files as recovery backup — never in code, comments, or diffs.
