# Steps With No ASC API At All

## Steps with no ASC API at all — must be clicked by a human

The three prerequisites above are gaps in an otherwise-scriptable flow. These are different:
Apple publishes no REST resource for them at all, so no amount of scripting closes the gap —
budget a manual, one-time (or rarely-repeated) click in the ASC web UI.

- **Verified ✓ — Agreements, Tax, and Banking (including accepting the Paid Apps Agreement).**
  Apple's App Store Connect API topic index (`developer.apple.com/tutorials/data/documentation/AppStoreConnectAPI.md`,
  checked 2026-09) lists every automatable area — App Store, TestFlight, Game Center,
  Provisioning, Xcode Cloud, Webhooks, Reporting, Users and Access, Alternative App
  Distribution — and "Agreements, Tax, and Banking" is absent from all of them; no
  `agreements`/`taxForms`/`bankAccounts`-shaped resource exists anywhere in the reference.
  ASC Help's *Schedule price changes for apps* page confirms the practical consequence for
  this skill's pricing prerequisite above: "If you've accepted the Paid Apps Agreement and
  submitted your app for review, you can schedule price changes for your app" — the
  Agreement is accepted only in ASC's *Manage Agreements* section, by the Account Holder, in
  the browser. This is the actual gate behind the "app pricing must be set first" prerequisite
  above, not a scriptable pricing endpoint being missing (as of 2026, `POST /v1/appPriceSchedules`
  does exist for pricing itself — but it 404s/403s until the Agreement is accepted, and the
  Agreement has no API path).
- **Verified ✓ — App promo codes (whole-app free-download codes, Apps → \<App\> → Promo Codes).**
  ASC Help's *Request and manage promo codes* page (`developer.apple.com/help/app-store-connect/offer-promo-codes/request-and-manage-promo-codes`)
  documents only the web click-path ("In Apps, select the app you want to view. In the
  sidebar, click Promo Codes. The Promo Code page opens with Generate selected.") with no
  REST alternative mentioned; no `promoCodes`-shaped resource appears in the API topic index
  either. Don't confuse this with **Subscription Offer Codes**, which do have a documented API
  (`POST /v1/subscriptionOfferCodeCustomCodes` and siblings under *Subscription Offer Codes*)
  — the API gap is specific to whole-app promo codes, not offer codes in general.
