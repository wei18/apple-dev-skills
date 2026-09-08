#!/bin/sh
# C-hybrid: translate when `claude` is available; otherwise verify freshness.
# Usage: scripts/gen-readme-zh.sh <locale>   (e.g. zh-Hant)
set -eu
cd "$(git rev-parse --show-toplevel)"

LOCALE="${1:?usage: gen-readme-zh.sh <locale>, e.g. zh-Hant}"
case "$LOCALE" in
  zh-Hant) LANG_NAME="Traditional Chinese (zh-Hant)" ;;
  zh-Hans) LANG_NAME="Simplified Chinese (zh-Hans), using mainland-China terminology and simplified characters throughout" ;;
  ja) LANG_NAME="natural, idiomatic Japanese (ja) written in polite desu/masu style throughout, using terminology
and phrasing familiar to the Japanese iOS/Swift developer community (katakana or English mixed in the way
Japanese technical writing conventionally does), with full-width punctuation (、。（）「」・)" ;;
  *) echo "unsupported locale: $LOCALE (known: zh-Hant, zh-Hans, ja)" >&2; exit 1 ;;
esac
OUT="README.$LOCALE.md"

SHA="$(git hash-object README.md)"

if command -v claude >/dev/null 2>&1; then
  TMP="$(mktemp)"
  trap 'rm -f "$TMP"' EXIT
  claude -p "Translate the markdown read from stdin into $LANG_NAME.
Preserve structure, code fences, links, table layout, and all identifiers (kebab-case
skill/plugin names, install commands) verbatim. Translate only prose and table one-liners.
Output ONLY the translated markdown, nothing else." < README.md > "$TMP"
  if [ ! -s "$TMP" ]; then
    echo "claude produced empty output; leaving $OUT unchanged" >&2
    exit 1
  fi
  printf '\n<!-- src-sha: %s -->\n' "$SHA" >> "$TMP"
  mv "$TMP" "$OUT"
  git add "$OUT"
  echo "regenerated $OUT (src-sha $SHA)"
else
  EMB="$(grep -oE '<!-- src-sha: [0-9a-f]+ -->' "$OUT" 2>/dev/null | grep -oE '[0-9a-f]{7,}' || true)"
  if [ "$EMB" != "$SHA" ]; then
    echo "$OUT is stale; run 'mise run readme-zh' where 'claude' is on PATH" >&2
    exit 1
  fi
  echo "$OUT fresh (src-sha $SHA)"
fi
