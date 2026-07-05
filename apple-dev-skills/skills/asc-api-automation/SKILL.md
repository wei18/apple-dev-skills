---
name: asc-api-automation
description: Use when automating App Store Connect from a CLI or CI — mint the ES256 JWT from an ASC API `.p8` key (`kid`, `iss` = Issuer ID, `aud` `appstoreconnect-v1`, exp ≤ 20 min), then drive `api.appstoreconnect.apple.com` with curl for TestFlight `betaGroups` / `betaBuildLocalizations`, `appStoreVersions` metadata, `reviewSubmissions` submit-for-review, `salesReports` / `analyticsReportRequests`. No fastlane, no Ruby — a CryptoKit token script + curl. Invoke when asked "automate TestFlight / submission / release notes", writing release tooling, or debugging 401 NOT_AUTHORIZED / 429 RATE_LIMIT_EXCEEDED. API-side ops only: build & upload → xcode-cloud-single-track-ci; `.p8` storage / leak prevention → build-time-secret-injection + apple-public-repo-security.
---

# App Store Connect API Automation

This catalog's default way to drive App Store Connect from scripts and CI: an Apple-native toolchain — a ~30-line Swift/CryptoKit script mints the JWT, plain curl calls the REST API. No fastlane/spaceship, no Ruby gems, no Homebrew, consistent with the catalog's mise + no-third-party baselines.

## When to invoke

- Writing release tooling: distribute a build to TestFlight groups, set what's-new, create the next App Store version, submit for review
- Pulling sales or App Store analytics reports on a schedule
- Debugging ASC API auth failures (401 `NOT_AUTHORIZED`) or rate limiting (429)
- Asked "should I use fastlane for this?"

## Scope

Owns: token minting, curl conventions, and the endpoint cookbook below. Does NOT own:

- **Building / uploading the binary** — there is no REST endpoint for `.ipa` upload; builds arrive in ASC via Xcode Cloud (→ [[xcode-cloud-single-track-ci]]), Xcode Organizer, or Transporter. This skill picks up *after* the build exists in ASC.
- **`.p8` key storage & leak prevention** → [[build-time-secret-injection]] (Layer 2 `secrets/.env`) + [[apple-public-repo-security]] (rotate-first SOP).
- **What metadata will pass review** → [[app-store-review-rejections]]; this skill is *how* to submit, not *what*.

## Keys: create, scope, store

| Key kind | Where | JWT identity claim | Use for |
|---|---|---|---|
| **Team key** (default) | Users and Access → Integrations; role-scoped | `iss` = Issuer ID | CI and shared tooling — pick the least-privilege role that works (App Manager covers release ops; avoid Admin) |
| **Individual key** | Your user profile → Individual API Key | `sub: "user"` (no `iss`) | Personal one-off scripts; inherits *your* permissions |

Store per [[build-time-secret-injection]] Layer 2:

```bash
# secrets/.env (gitignored; .env.example committed)
ASC_KEY_ID=2X9R4HXF34
ASC_ISSUER_ID=57246542-96fe-1a63-e053-0824d011072a
ASC_KEY_PATH=secrets/AuthKey_2X9R4HXF34.p8
```

## Mint the token (CryptoKit, zero dependencies)

