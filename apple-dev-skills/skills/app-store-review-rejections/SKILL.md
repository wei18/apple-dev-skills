---
name: app-store-review-rejections
description: Use when preparing an App Store submission, diagnosing an App Review rejection / Resolution Center message, or hardening a free game/app with ads + Remove-Ads IAP + CloudKit + Game Center against the rejection classes it realistically hits. Covers guideline 1.3 / 2.1 / 2.3 / 2.5.x / 3.1.1 / 4.0 / 4.3 / 5.1.1 / 5.1.2, the ATT-vs-AdMob trap, privacy-label parity, and a pre-submit checklist.
---

# App Store Review Rejections

## Overview

App Review rejects on a small set of recurring guideline violations. Per Apple's
own transparency reporting, **performance/completeness (2.1) is the #1 cause**, and
**privacy (5.1.x)** is the leading policy cause. This skill maps the rejection
classes that **a free game/app with banner ads + a Remove-Ads IAP + CloudKit +
Game Center** realistically hits, to a concrete pre-submission fix. These examples
assume a free app with banner ads + a Remove-Ads IAP + CloudKit + Game Center; the
guideline classes apply broadly — skip sections that don't fit your app's feature set.

It is the *content* companion to your ASC submission-ops workflow (which says **who** may push
each ASC button); this says **why a build gets bounced and how to pre-empt it**.

## When to use

- Before any TestFlight→App Store submission (your TestFlight upload workflow got the build up; this gates whether it passes review).
- A Resolution Center message arrived citing "Guideline X.Y" — find the row, apply the fix.
- Auditing a new app/game for submission-readiness.
- NOT for the *mechanics* of submitting (that's your ASC submission-ops workflow) or screenshot generation (that's your screenshot-generation pipeline).

## Quick reference — rejection class → fix (weighted to these apps)

| Guideline | Why it bounces a puzzle-game-with-ads | Pre-submit fix here |
|---|---|---|
| **2.1 App Completeness** | Crash on reviewer's device/OS, dead-end flow, placeholder content, ad fails to load → blank space, debug/test ad shown in the prod build | Run the build on a *clean* device + the oldest supported OS. Ensure ads degrade gracefully (no empty frame on no-fill). TF builds should carry **prod** (not test) ad IDs — verify real ads render, not test units. No `<TRANSLATE>` / lorem strings. |
| **2.3.1 Hidden features** | Shipping dormant code / hidden toggles reviewers can reach | No DEBUG-only surfaces (NearWin hooks) reachable in Release. |
| **2.3.3 Screenshots** | Screenshots don't match the actual app, wrong dimensions, contain device frames Apple disallows, alpha channel | Do **not** upload snapshot-test baselines directly — they have an alpha channel + wrong dims (use your screenshot-generation pipeline). Use real device/sim captures at exact spec sizes. |
| **2.3.10 Irrelevant metadata** | Mentioning Android / "also on Google Play", other platform names in description/keywords | Strip platform references from all 7 locales' metadata. |
| **3.1.1 In-App Purchase** | Remove-Ads unlock sold outside IAP; **no "Restore Purchases" control**; price/benefit unclear | Remove-Ads must be StoreKit IAP (it is — [[monetization-sdk-integration]]). Apple's wording is "you *should* have a restore mechanism," but it is enforced in practice as mandatory — ship a visible **Restore Purchases** button; non-consumable must restore on reinstall. |
| **4.3(a)/(b) Spam / saturation** | **Highest latent risk** — saturated genres (puzzle, utility) face 4.3(b) "indistinguishable from what's already available" risk. (Apple's *enumerated* 4.3(b) examples are flashlight/sound-effects/wallpaper/timer/fortune-telling — puzzle games aren't named; the risk is inferred from saturation, not an explicit callout.) A thin clone gets bounced as spam. | Lead with genuine differentiation (design system, content hub, Game Center, cross-platform). Distinct app name/icon/screenshots per app; never ship two near-identical binaries under different names (4.3(a) = same app under multiple Bundle IDs). |
| **4.0 / 4.2 Minimum functionality** | Too simple, feels like a web wrapper or template | Native features (haptics, Game Center, iCloud resume, widgets if any) demonstrate platform depth. |
| **5.1.1(v) Account deletion / data** | App "supports account creation" but offers no in-app deletion path | Apple's text triggers the deletion requirement only for apps that **"support account creation"**. If the app has no app-specific account-creation flow (identity via iCloud / Game Center), 5.1.1(v) likely doesn't apply — confirm for your app. But **Apple publishes NO explicit iCloud/Game-Center exemption**, so don't assert one as fact. Still: provide a way to clear the user's CloudKit data + a reachable privacy-policy URL. If rejected on 5.1.1(v), reply to Review that the app creates no app-specific account and data-clearing is available, rather than claiming a blanket exemption. |
| **5.1.1 Privacy policy** | Missing/unreachable privacy policy URL in ASC + in-app | Privacy policy URL set in App Privacy + reachable; covers ads (AdMob) + analytics data. |
| **5.1.2 Data Use — ATT** | **The AdMob trap.** App accesses `ASIdentifierManager.advertisingIdentifier` (IDFA) or presents the ATT prompt via UMP but lacks `NSUserTrackingUsageDescription`, or never shows the prompt at all | ATT is required when the app accesses IDFA (`ASIdentifierManager.advertisingIdentifier`) or presents the ATT prompt via UMP. **AdMob can serve limited/non-personalized ads without accessing IDFA — in that case ATT is not required** (though UMP/GDPR consent may still apply). When ATT is required: `NSUserTrackingUsageDescription` present in **all 7 locales**, ATT prompt shown via UMP before personalized ads. Ensure each new app in a multi-app repo has its own ATT primer coordinator component — it is a submission blocker if missing. If you do NOT access IDFA, declare so and don't link to it. Note: reviewers sometimes cite **2.1 (Information Needed)** instead of 5.1.2 when they simply can't *find* where the prompt fires — the sim-verify checklist item below covers both. |
| **Privacy-label parity** | App Privacy "nutrition" answers in ASC contradict `PrivacyInfo.xcprivacy` / actual SDK behavior (AdMob collects identifiers + usage data) | ASC App Privacy answers must match the committed `PrivacyInfo.xcprivacy` and AdMob's declared collection. Keep them in sync ([[apple-three-piece-analytics]]). |
| **Age rating / 1.3** | Ads can serve mature content but rating says 4+ | Set AdMob max ad content rating appropriately; age rating must cover ad content. |
| **2.5.x / export compliance** | Build held "Processing" pending the encryption/export-compliance answer | Answer export compliance in ASC (uses standard crypto only) — user-owned, see your TestFlight upload workflow footgun. |

