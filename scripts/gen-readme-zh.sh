#!/bin/sh
# C-hybrid: translate when `claude` is available; otherwise verify freshness.
set -eu
cd "$(git rev-parse --show-toplevel)"
SHA="$(git hash-object README.md)"

if command -v claude >/dev/null 2>&1; then
  TMP="$(mktemp)"
  trap 'rm -f "$TMP"' EXIT
  claude -p "Translate the markdown read from stdin into Traditional Chinese (zh-Hant).
Preserve structure, code fences, links, table layout, and all identifiers (kebab-case
skill/plugin names, install commands) verbatim. Translate only prose and table one-liners.
Output ONLY the translated markdown, nothing else." < README.md > "$TMP"
  if [ ! -s "$TMP" ]; then
    echo "claude produced empty output; leaving README.zh-Hant.md unchanged" >&2
    exit 1
  fi
  printf '\n<!-- src-sha: %s -->\n' "$SHA" >> "$TMP"
  mv "$TMP" README.zh-Hant.md
  git add README.zh-Hant.md
  echo "regenerated README.zh-Hant.md (src-sha $SHA)"
else
  EMB="$(grep -oE '<!-- src-sha: [0-9a-f]+ -->' README.zh-Hant.md 2>/dev/null | grep -oE '[0-9a-f]{7,}' || true)"
  if [ "$EMB" != "$SHA" ]; then
    echo "README.zh-Hant.md is stale; run 'mise run readme-zh' where 'claude' is on PATH" >&2
    exit 1
  fi
  echo "README.zh-Hant.md fresh (src-sha $SHA)"
fi