Claims (verified against Apple's *Generating tokens for API requests*, 2026-07): header `alg: ES256` (the only accepted algorithm), `kid`, `typ: JWT`; payload `iss` (**Issuer ID**, the UUID from Users and Access → Integrations — not your Team ID), `iat`, `exp` (invalid if more than 20 minutes ahead), `aud: "appstoreconnect-v1"`, optional `scope` (array of allowed requests like `"GET /v1/apps"` — pin single-purpose tokens to single endpoints).

`scripts/mint-asc-token.swift`:

```swift
#!/usr/bin/env swift
import CryptoKit
import Foundation

let env = ProcessInfo.processInfo.environment
guard let keyID = env["ASC_KEY_ID"], let issuerID = env["ASC_ISSUER_ID"],
      let keyPath = env["ASC_KEY_PATH"] else {
    FileHandle.standardError.write(Data("Set ASC_KEY_ID / ASC_ISSUER_ID / ASC_KEY_PATH (source secrets/.env)\n".utf8))
    exit(1)
}

func b64url(_ data: Data) -> String {
    data.base64EncodedString()
        .replacingOccurrences(of: "+", with: "-")
        .replacingOccurrences(of: "/", with: "_")
        .replacingOccurrences(of: "=", with: "")
}

let now = Int(Date().timeIntervalSince1970)
let header = #"{"alg":"ES256","kid":"\#(keyID)","typ":"JWT"}"#
// Apple rejects exp > 20 min ahead; 10 min leaves slack for clock skew.
let payload = #"{"iss":"\#(issuerID)","iat":\#(now),"exp":\#(now + 600),"aud":"appstoreconnect-v1"}"#
let signingInput = b64url(Data(header.utf8)) + "." + b64url(Data(payload.utf8))

let pem = try String(contentsOfFile: keyPath, encoding: .utf8)
let key = try P256.Signing.PrivateKey(pemRepresentation: pem)
let signature = try key.signature(for: Data(signingInput.utf8))  // ECDSA + SHA-256 = ES256
print(signingInput + "." + b64url(signature.rawRepresentation))  // rawRepresentation = r‖s, the JWT wire format
```

```bash
source secrets/.env
ASC_TOKEN=$(swift scripts/mint-asc-token.swift)
curl -sf -H "Authorization: Bearer $ASC_TOKEN" "https://api.appstoreconnect.apple.com/v1/apps?limit=200"
```

Mint fresh per run; a job that outlives the token re-mints instead of extending `exp`.

## curl conventions

- **JSON:API shape** — write calls send `Content-Type: application/json` with the body wrapped as `{"data": {"type": ..., "id": ..., "attributes": {...}, "relationships": {...}}}`.
- **Pagination** — pass `limit=200` (the max) and follow `links.next` until absent; the small default page size silently truncates lists otherwise.
- **Rate limit** — every response carries `X-Rate-Limit: user-hour-lim:3500; user-hour-rem:…` (rolling hour, per key; Apple says actual limits vary). Exceeding returns 429 `RATE_LIMIT_EXCEEDED` — back off and re-queue; a 429 lockout hits *everything* sharing that key, including CI.
- **Errors are structured** — read `.errors[].detail`. Triage: 401 = token/claims problem, 403 = key role or `scope` problem, 409 = resource state problem (e.g. version not in a submittable state).

## Endpoint cookbook

| Goal | Call |
|---|---|
| App's ASC id | `GET /v1/apps?filter[bundleId]=<bundle-id>` |
| Latest processed builds | `GET /v1/builds?filter[app]=<appId>&sort=-uploadedDate&limit=5` |
| TestFlight what's-new | `GET /v1/builds/<id>/betaBuildLocalizations` → `PATCH /v1/betaBuildLocalizations/<locId>` with `attributes.whatsNew` |
| Add build to a beta group | `POST /v1/betaGroups/<groupId>/relationships/builds` with `{"data":[{"type":"builds","id":"<buildId>"}]}` |
| Create next App Store version | `POST /v1/appStoreVersions` — relationship `app`, attributes `platform: "IOS"`, `versionString` |
| Set description / what's-new | `GET /v1/appStoreVersions/<id>/appStoreVersionLocalizations` → `PATCH /v1/appStoreVersionLocalizations/<locId>` |
| Attach build to version | `PATCH /v1/appStoreVersions/<id>/relationships/build` |
| Submit for review | `POST /v1/reviewSubmissions` (app + platform) → `POST /v1/reviewSubmissionItems` (reviewSubmission + appStoreVersion) → `PATCH /v1/reviewSubmissions/<id>` with `attributes.submitted: true` |
| Daily sales report | `GET /v1/salesReports?filter[frequency]=DAILY&filter[reportType]=SALES&filter[reportSubType]=SUMMARY&filter[vendorNumber]=<n>` (+ `filter[reportDate]=YYYY-MM-DD` for a specific day) — response is a **gzipped TSV**, not JSON: `curl -o report.gz` then `gunzip` |
| App Store analytics | `POST /v1/analyticsReportRequests` (`accessType: "ONGOING"`) once per app, then poll its `reports` → instances → segments for download URLs |

The review-submission flow is the 2022+ `reviewSubmissions` model, which replaced the deprecated one-shot `appStoreVersionSubmissions`.

## Rationale

- **No fastlane by default**: spaceship drags a Ruby toolchain into a repo whose only Ruby consumer would be release tooling — against the catalog's mise/no-Homebrew baseline — and inserts a drift layer that breaks whenever ASC changes ahead of a spaceship release. Direct REST against Apple's own docs has zero intermediary.
- **CryptoKit mint script**: token minting is the only genuinely fiddly step (ES256, raw-signature format); everything after is plain curl. A 30-line Apple-native script beats installing PyJWT or hand-rolling openssl DER conversion.
- **Least privilege**: token-leak blast radius scales with the key's role; the `scope` claim can pin a single script to a single request.

## Deviation considerations

- **Already on fastlane** with maintained lanes and a Gemfile → keep it; this skill is the default for repos *without* a Ruby toolchain, not a migration mandate.
- **Heavy tooling** (dozens of endpoints, typed models, retries) → generate a client from Apple's published App Store Connect OpenAPI spec instead of hand-rolled curl; still no fastlane required.
- **One-off manual task** → the ASC web UI is faster; scripting has a floor cost.

## Common Mistakes

1. **`iss` set to Team ID** — ASC API wants the **Issuer ID** (UUID); Team ID belongs to other Apple JWTs (e.g. APNs). Symptom: 401 `NOT_AUTHORIZED` with a well-formed token.
2. **`exp` more than 20 minutes ahead** — token rejected outright; also watch local clock skew on `iat`.
3. **openssl-signed tokens failing** — `openssl dgst` emits a DER-encoded signature; JWT ES256 requires the raw 64-byte r‖s form. CryptoKit's `rawRepresentation` is already correct.
4. **Uploading the binary via REST** — no such endpoint exists; route builds through Xcode Cloud / Organizer / Transporter.
5. **Ignoring pagination** — the default page size silently truncates; always `limit=200` + follow `links.next`.
6. **Parsing `salesReports` as JSON** — it's a gzipped TSV file.
7. **Tight-polling build processing or analytics** without reading `X-Rate-Limit` — 429 locks out every consumer of the key.
8. **Admin-role key in CI** when App Manager or a `scope`d token suffices.
9. **`.p8` committed to the repo** — stop and run the rotate-first SOP in [[apple-public-repo-security]]; storage layout per [[build-time-secret-injection]].

## Review Checklist

- [ ] Team key with least-privilege role; `.p8` + IDs stored per build-time-secret-injection Layer 2, nothing tracked by git
- [ ] Token claims: ES256, `kid` header, `iss` = Issuer ID (or `sub: "user"` for individual keys), `exp` ≤ 20 min, `aud` `appstoreconnect-v1`
- [ ] Every collection call sets `limit` and follows `links.next`
- [ ] 429 handled with backoff; no tight polling loops
- [ ] Write calls use the JSON:API `{"data": {...}}` wrapper
- [ ] No REST binary-upload attempt; build side delegated to xcode-cloud-single-track-ci
- [ ] `grep` for key IDs / issuer ID / `.p8` contents across tracked files returns zero hits

## Related skills

- [[xcode-cloud-single-track-ci]] — build & upload side; this skill starts after the build exists in ASC
- [[build-time-secret-injection]] — where `ASC_KEY_ID` / `ASC_ISSUER_ID` / the `.p8` live (Layer 2 `secrets/.env`)
- [[apple-public-repo-security]] — `.p8` leak prevention and the rotate-first SOP
- [[app-store-review-rejections]] — *what* to submit so review passes; this skill is *how* to submit