## Pre-submission checklist (run before flipping a build to "Submit for Review")

1. Clean-device + oldest-OS smoke run; no crash, no blank ad frame, no debug surface.
2. L10n gate green — 0 `<TRANSLATE>`, all 7 locales complete (rejection-grade for 2.1/2.3).
3. ATT: `NSUserTrackingUsageDescription` localized ×7; **sim-verify the ATT prompt actually fires** on a fresh install (drive it with an interactive simulator drive, e.g. idb / simctl tap + screenshot — reviewers reject on the *runtime* prompt being absent, not just the Info.plist key); ATT primer present in every shipped app.
4. Restore-Purchases button visible; Remove-Ads restores on reinstall.
5. ASC App Privacy answers == `PrivacyInfo.xcprivacy` == AdMob's declared data use.
6. Screenshots are real captures at spec dimensions (not snapshot baselines).
7. Privacy-policy URL set and reachable; no other-platform mentions in any locale's metadata.
8. Per-app distinct name/icon/screenshots; differentiation visible in the first screenshot (4.3).

## Common mistakes

- **Trusting "it compiled / TF accepted it."** Upload success ≠ review pass; the gates above are orthogonal to a green build.
- **Re-using snapshot PNGs as store screenshots** — wrong dims + alpha → 2.3.3.
- **Adding the ad SDK but skipping ATT** — the single most common ads-app 5.1.2 bounce.
- **Filling App Privacy by guesswork** — must mirror the actual SDK + `PrivacyInfo.xcprivacy`, or it's a 5.1.x mismatch.
- **Shipping a sibling app as a near-clone** — 4.3 spam; sharing code is fine, but each product must have a distinct identity.

## Sources

Apple App Store Review Guidelines (developer.apple.com) + Apple App Store
Transparency Report (performance = top rejection cause); Google AdMob iOS privacy
strategies (ATT / UMP / `NSUserTrackingUsageDescription`). Re-verify guideline
numbers against the live Guidelines before quoting them in a Resolution Center
reply — Apple renumbers.
