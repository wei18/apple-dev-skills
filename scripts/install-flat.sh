#!/bin/sh
# Path C (flat, no plugin) for the WHOLE catalog: `npx skills` scans a repo for
# SKILL.md folders and never reads marketplace.json, so `npx skills add
# wei18/apple-dev-skills` yields only the first-party skills and silently skips
# the aggregated externals. This script walks marketplace.json (the SSOT) and
# adds every plugin source, externals included, from their authors' repos.
# Usage: scripts/install-flat.sh [--dry-run] [extra `npx skills add` flags, e.g. -g]
set -eu
cd "$(git rev-parse --show-toplevel)"

DRY=0
if [ "${1:-}" = "--dry-run" ]; then DRY=1; shift; fi

SOURCES="$(python3 - <<'PY'
import json
printed_self = False
for p in json.load(open(".claude-plugin/marketplace.json"))["plugins"]:
    s = p["source"]
    if isinstance(s, str):  # local subdir plugin -> one add of this repo covers all
        if not printed_self:
            print("wei18/apple-dev-skills")
            printed_self = True
    elif s.get("source") == "github":
        print(s["repo"])
    elif s.get("source") == "git-subdir":
        print(s["url"])
PY
)"

for src in $SOURCES; do
  if [ "$DRY" -eq 1 ]; then
    echo "npx skills add $src --skill '*' -y $*"
  else
    npx -y skills add "$src" --skill '*' -y "$@"
  fi
done
