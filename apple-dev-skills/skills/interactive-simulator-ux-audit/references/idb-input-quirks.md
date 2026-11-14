# idb Input Quirks: Typing, Timing, Banners

Text entry and timing through `idb` fail in ways the accessibility tree does not show.
Confirm every typed value with a screenshot before you submit a form.

Observations below come from iOS 27.0 Simulator runtimes with idb 1.6.x (2026-10 to 2026-11).
Each is labelled with how often it was seen. Re-check on a newer idb before you rely on one.

## Keyboard layout comes first

A simulator whose language or region gives a non-Latin default keyboard (for example
Zhuyin) turns `idb ui text "abc"` into that keyboard's symbols. Set an English keyboard,
then relaunch the app:

```bash
xcrun simctl spawn <udid> defaults write .GlobalPreferences AppleKeyboards -array "en_US@sw=QWERTY;hw=Automatic"
```

`idb ui text` cannot type CJK characters at all, so use Latin-only test data. Seen in two
separate sessions.

## `idb ui text` returns before typing finishes

`idb ui text` returns while characters are still being sent. A `tap` or `key` sent right
after it interrupts the string and inserts the rest mid-text. The keyboard sliding in after
the field tap also eats the first characters. Recipe A (observed once, iOS 27.0, idb 1.6.10),
which follows from that mechanism:

1. Tap the field, then wait about 3 s for the keyboard to settle.
2. `idb ui text "<whole string>"`, then wait about 10 s.
3. Screenshot and read the field.
4. Submit with the keyboard's return / go key. Do not tap elsewhere first.

Recipe B (observed once, iOS 27.0, idb version not recorded; no mechanism found): on another
day a whole-string `idb ui text` kept only the first character. Typing one character per
`idb ui text` call, about 0.2 s apart, worked. The two observations disagree; start with
recipe A and switch to B when the screenshot shows dropped characters.

Related, each observed once:

- `idb ui key 42` (backspace) was unreliable. Tap to put the cursor at the end of the text,
  then tap the software keyboard's delete key (long-press the field once if the keyboard is
  hidden).
- After the keyboard is dismissed, the first `idb ui tap` is often ignored. Tap twice, or
  submit with the keyboard's go key.
- A web form can accept any value at its first step, so a "next" screen is not proof the
  input was right. Check the screenshot before the final submit.

## Timed gestures do not survive idb latency

Each `idb ui tap` took one to several seconds, so a gesture such as "tap N times within T seconds" resets
before it completes (seen twice). Do not try to drive one. Give Debug and simulator builds
a direct entry instead (a single tap or a launch argument), as described under
"Deterministic entry points for hard-to-reach states" in `host-driven-xcuitest-e2e`.

## Companion start-up and reconnect

- The first idb command against a simulator can wait more than 60 s while `idb_companion`
  starts (observed once). Do not treat that wait as a hang.
- After the simulator reboots, run `idb disconnect <udid>` then `idb connect <udid>` before
  driving again (observed once).

## Foreground notification banners are not in the tree

A banner shown while the app is in the foreground is not in the app's accessibility tree
(observed once). After `xcrun simctl push <udid> <bundle-id> payload.apns`, take a screenshot
about 1.5 s later and read the banner from the image.
